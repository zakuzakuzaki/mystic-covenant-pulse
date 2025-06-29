"""MCP結果処理コントローラー"""

import json
from typing import Optional, Dict, Any

from ..api.models import ClaudeResultData, BattleResult, CreatureGeneration, ModelGeneration, BattleAction
from .mcp_manager import mcp_manager


class MCPController:
    """MCP（Model Context Protocol）結果の処理を行うコントローラー"""
    
    async def process_mcp_result(self, result_data: str) -> Dict[str, Any]:
        """
        Claude DesktopからのMCP結果を処理する
        
        Args:
            result_data: Claude Desktopからの結果データ（JSON文字列）
            
        Returns:
            処理結果の情報
        """
        try:
            # 実行IDを生成
            execution_id = mcp_manager.generate_execution_id()
            
            # 結果をファイルに保存
            save_result = mcp_manager.save_result(execution_id, result_data)
            
            # 結果データを解析
            parsed_data = None
            if isinstance(result_data, str):
                try:
                    parsed_data = json.loads(result_data)
                except json.JSONDecodeError:
                    parsed_data = {"raw_result": result_data}
            else:
                parsed_data = result_data
            
            # 結果タイプに応じて追加処理
            result_type = save_result.get("result_type", "unknown")
            processing_result = {"execution_id": execution_id, "result_type": result_type}
            
            if result_type == "creature_data" and isinstance(parsed_data, dict):
                # 召喚獣データの場合、召喚獣として登録
                creature_result = mcp_manager.process_creature_result(execution_id, parsed_data)
                processing_result.update(creature_result)
                
            elif result_type == "model_generation" and isinstance(parsed_data, dict):
                # 3Dモデル生成結果の場合
                model_result = mcp_manager.process_model_result(execution_id, parsed_data)
                processing_result.update(model_result)
            
            # 構造化データの作成
            structured_data = self._parse_claude_result_data(parsed_data, result_type)
            
            # 処理結果を統合
            final_result = {
                **save_result,
                **processing_result,
                "processing_status": "completed",
                "parsed_data": structured_data.dict() if structured_data else None
            }
            
            print(f"MCP結果処理完了: {execution_id} ({result_type})")
            return final_result
            
        except Exception as e:
            error_msg = f"MCP結果処理エラー: {str(e)}"
            print(error_msg)
            return {
                "execution_id": execution_id if 'execution_id' in locals() else "unknown",
                "error": error_msg,
                "processing_status": "failed"
            }
    
    def get_current_mcp_result(self) -> Optional[Dict[str, Any]]:
        """
        現在キューされているMCP結果を取得する（取得後削除）
        
        Returns:
            現在の結果データまたはNone
        """
        try:
            return mcp_manager.get_current_result()
        except Exception as e:
            print(f"現在のMCP結果取得エラー: {e}")
            return None
    
    def has_mcp_result(self) -> bool:
        """
        キューにMCP結果があるかチェックする
        
        Returns:
            結果があるかどうか
        """
        try:
            return mcp_manager.has_result()
        except Exception as e:
            print(f"MCP結果存在確認エラー: {e}")
            return False
    
    def get_mcp_result(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        特定のMCP結果を取得する
        
        Args:
            execution_id: 実行ID
            
        Returns:
            結果データまたはNone
        """
        try:
            return mcp_manager.get_result(execution_id)
        except Exception as e:
            print(f"MCP結果取得エラー: {e}")
            return None
    
    def _parse_claude_result_data(self, data: Dict[str, Any], result_type: str) -> Optional[ClaudeResultData]:
        """
        Claude結果データを構造化データに変換する
        
        Args:
            data: パース済みデータ
            result_type: 結果タイプ
            
        Returns:
            構造化されたClaudeResultData
        """
        try:
            if result_type == "battle_result":
                return self._parse_battle_result(data)
            elif result_type == "creature_data":
                return self._parse_creature_generation(data)
            elif result_type == "model_generation":
                return self._parse_model_generation(data)
            else:
                # 生テキストまたは不明な形式
                return ClaudeResultData(
                    result_type=result_type,
                    raw_text=json.dumps(data) if isinstance(data, dict) else str(data)
                )
        except Exception as e:
            print(f"Claude結果データパース エラー: {e}")
            return ClaudeResultData(
                result_type="parse_error",
                raw_text=str(data)
            )
    
    def _parse_battle_result(self, data: Dict[str, Any]) -> ClaudeResultData:
        """バトル結果をパースする"""
        try:
            # 基本的なバトル結果フォーマット
            if "damage" in data and "comment" in data:
                battle_action = BattleAction(
                    action_type="attack",
                    damage=data.get("damage", 0),
                    comment=data.get("comment", "攻撃が発動！"),
                    critical=data.get("critical", False)
                )
                
                battle_result = BattleResult(
                    attacker_actions=[battle_action],
                    battle_comment=data.get("comment", "攻撃が発動！"),
                    hp_changes=data.get("hp_changes", {}),
                    turn_end=data.get("turn_end", True),
                    battle_end=data.get("battle_end", False),
                    winner=data.get("winner")
                )
                
                return ClaudeResultData(
                    result_type="battle_result",
                    battle_result=battle_result
                )
            
            # HP変更指示フォーマット
            elif "hp_changes" in data:
                battle_result = BattleResult(
                    hp_changes=data["hp_changes"],
                    battle_comment=data.get("comment", "HP変更が発生！"),
                    turn_end=data.get("turn_end", True),
                    battle_end=data.get("battle_end", False),
                    winner=data.get("winner")
                )
                
                return ClaudeResultData(
                    result_type="battle_result",
                    battle_result=battle_result
                )
            
            else:
                # 不明なバトル結果フォーマット
                return ClaudeResultData(
                    result_type="battle_result", 
                    raw_text=json.dumps(data)
                )
                
        except Exception as e:
            print(f"バトル結果パース エラー: {e}")
            return ClaudeResultData(
                result_type="battle_result",
                raw_text=json.dumps(data)
            )
    
    def _parse_creature_generation(self, data: Dict[str, Any]) -> ClaudeResultData:
        """召喚獣生成結果をパースする"""
        try:
            creature = CreatureGeneration(
                name=data.get("name", "不明な召喚獣"),
                hp=data.get("hp", 100),
                specialMove=data.get("specialMove", "通常攻撃"),
                description=data.get("description", ""),
                element=data.get("element"),
                rarity=data.get("rarity")
            )
            
            return ClaudeResultData(
                result_type="creature_generation",
                creature_generation=creature
            )
        except Exception as e:
            print(f"召喚獣生成結果パース エラー: {e}")
            return ClaudeResultData(
                result_type="creature_generation",
                raw_text=json.dumps(data)
            )
    
    def _parse_model_generation(self, data: Dict[str, Any]) -> ClaudeResultData:
        """3Dモデル生成結果をパースする"""
        try:
            model = ModelGeneration(
                model_path=data.get("model_path", ""),
                blender_script=data.get("blender_script"),
                generation_time=data.get("generation_time"),
                model_info=data.get("model_info", {})
            )
            
            return ClaudeResultData(
                result_type="model_generation",
                model_generation=model
            )
        except Exception as e:
            print(f"モデル生成結果パース エラー: {e}")
            return ClaudeResultData(
                result_type="model_generation",
                raw_text=json.dumps(data)
            )