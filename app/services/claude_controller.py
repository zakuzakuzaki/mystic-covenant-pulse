"""Claude Desktop制御サービス"""

import asyncio
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any
import pyautogui
import pyperclip

from ..api.models import CreatureStats, AttackResult
from .file_manager import FileManager
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
    
    async def process_attack(self, attack_prompt: str, me: CreatureStats, enemy: CreatureStats) -> Optional[AttackResult]:
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

以下のJSON形式で攻撃結果を返してください：
```json
{{
  "damage": ダメージ数値,
  "comment": "攻撃の様子を描写したコメント"
}}
```

攻撃呪文の内容、双方の能力、相性などを考慮してダメージと臨場感のあるコメントを生成してください。
"""
            
            # Claude Desktopにメッセージを送信
            self._send_to_claude_desktop(claude_prompt, x, y)
            
            # レスポンス待機（実際の実装では、Claude Desktopからの出力を監視）
            await asyncio.sleep(3)
            
            # 仮の結果を返す（実際の実装では、Claude Desktopの出力を解析）
            return AttackResult(
                damage=50,  # 実際はClaude Desktopからの結果を解析
                comment=f"「{attack_prompt}」攻撃！効果的なダメージを与えた！"
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