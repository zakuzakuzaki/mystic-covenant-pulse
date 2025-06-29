"""召喚処理コントローラー"""

import asyncio
from typing import Optional

from .claude_desktop_client import ClaudeDesktopClient
from .file_manager import FileManager
from ..core.constants import Timing, PromptTemplates
from ..core.exceptions import SummonError, ClaudeDesktopError


class SummonController:
    """召喚獣生成処理を行うコントローラー"""
    
    def __init__(self):
        self.desktop_client = ClaudeDesktopClient()
        self.file_manager = FileManager()
        
    async def generate_summon(self, prompt: str, summon_id: str) -> bool:
        """召喚獣を生成する"""
        try:
            position = self.desktop_client.load_claude_position()
            if not position:
                raise SummonError("Claude Desktopの座標が設定されていません")
            
            x, y = position
            
            # 召喚獣生成のプロンプトを作成
            claude_prompt = PromptTemplates.SUMMON_TEMPLATE.format(
                prompt=prompt,
                summon_id=summon_id
            )
            
            # Claude Desktopにメッセージを送信
            self.desktop_client.send_to_claude_desktop(claude_prompt, x, y)
            
            # ファイル生成を待機・確認
            max_wait_time = Timing.SUMMON_MAX_WAIT_TIME
            check_interval = Timing.SUMMON_CHECK_INTERVAL
            elapsed_time = 0
            
            while elapsed_time < max_wait_time:
                await asyncio.sleep(check_interval)
                elapsed_time += check_interval
                
                # ファイルが生成されたかチェック
                if self.file_manager.check_summon_complete(summon_id):
                    print(f"召喚完了を確認: {summon_id}")
                    return True
                
                print(f"召喚生成中... ({elapsed_time}秒経過)")
            
            raise SummonError(f"召喚生成タイムアウト: {summon_id}")
            
        except ClaudeDesktopError:
            # Claude Desktop関連エラーは再発生
            raise
        except SummonError:
            # Summon関連エラーは再発生
            raise
        except Exception as e:
            raise SummonError(f"召喚生成中に予期しないエラーが発生しました: {e}")