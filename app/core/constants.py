"""アプリケーション定数"""

# 時間関連定数（秒）
class Timing:
    """タイミング関連の定数"""
    CLAUDE_CLICK_DELAY = 0.5
    CLAUDE_WAIT_DELAY = 2.0
    CLIPBOARD_DELAY = 0.5
    PASTE_DELAY = 0.8
    
    # 召喚関連
    SUMMON_MAX_WAIT_TIME = 300  # 5分
    SUMMON_CHECK_INTERVAL = 5   # 5秒
    
    # バトル関連
    ATTACK_RESPONSE_WAIT = 3
    FINISH_RESPONSE_WAIT = 2
    
    # MCP関連
    MCP_POLL_INTERVAL = 1000  # 1秒（ミリ秒）
    MCP_MAX_ATTEMPTS = 30


# プロンプトテンプレート
class PromptTemplates:
    """プロンプトテンプレートの定数"""
    
    SUMMON_TEMPLATE = """
召喚呪文「{prompt}」から召喚獣を生成してください。

以下の形式でSTLファイルとJSONステータスを作成してください：

1. STLファイル：
   - ファイル名: {repo_root}/assets/{summon_id}/model.stl
   - 召喚獣の3Dモデルを生成
   - 可能であれば、Hyper3Dを使用してモデルを作成してください。
   - Blenderでモデル作成後、以下のPythonスクリプトを実行してください：

```python
import bpy
import os

# エクスポート設定
file_path = "{repo_root}/assets/{summon_id}/model.stl"
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
     "description": "召喚獣の説明",
     "finishLine": "勝利時の決め台詞（この召喚獣が勝利した時の一言）"
   }}
   ```

召喚呪文を元に、創造的で魅力的な召喚獣を作成してください。
モデル保存後は必ずBlenderシーンから削除してクリーンな状態を保ってください。
"""

    ATTACK_TEMPLATE = """
バトル攻撃を処理してください。

攻撃者: {attacker_name} (HP: {attacker_hp}, 必殺技: {attacker_special})
防御者: {defender_name} (HP: {defender_hp}, 必殺技: {defender_special})
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
チャット欄には極力表示しないでください。
"""



# デフォルト値
class Defaults:
    """デフォルト値の定数"""
    DEFAULT_HP = 100
    DEFAULT_DAMAGE = 50
    DEFAULT_FINISH_COMMENT = "破れ散りなさい……！"
    DEFAULT_ATTACK_COMMENT = "攻撃が発動！効果的なダメージを与えた！"
    
    # API関連
    DEFAULT_TIMEOUT = 120000  # 2分（ミリ秒）
    MAX_TIMEOUT = 600000      # 10分（ミリ秒）