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
    
    def send_to_claude_desktop(self, message: str, x: int = None, y: int = None, restore_mouse: bool = True):
        """Claude Desktopにメッセージを送信"""
        # 現在のマウス座標を記憶
        original_position = None
        if restore_mouse:
            original_position = pyautogui.position()
            print(f"マウス座標を記憶: {original_position}")
        
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
            
            # Enterキー押下後に元の座標に戻す
            if restore_mouse and original_position:
                time.sleep(0.2)  # 送信完了を待つ
                pyautogui.moveTo(original_position.x, original_position.y)
                print(f"マウス座標を元に戻しました: {original_position}")
            
        except Exception as e:
            # エラー時でも座標を復元
            if restore_mouse and original_position:
                pyautogui.moveTo(original_position.x, original_position.y)
                print(f"エラー時にマウス座標を復元: {original_position}")
            raise ClaudeDesktopError(f"Claude Desktopへのメッセージ送信に失敗しました: {e}")
    
    def execute_with_mouse_restore(self, action_func, wait_for_enter: bool = False):
        """
        マウス座標を記憶し、アクション実行後に元の位置に戻す
        
        Args:
            action_func: 実行する処理の関数
            wait_for_enter: Enterキー入力まで待機するかどうか
        """
        # 現在のマウス座標を記憶
        original_position = pyautogui.position()
        print(f"現在のマウス座標を記憶: {original_position}")
        
        try:
            # 指定されたアクションを実行
            action_func()
            
            if wait_for_enter:
                # Enterキーの入力を待機
                print("Enterキーを押すと元の座標に戻ります...")
                input()  # Enterキー待ち
            
        finally:
            # 元の座標に戻す
            pyautogui.moveTo(original_position.x, original_position.y)
            print(f"マウス座標を元に戻しました: {original_position}")