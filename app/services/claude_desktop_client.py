"""Claude Desktop GUI自動化クライアント"""

import json
import time
from pathlib import Path
from typing import Optional
import pyautogui
import pyperclip

from ..core.config import settings
from ..core.constants import Timing
from ..core.exceptions import ClaudeDesktopError


class ClaudeDesktopClient:
    """Claude Desktopとの GUI自動化を行うクライアント"""
    
    def __init__(self):
        self.config_file = settings.CLAUDE_CONFIG_FILE
        self.config_file.parent.mkdir(exist_ok=True)
        
    def load_claude_position(self) -> Optional[tuple]:
        """Claude Desktopの座標を読み込む"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                return config["x"], config["y"]
            return None
        except (json.JSONDecodeError, KeyError) as e:
            raise ClaudeDesktopError(f"設定ファイルの読み込みに失敗しました: {e}")
        except Exception as e:
            raise ClaudeDesktopError(f"予期しないエラーが発生しました: {e}")
    
    def send_to_claude_desktop(self, message: str, x: int = None, y: int = None):
        """Claude Desktopにメッセージを送信"""
        try:
            if x is not None and y is not None:
                pyautogui.click(x, y)
                time.sleep(Timing.CLAUDE_CLICK_DELAY)
            else:
                time.sleep(Timing.CLAUDE_WAIT_DELAY)
            
            # クリップボードを使用して日本語テキストを送信
            pyperclip.copy(message)
            time.sleep(Timing.CLIPBOARD_DELAY)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(Timing.PASTE_DELAY)
            
            # Enterキーを押して送信
            pyautogui.press('enter')
            
        except Exception as e:
            raise ClaudeDesktopError(f"Claude Desktopへのメッセージ送信に失敗しました: {e}")