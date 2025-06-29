## 💾 指示書: 召喚獸バトルアプリ用 Claude 指示概要

### 🎮 概要

このプロジェクトは、召喚呪文を元に3D召喚獸を生成し、バトルさせるWebアプリケーションのMVPです。
以下の構成とシーケンスに基づいて、Claude Desktopを制御し、プロンプト入力からモデル生成までを自動化します。

---

## 🏠 システム構成

* **Frontend**

  * 技術: `HTML / CSS / TypeScript / Three.js`
  * 機能: ユーザーの召喚呪文入力、モデルの表示、バトルUI

* **Backend**

  * 技術: `Python`（FastAPI想定）
  * ライブラリ: `pyautogui` を使って `Claude Desktop` に指示を出す
  * ステートレス動作
  * モデル生成物は `assets/{summonId}` に格納される

---

## 🔁 シーケンス概要

### ① 召喚リクエスト（×2体）

```http
POST /summons
Content-Type: application/json

{
  "prompt": "出でよ神龍 そして願いを可ったたまえ"
}
```

* Claudeに `pyautogui` を使ってプロンプト入力を自動化。
* ClaudeがSTLモデルと、キャラステータス（JSON形式）を生成。
* 結果は `assets/{summonId}/model.stl` + `status.json` に保存。

---

### ② 生成完了チェック

```http
GET /summons/{summonId}
```

* レスポンス例：

```json
{
  "models": "assets/abc123/model.stl",
  "status": {
    "name": "神龍",
    "hp": 100,
    "specialMove": "願いを一つ可える",
    "description": "地球で数々の人間をよみがえらせた魔獣"
  }
}
```

---

### ③ バトル開始（3D表示、チャット入力）

* ユーザーが交互に攻撃プロンプトを送信
* Claudeがプロンプトを解釈し、**ダメージ判定・コメント出力**を返す

```http
POST /attack
Content-Type: application/json

{
  "prompt": "いてつくはどう",
  "me": {
    "name": "神龍",
    "hp": 100,
    "specialMove": "願いを一つ可える",
    "description": "地球で数々の人間をよみがえらせた魔獣"
  },
  "enemy": {
    "name": "シヴァ",
    "hp": 80,
    "specialMove": "ふぶき",
    "description": "氷属性の召喚獸"
  }
}
```

* Claudeのレスポンス例：

```json
{
  "result": {
    "hp": -100,
    "comment": "「いてつくはどう」攻撃！！、相手に氷攻撃を与えた。しかし相手は氷属性なので。今一つのようだ。"
  }
}
```

---

### ④ 勝者決定 & 決め台語

```http
POST /finish
Content-Type: application/json

{
  "me": {
    "name": "シヴァ",
    "hp": 80,
    "specialMove": "ふぶき",
    "description": "氷属性の召喚獸"
  }
}
```

* Claudeのレスポンス例：

```json
{
  "comment": "破れ散りなさい……！"
}
```

---

## 🔧 Claudeへの操作例（pyautogui）

```python
import pyautogui
import time
import json
import os
import pyperclip

# Configuration file to store Claude Desktop position
CONFIG_FILE = "claude_desktop_config.json"

def save_claude_position():
    """
    Save Claude Desktop position to config file
    """
    print("Please click on Claude Desktop's chat input area to save its position...")
    print("You have 5 seconds to click...")
    
    # Countdown
    for i in range(5, 0, -1):
        print(i)
        time.sleep(1)
    
    # Get current mouse position
    x, y = pyautogui.position()
    
    # Save to config file
    config = {"x": x, "y": y}
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)
    
    print(f"Claude Desktop position saved: ({x}, {y})")
    return x, y

def load_claude_position():
    """
    Load Claude Desktop position from config file
    """
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        return config["x"], config["y"]
    return None

def send_to_claude_desktop(message, x=None, y=None):
    """
    Send message to Claude Desktop chat input
    
    Args:
        message (str): Message to send
        x (int): X coordinate of chat input (optional)
        y (int): Y coordinate of chat input (optional)
    """
    # If coordinates provided, click there first
    if x is not None and y is not None:
        pyautogui.click(x, y)
        time.sleep(0.5)
    else:
        # Wait a bit for Claude Desktop to be active
        time.sleep(2)
    
    # Use clipboard for Japanese text to avoid IME issues
    pyperclip.copy(message)
    time.sleep(0.5)  # Wait for clipboard to be set
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.8)  # Wait for paste to complete
    
    # Press Enter to send
    pyautogui.press('enter')

if __name__ == "__main__":
    # Check if we have saved position
    position = load_claude_position()
    
    if position is None:
        # First time setup
        print("First time setup: Saving Claude Desktop position")
        x, y = save_claude_position()
        
        # Test with a sample message
        test_message = "Hello from Python automation!"
        print(f"Sending test message: {test_message}")
        send_to_claude_desktop(test_message, x, y)
        print("Test message sent!")
        
    else:
        # Use saved position and get user input
        x, y = position
        print(f"Using saved Claude Desktop position: ({x}, {y})")
        
        while True:
            message = input("Enter message to send to Claude Desktop (or 'quit' to exit): ")
            
            if message.lower() == 'quit':
                print("Goodbye!")
                break
            
            if message.strip():
                print(f"Sending: {message}")
                send_to_claude_desktop(message, x, y)
                print("Message sent!")
            else:
                print("Please enter a valid message.")

```
