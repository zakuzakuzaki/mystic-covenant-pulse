"""MCP結果管理サービス"""

import json
import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..core.config import settings

logger = logging.getLogger(__name__)

class MCPResultManager:
    """Claude DesktopからのMCP結果を管理するクラス"""
    
    def __init__(self):
        self.mcp_results_dir = settings.ASSETS_DIR / "mcp_results"
        self.mcp_results_dir.mkdir(exist_ok=True)
        logger.info(f"MCP結果ディレクトリを初期化: {self.mcp_results_dir}")
    
    def generate_execution_id(self) -> str:
        """実行UUIDを生成"""
        return str(uuid.uuid4())
    
    def save_result(self, execution_id: str, result_data: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Claude Desktopの結果をファイルに保存（1個のみキュー）
        
        新しい結果を保存する前に、既存の結果ファイルを全て削除します。
        
        Args:
            execution_id: 実行UUID
            result_data: 結果データ（JSON文字列またはdict）
            
        Returns:
            保存された結果の情報
        """
        try:
            # 既存のMCP結果ファイルを全て削除（1個のみキューのため）
            self._clear_all_results()
            
            # 結果データを辞書形式に変換
            if isinstance(result_data, str):
                try:
                    parsed_data = json.loads(result_data)
                except json.JSONDecodeError:
                    # JSONでない場合は文字列として保存
                    parsed_data = {"raw_result": result_data}
            else:
                parsed_data = result_data
            print(parsed_data)
            # メタデータを追加
            result_with_metadata = {
                "execution_id": execution_id,
                "timestamp": datetime.now().isoformat(),
                "result_type": self._detect_result_type(parsed_data),
                "data": parsed_data
            }
            
            # ファイルに保存
            result_file = self.mcp_results_dir / f"{execution_id}.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result_with_metadata, f, ensure_ascii=False, indent=2)
            
            logger.info(f"MCP結果を保存しました: {result_file}")
            
            return {
                "execution_id": execution_id,
                "file_path": str(result_file),
                "timestamp": result_with_metadata["timestamp"],
                "result_type": result_with_metadata["result_type"],
                "status": "saved"
            }
            
        except Exception as e:
            logger.error(f"MCP結果保存エラー: {e}")
            raise Exception(f"結果の保存に失敗しました: {str(e)}")
    
    def _clear_all_results(self):
        """既存のMCP結果ファイルを全て削除"""
        try:
            for result_file in self.mcp_results_dir.glob("*.json"):
                result_file.unlink()
                logger.info(f"既存のMCP結果を削除しました: {result_file}")
        except Exception as e:
            logger.warning(f"既存ファイル削除エラー: {e}")
    
    def _detect_result_type(self, data: Dict[str, Any]) -> str:
        """結果データの種類を判定"""
        # まずparsed_dataからresult_typeを取得を試行
        if isinstance(data, dict) and "result_type" in data:
            return data["result_type"]
        
        # result_typeが存在しない場合は従来の判定処理
        if isinstance(data, dict):
            # 決着コメントか判定
            if "comment" in data and len(data) == 1:
                return "finish_comment"
            
            # 召喚獣データか判定
            if all(key in data for key in ["name", "hp", "specialMove", "description"]):
                return "creature_data"
            
            # 攻撃結果か判定
            if all(key in data for key in ["attacker", "defender", "comment"]):
                return "attack"
            
            # 3Dモデル生成結果か判定
            if "model_path" in data or "stl_data" in data:
                return "model_generation"
            
            # Blenderスクリプトか判定
            if "blender_script" in data or "python_code" in data:
                return "blender_script"
            
            # より精密な攻撃結果判定
            if "comment" in data and ("attacker" in data or "defender" in data):
                return "attack"
            
            return "general_json"
    
    def get_result(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """実行IDから結果を取得（取得後ファイル削除）"""
        try:
            result_file = self.mcp_results_dir / f"{execution_id}.json"
            
            if not result_file.exists():
                return None
            
            with open(result_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # ファイルを削除（キューから取り出し）
            result_file.unlink()
            logger.info(f"MCP結果を取得し削除しました: {result_file}")
            
            return data
                
        except Exception as e:
            logger.error(f"MCP結果取得エラー: {e}")
            return None
    
    def get_current_result(self) -> Optional[Dict[str, Any]]:
        """現在キューされている結果を取得（取得後削除）"""
        try:
            # mcp_resultsディレクトリ内の最初のJSONファイルを取得
            result_files = list(self.mcp_results_dir.glob("*.json"))
            
            if not result_files:
                return None
            
            # 最初（唯一）のファイルを取得
            result_file = result_files[0]
            
            with open(result_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # ファイルを削除（キューから取り出し）
            result_file.unlink()
            logger.info(f"現在のMCP結果を取得し削除しました: {result_file}")
            
            return data
                
        except Exception as e:
            logger.error(f"現在のMCP結果取得エラー: {e}")
            return None
    
    def has_result(self) -> bool:
        """キューに結果があるかチェック"""
        try:
            result_files = list(self.mcp_results_dir.glob("*.json"))
            return len(result_files) > 0
        except Exception as e:
            logger.error(f"結果存在確認エラー: {e}")
            return False
    
    def list_results(self, limit: int = 50, result_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """結果リストを取得"""
        try:
            results = []
            
            # 全JSONファイルを取得
            for result_file in self.mcp_results_dir.glob("*.json"):
                try:
                    with open(result_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # フィルタリング
                    if result_type and data.get("result_type") != result_type:
                        continue
                    
                    # サマリー情報のみ抽出
                    summary = {
                        "execution_id": data.get("execution_id"),
                        "timestamp": data.get("timestamp"),
                        "result_type": data.get("result_type"),
                        "file_path": str(result_file)
                    }
                    
                    results.append(summary)
                    
                except Exception as e:
                    logger.warning(f"結果ファイル読み込みエラー {result_file}: {e}")
            
            # タイムスタンプでソート（新しい順）
            results.sort(key=lambda x: x["timestamp"], reverse=True)
            
            return results[:limit]
            
        except Exception as e:
            logger.error(f"結果リスト取得エラー: {e}")
            return []
    
    def delete_result(self, execution_id: str) -> bool:
        """結果を削除"""
        try:
            result_file = self.mcp_results_dir / f"{execution_id}.json"
            
            if result_file.exists():
                result_file.unlink()
                logger.info(f"MCP結果を削除しました: {result_file}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"MCP結果削除エラー: {e}")
            return False
    
    def process_creature_result(self, execution_id: str, creature_data: Dict[str, Any]) -> Dict[str, Any]:
        """召喚獣生成結果を処理"""
        try:
            # 基本的な検証
            required_fields = ["name", "hp", "specialMove", "description"]
            if not all(field in creature_data for field in required_fields):
                raise ValueError(f"必須フィールドが不足しています: {required_fields}")
            
            # 召喚獣ディレクトリを作成
            creature_id = str(uuid.uuid4())
            creature_dir = settings.ASSETS_DIR / creature_id
            creature_dir.mkdir(exist_ok=True)
            
            # 召喚獣ステータスファイルを保存
            status_file = creature_dir / "status.json"
            with open(status_file, 'w', encoding='utf-8') as f:
                json.dump(creature_data, f, ensure_ascii=False, indent=2)
            
            # 召喚状態ファイルを保存
            summon_status = {
                "status": "completed",
                "creature_id": creature_id,
                "execution_id": execution_id,
                "created_at": datetime.now().isoformat(),
                "source": "mcp_result"
            }
            
            summon_status_file = creature_dir / "summon_status.json"
            with open(summon_status_file, 'w', encoding='utf-8') as f:
                json.dump(summon_status, f, ensure_ascii=False, indent=2)
            
            logger.info(f"召喚獣データを処理しました: {creature_id}")
            
            return {
                "creature_id": creature_id,
                "execution_id": execution_id,
                "status": "processed",
                "creature_dir": str(creature_dir)
            }
            
        except Exception as e:
            logger.error(f"召喚獣結果処理エラー: {e}")
            raise Exception(f"召喚獣データの処理に失敗しました: {str(e)}")
    
    def process_model_result(self, execution_id: str, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """3Dモデル生成結果を処理"""
        try:
            # モデルファイルの保存先を決定
            model_dir = self.mcp_results_dir / f"models_{execution_id}"
            model_dir.mkdir(exist_ok=True)
            
            # STLデータがある場合は保存
            if "stl_data" in model_data:
                stl_file = model_dir / "model.stl"
                with open(stl_file, 'w', encoding='utf-8') as f:
                    f.write(model_data["stl_data"])
                
                model_data["stl_file_path"] = str(stl_file)
            
            # Blenderスクリプトがある場合は保存
            if "blender_script" in model_data:
                script_file = model_dir / "generate_model.py"
                with open(script_file, 'w', encoding='utf-8') as f:
                    f.write(model_data["blender_script"])
                
                model_data["script_file_path"] = str(script_file)
            
            logger.info(f"3Dモデルデータを処理しました: {model_dir}")
            
            return {
                "execution_id": execution_id,
                "model_dir": str(model_dir),
                "status": "processed"
            }
            
        except Exception as e:
            logger.error(f"3Dモデル結果処理エラー: {e}")
            raise Exception(f"3Dモデルデータの処理に失敗しました: {str(e)}")

# グローバルインスタンス
mcp_manager = MCPResultManager()