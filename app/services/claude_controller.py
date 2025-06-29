"""Claude Desktop制御サービス"""

import asyncio
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any
import pyautogui
import pyperclip

from ..api.models import CreatureStats, AttackResult, ClaudeResultData, BattleResult, CreatureGeneration, ModelGeneration, BattleAction, AttackResultData
from .file_manager import FileManager
from .mcp_manager import mcp_manager
from ..core.config import settings

class ClaudeController:
    """Claude Desktopを制御するサービス"""
    
    def __init__(self):
        self.config_file = settings.CLAUDE_CONFIG_FILE
        self.config_file.parent.mkdir(exist_ok=True)
        self.file_manager = FileManager()
        
    def _load_claude_position(self) -> Optional[tuple]:
        """Claude Desktopの座標を読み込む"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            return config["x"], config["y"]
        return None
    
    def _send_to_claude_desktop(self, message: str, x: int = None, y: int = None):
        """Claude Desktopにメッセージを送信"""
        if x is not None and y is not None:
            pyautogui.click(x, y)
            time.sleep(0.5)
        else:
            time.sleep(2)
        
        # クリップボードを使用して日本語テキストを送信
        pyperclip.copy(message)
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.8)
        
        # Enterキーを押して送信
        pyautogui.press('enter')
    
    async def generate_summon(self, prompt: str, summon_id: str) -> bool:
        """召喚獣を生成する"""
        try:
            position = self._load_claude_position()
            if not position:
                print("Claude Desktopの座標が設定されていません")
                return False
            
            x, y = position
            
            # 召喚獣生成のプロンプトを作成
            claude_prompt = f"""
召喚呪文「{prompt}」から召喚獣を生成してください。

以下の形式でSTLファイルとJSONステータスを作成してください：

1. STLファイル：
   - ファイル名: assets/{summon_id}/model.stl
   - 召喚獣の3Dモデルを生成
   - Blenderでモデル作成後、以下のPythonスクリプトを実行してください：

```python
import bpy
import os

# エクスポート設定
file_path = "assets/{summon_id}/model.stl"
os.makedirs(os.path.dirname(file_path), exist_ok=True)

# 選択されたオブジェクトまたは全オブジェクトをSTL形式でエクスポート
bpy.ops.export_mesh.stl(filepath=file_path, use_selection=False)

# エクスポート後、生成したモデルをBlenderシーンから削除
# メッシュオブジェクトのみを削除（ライト、カメラは残す）
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        bpy.data.objects.remove(obj, do_unlink=True)

# 孤立したメッシュデータも削除
for mesh in bpy.data.meshes:
    if mesh.users == 0:
        bpy.data.meshes.remove(mesh)

print(f"STLファイルを保存し、モデルを削除しました: {{file_path}}")
```

2. JSONファイル：
   - ファイル名: assets/{summon_id}/status.json
   - 以下の形式で作成：
   ```json
   {{
     "name": "召喚獣名",
     "hp": 数値(1-1000),
     "specialMove": "必殺技名",
     "description": "召喚獣の説明"
   }}
   ```

召喚呪文を元に、創造的で魅力的な召喚獣を作成してください。
モデル保存後は必ずBlenderシーンから削除してクリーンな状態を保ってください。
"""
            
            # Claude Desktopにメッセージを送信
            self._send_to_claude_desktop(claude_prompt, x, y)
            
            # ファイル生成を待機・確認
            max_wait_time = 300  # 最大5分待機
            check_interval = 5   # 5秒間隔でチェック
            elapsed_time = 0
            
            while elapsed_time < max_wait_time:
                await asyncio.sleep(check_interval)
                elapsed_time += check_interval
                
                # ファイルが生成されたかチェック
                if self.file_manager.check_summon_complete(summon_id):
                    print(f"召喚完了を確認: {summon_id}")
                    return True
                
                print(f"召喚生成中... ({elapsed_time}秒経過)")
            
            print(f"召喚生成タイムアウト: {summon_id}")
            return False
            
        except Exception as e:
            print(f"召喚生成エラー: {e}")
            return False
    
    async def process_attack(self, attack_prompt: str, me: CreatureStats, enemy: CreatureStats) -> Optional[AttackResultData]:
        """攻撃を処理する"""
        try:
            position = self._load_claude_position()
            if not position:
                print("Claude Desktopの座標が設定されていません")
                return None
            
            x, y = position
            
            # 攻撃処理のプロンプトを作成
            claude_prompt = f"""
バトル攻撃を処理してください。

攻撃者: {me.name} (HP: {me.hp}, 必殺技: {me.specialMove})
防御者: {enemy.name} (HP: {enemy.hp}, 必殺技: {enemy.specialMove})
攻撃呪文: 「{attack_prompt}」

以下のJSON形式で攻撃結果を返してください:
```json
    {{
    "result_type": "attack",
    "comment": "攻撃を放ったときの実況コメント",
    "attacker": {{
        "damage": 攻撃者のダメージ数値（正の値は回復、負の値はダメージ）
    }},
    "defender": {{
        "damage": 防御者のダメージ数値（負の値はダメージ、正の値は回復）
    }}
}}
```

攻撃呪文の内容、双方の能力、相性などを考慮して臨場感のあるコメントとダメージを生成してください。
"""
            
            # Claude Desktopにメッセージを送信
            self._send_to_claude_desktop(claude_prompt, x, y)
            
            # レスポンス待機（実際の実装では、Claude Desktopからの出力を監視）
            await asyncio.sleep(3)
            
            # 仮の結果を返す（実際の実装では、Claude Desktopの出力を解析）
            return AttackResultData(
                comment=f"「{attack_prompt}」攻撃！効果的なダメージを与えた！",
                attacker={"damage": 0},  # 攻撃者はダメージなし
                defender={"damage": -50}  # 防御者に50ダメージ
            )
            
        except Exception as e:
            print(f"攻撃処理エラー: {e}")
            return None
    
    async def generate_finish_comment(self, winner: CreatureStats) -> Optional[str]:
        """勝利時のコメントを生成する"""
        try:
            position = self._load_claude_position()
            if not position:
                print("Claude Desktopの座標が設定されていません")
                return None
            
            x, y = position
            
            # 決着コメントのプロンプトを作成
            claude_prompt = f"""
勝者：{winner.name}
特徴：{winner.description}
必殺技：{winner.specialMove}

この召喚獣が勝利した時の決め台詞を生成してください。
キャラクターの特徴に合った、かっこいい一言を返してください。

決め台詞のみを返してください（余計な説明は不要）。
"""
            
            # Claude Desktopにメッセージを送信
            self._send_to_claude_desktop(claude_prompt, x, y)
            
            # レスポンス待機
            await asyncio.sleep(2)
            
            # 仮の結果を返す
            return "破れ散りなさい……！"
            
        except Exception as e:
            print(f"決着コメント生成エラー: {e}")
            return None
    
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
                name=data.get("name", "未知の召喚獣"),
                hp=data.get("hp", 100),
                specialMove=data.get("specialMove", "基本攻撃"),
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
        """モデル生成結果をパースする"""
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