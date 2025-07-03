"""バトル関連API"""

from fastapi import APIRouter, HTTPException, Query
from .models import AttackRequest, AttackResponse, FinishRequest, FinishResponse, AttackResultData
from ..services.claude_controller import ClaudeController
from ..services.file_manager import FileManager

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
    """勝負を決着する（勝者の決め台詞を返す）"""
    try:
        file_manager = FileManager()
        
        # summon_idからステータスを読み込み
        stats = file_manager.load_stats(request.summonId)
        if not stats:
            raise HTTPException(status_code=404, detail="召喚獣が見つかりません")
        
        # 勝利コメントを取得
        victory_comment = stats.get('victoryComment')
        if not victory_comment:
            creature_name = stats.get('name', '召喚獣')
            victory_comment = f"{creature_name}の勝利！"
        
        return FinishResponse(comment=victory_comment)
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"決着処理エラー: {e}")
        raise HTTPException(status_code=500, detail="決着処理中にエラーが発生しました")
