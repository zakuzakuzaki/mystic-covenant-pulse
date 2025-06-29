"""バトル関連API"""

from fastapi import APIRouter, HTTPException
from .models import AttackRequest, AttackResponse, AttackResult, FinishRequest, FinishResponse
from ..services.claude_controller import ClaudeController

router = APIRouter(prefix="/battle", tags=["battle"])

@router.post("/attack", response_model=AttackResponse)
async def attack(request: AttackRequest):
    """攻撃を実行する"""
    try:
        claude_controller = ClaudeController()
        result = await claude_controller.process_attack(
            request.prompt,
            request.me,
            request.enemy
        )
        
        if result:
            return AttackResponse(result=result)
        else:
            raise HTTPException(status_code=500, detail="攻撃処理に失敗しました")
            
    except Exception as e:
        print(f"攻撃処理エラー: {e}")
        raise HTTPException(status_code=500, detail="攻撃処理中にエラーが発生しました")

@router.post("/finish", response_model=FinishResponse)
async def finish_battle(request: FinishRequest):
    """勝負を決着する"""
    try:
        claude_controller = ClaudeController()
        comment = await claude_controller.generate_finish_comment(request.winner)
        
        if comment:
            return FinishResponse(comment=comment)
        else:
            raise HTTPException(status_code=500, detail="決着処理に失敗しました")
            
    except Exception as e:
        print(f"決着処理エラー: {e}")
        raise HTTPException(status_code=500, detail="決着処理中にエラーが発生しました")