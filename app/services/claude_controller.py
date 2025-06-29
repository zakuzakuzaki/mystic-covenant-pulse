"""Claude Desktop制御サービス（統合クラス）"""

from typing import Optional, Dict, Any

from ..api.models import CreatureStats, AttackResultData
from .summon_controller import SummonController
from .battle_controller import BattleController
from .mcp_controller import MCPController

class ClaudeController:
    """Claude Desktopを制御するサービス（分割されたコントローラーの統合）"""
    
    def __init__(self):
        self.summon_controller = SummonController()
        self.battle_controller = BattleController()
        self.mcp_controller = MCPController()
    
    # 召喚関連メソッド（SummonControllerに委譲）
    async def generate_summon(self, prompt: str, summon_id: str) -> bool:
        """召喚獣を生成する"""
        return await self.summon_controller.generate_summon(prompt, summon_id)
    
    # バトル関連メソッド（BattleControllerに委譲）
    async def process_attack(self, attack_prompt: str, me: CreatureStats, enemy: CreatureStats) -> Optional[AttackResultData]:
        """攻撃を処理する"""
        return await self.battle_controller.process_attack(attack_prompt, me, enemy)
    
    async def generate_finish_comment(self, winner: CreatureStats) -> bool:
        """勝利時のコメント生成をClaude Desktopに送信する"""
        return await self.battle_controller.generate_finish_comment(winner)
    
    # MCP関連メソッド（MCPControllerに委譲）
    async def process_mcp_result(self, result_data: str) -> Dict[str, Any]:
        """Claude DesktopからのMCP結果を処理する"""
        return await self.mcp_controller.process_mcp_result(result_data)
    
    def get_current_mcp_result(self) -> Optional[Dict[str, Any]]:
        """現在キューされているMCP結果を取得する"""
        return self.mcp_controller.get_current_mcp_result()
    
    def has_mcp_result(self) -> bool:
        """キューにMCP結果があるかチェックする"""
        return self.mcp_controller.has_mcp_result()
    
    def get_mcp_result(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """特定のMCP結果を取得する"""
        return self.mcp_controller.get_mcp_result(execution_id)