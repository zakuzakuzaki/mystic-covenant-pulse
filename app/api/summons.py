"""召喚関連API"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pathlib import Path
import uuid
import asyncio
import json
from typing import Dict, List

from .models import (
    SummonRequest, SummonResponse, SummonStatusResponse, SummonStatus, CreatureStats,
    SummonListResponse, SummonListItem
)
from ..services.claude_controller import ClaudeController
from ..services.file_manager import FileManager

router = APIRouter(prefix="/summons", tags=["summoning"])

@router.get("", response_model=SummonListResponse)
async def get_summons_list():
    """召喚獣リストを取得する"""
    file_manager = FileManager()
    summons = []
    
    # assetsディレクトリ内のすべての召喚獣をスキャン
    if file_manager.assets_dir.exists():
        for summon_dir in file_manager.assets_dir.iterdir():
            if summon_dir.is_dir():
                summon_id = summon_dir.name
                status_str = file_manager.load_summon_status(summon_id)
                
                try:
                    status = SummonStatus(status_str)
                except ValueError:
                    if status_str == "completed":
                        status = SummonStatus.COMPLETED
                    else:
                        status = SummonStatus.FAILED
                
                # 召喚獣の詳細情報を取得
                name = "不明な召喚獣"
                description = "説明なし"
                models_path = None
                
                if status == SummonStatus.COMPLETED:
                    stats_path = file_manager.get_stats_path(summon_id)
                    if stats_path.exists():
                        try:
                            with open(stats_path, 'r', encoding='utf-8') as f:
                                stats_data = json.load(f)
                                name = stats_data.get("name", name)
                                description = stats_data.get("description", description)
                                models_path = f"assets/{summon_id}/model.stl"
                        except Exception as e:
                            print(f"ステータス読み込みエラー {summon_id}: {e}")
                
                summons.append(SummonListItem(
                    summonId=summon_id,
                    name=name,
                    description=description,
                    status=status,
                    models=models_path
                ))
    
    # 作成日時順にソート（新しい順）
    summons.sort(key=lambda x: x.summonId, reverse=True)
    return SummonListResponse(summons=summons)

@router.post("", response_model=SummonResponse)
async def create_summon(
    request: SummonRequest, 
    background_tasks: BackgroundTasks
):
    """召喚獣を生成する"""
    summon_id = str(uuid.uuid4())
    file_manager = FileManager()
    
    # ファイルベースで状態を保存
    file_manager.save_summon_status(summon_id, SummonStatus.PENDING.value)
    
    # バックグラウンドタスクで召喚処理を実行
    background_tasks.add_task(
        process_summon, 
        summon_id, 
        request.prompt
    )
    
    return SummonResponse(
        summonId=summon_id,
        status=SummonStatus.PENDING,
        message="召喚処理を開始しました"
    )

@router.get("/{summon_id}", response_model=SummonStatusResponse)
async def get_summon_status(summon_id: str):
    """召喚状態を取得する"""
    file_manager = FileManager()
    
    # ファイルベースで召喚IDの存在をチェック
    if not file_manager.summon_exists(summon_id):
        raise HTTPException(status_code=404, detail="召喚IDが見つかりません")
    
    # ファイルベースで状態を取得
    status_str = file_manager.load_summon_status(summon_id)
    
    try:
        status = SummonStatus(status_str)
    except ValueError:
        # unknown など、enumに存在しない値の場合
        if status_str == "completed":
            status = SummonStatus.COMPLETED
        else:
            status = SummonStatus.FAILED
    
    # 完了状態の場合、ファイルとステータスを確認
    if status == SummonStatus.COMPLETED:
        model_path = file_manager.get_model_path(summon_id)
        stats_path = file_manager.get_stats_path(summon_id)
        
        if model_path.exists() and stats_path.exists():
            with open(stats_path, 'r', encoding='utf-8') as f:
                stats_data = json.load(f)
                stats = CreatureStats(**stats_data)
            
            return SummonStatusResponse(
                summonId=summon_id,
                status=status,
                models=f"assets/{summon_id}/model.stl",
                stats=stats
            )
    
    return SummonStatusResponse(
        summonId=summon_id,
        status=status
    )

async def process_summon(summon_id: str, prompt: str):
    """召喚処理を実行する（バックグラウンドタスク）"""
    file_manager = FileManager()
    
    try:
        # ファイルベースで状態を更新
        file_manager.save_summon_status(summon_id, SummonStatus.GENERATING.value)
        
        claude_controller = ClaudeController()
        
        # ディレクトリを作成
        file_manager.create_summon_directory(summon_id)
        
        # Claudeに召喚リクエストを送信
        result = await claude_controller.generate_summon(prompt, summon_id)
        
        if result:
            file_manager.save_summon_status(summon_id, SummonStatus.COMPLETED.value)
        else:
            file_manager.save_summon_status(summon_id, SummonStatus.FAILED.value)
            
    except Exception as e:
        print(f"召喚処理エラー: {e}")
        file_manager.save_summon_status(summon_id, SummonStatus.FAILED.value)