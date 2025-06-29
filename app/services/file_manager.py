"""ファイル管理サービス"""

from pathlib import Path
import json
import time
from typing import Dict, Any
from ..core.config import settings

class FileManager:
    """ファイル管理を行うサービス"""
    
    def __init__(self):
        self.assets_dir = settings.ASSETS_DIR
        self.assets_dir.mkdir(parents=True, exist_ok=True)
    
    def create_summon_directory(self, summon_id: str) -> Path:
        """召喚獣用のディレクトリを作成"""
        summon_dir = self.assets_dir / summon_id
        summon_dir.mkdir(exist_ok=True)
        return summon_dir
    
    def get_model_path(self, summon_id: str) -> Path:
        """STLモデルファイルのパスを取得"""
        return self.assets_dir / summon_id / "model.stl"
    
    def get_stats_path(self, summon_id: str) -> Path:
        """ステータスJSONファイルのパスを取得"""
        return self.assets_dir / summon_id / "status.json"
    
    def save_stats(self, summon_id: str, stats: Dict[str, Any]) -> bool:
        """ステータスをJSONファイルに保存"""
        try:
            stats_path = self.get_stats_path(summon_id)
            with open(stats_path, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"ステータス保存エラー: {e}")
            return False
    
    def load_stats(self, summon_id: str) -> Dict[str, Any]:
        """ステータスをJSONファイルから読み込み"""
        try:
            stats_path = self.get_stats_path(summon_id)
            if stats_path.exists():
                with open(stats_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"ステータス読み込みエラー: {e}")
        return {}
    
    def check_summon_complete(self, summon_id: str) -> bool:
        """召喚が完了しているかチェック"""
        model_path = self.get_model_path(summon_id)
        stats_path = self.get_stats_path(summon_id)
        return model_path.exists() and stats_path.exists()
    
    def save_summon_status(self, summon_id: str, status: str) -> bool:
        """召喚状態をファイルに保存"""
        try:
            status_file = self.assets_dir / summon_id / "summon_status.json"
            status_file.parent.mkdir(parents=True, exist_ok=True)
            
            status_data = {
                "summon_id": summon_id,
                "status": status,
                "created_at": time.time()
            }
            
            with open(status_file, 'w', encoding='utf-8') as f:
                json.dump(status_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"状態保存エラー: {e}")
            return False
    
    def load_summon_status(self, summon_id: str) -> str:
        """召喚状態をファイルから読み込み"""
        try:
            status_file = self.assets_dir / summon_id / "summon_status.json"
            if status_file.exists():
                with open(status_file, 'r', encoding='utf-8') as f:
                    status_data = json.load(f)
                return status_data.get("status", "unknown")
            
            # ファイルが存在しない場合、完了チェック
            if self.check_summon_complete(summon_id):
                return "completed"
            else:
                return "unknown"
        except Exception as e:
            print(f"状態読み込みエラー: {e}")
            return "unknown"
    
    def summon_exists(self, summon_id: str) -> bool:
        """召喚IDが存在するかチェック"""
        summon_dir = self.assets_dir / summon_id
        status_file = summon_dir / "summon_status.json"
        
        # ステータスファイルが存在するか、完成したファイルが存在するかチェック
        return status_file.exists() or self.check_summon_complete(summon_id)
    
    def cleanup_summon(self, summon_id: str) -> bool:
        """召喚獣ファイルを削除"""
        try:
            summon_dir = self.assets_dir / summon_id
            if summon_dir.exists():
                for file in summon_dir.iterdir():
                    file.unlink()
                summon_dir.rmdir()
            return True
        except Exception as e:
            print(f"クリーンアップエラー: {e}")
            return False