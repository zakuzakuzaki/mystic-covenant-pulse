"""バトル処理コントローラー"""

import asyncio
from typing import Optional

from ..api.models import CreatureStats, AttackResultData, AttackParticipant
from .claude_desktop_client import ClaudeDesktopClient
from ..core.constants import Timing, PromptTemplates, Defaults


class BattleController:
    """バトル処理を行うコントローラー"""
    
    def __init__(self):
        self.desktop_client = ClaudeDesktopClient()
        
    async def process_attack(self, attack_prompt: str, me: CreatureStats, enemy: CreatureStats) -> Optional[AttackResultData]:
        """攻撃を処理する"""
        try:
            position = self.desktop_client.load_claude_position()
            if not position:
                print("Claude Desktopの座標が設定されていません")
                return None
            
            x, y = position
            
            # 攻撃処理のプロンプトを作成
            claude_prompt = PromptTemplates.ATTACK_TEMPLATE.format(
                attacker_name=me.name,
                attacker_hp=me.hp,
                attacker_special=me.specialMove,
                defender_name=enemy.name,
                defender_hp=enemy.hp,
                defender_special=enemy.specialMove,
                attack_prompt=attack_prompt
            )
            
            # Claude Desktopにメッセージを送信
            self.desktop_client.send_to_claude_desktop(claude_prompt, x, y)
            
            # レスポンス待機（実際の実装では、Claude Desktopからの出力を監視）
            await asyncio.sleep(Timing.ATTACK_RESPONSE_WAIT)
            
            # 仮の結果を返す（実際の実装では、Claude Desktopの出力を解析）
            return AttackResultData(
                comment=f"「{attack_prompt}」{Defaults.DEFAULT_ATTACK_COMMENT}",
                attacker=AttackParticipant(damage=0),  # 攻撃者はダメージなし
                defender=AttackParticipant(damage=-Defaults.DEFAULT_DAMAGE)  # 防御者にダメージ
            )
            
        except Exception as e:
            print(f"攻撃処理エラー: {e}")
            return None
    
