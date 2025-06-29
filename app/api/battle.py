"""バトル関連API"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any, List
from .models import AttackRequest, AttackResponse, AttackResult, FinishRequest, FinishResponse, ClaudeResult, ClaudeResultResponse, AttackResultData
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
            # 新しいAttackResultDataを古いAttackResult形式に変換
            if isinstance(result, AttackResultData):
                # 防御者のダメージをメインダメージとして使用（負の値）
                main_damage = result.defender.damage if result.defender.damage < 0 else -result.defender.damage
                converted_result = AttackResult(
                    damage=abs(main_damage),
                    comment=result.comment
                )
            else:
                # 既存のAttackResultの場合はそのまま使用
                converted_result = result
                
            return AttackResponse(result=converted_result)
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

@router.get("/mcp-result")
async def get_current_mcp_result() -> Dict[str, Any]:
    """
    現在キューされているMCP結果を取得する（取得後削除）
    
    Claude Desktopから受信された最新の結果データを返します。
    取得後、ファイルは自動的に削除されます（1個のみキュー）。
    """
    try:
        claude_controller = ClaudeController()
        result = claude_controller.get_current_mcp_result()
        
        if result:
            return result
        else:
            raise HTTPException(
                status_code=404, 
                detail="キューされているMCP結果がありません"
            )
    except HTTPException:
        raise
    except Exception as e:
        print(f"MCP結果取得エラー: {e}")
        raise HTTPException(status_code=500, detail=f"MCP結果取得エラー: {str(e)}")

@router.get("/mcp-result/status")
async def get_mcp_result_status() -> Dict[str, Any]:
    """
    MCP結果キューの状態を確認する
    
    現在キューに結果があるかどうかを確認します。
    """
    try:
        claude_controller = ClaudeController()
        has_result = claude_controller.has_mcp_result()
        
        return {
            "has_result": has_result,
            "message": "結果がキューされています" if has_result else "キューは空です"
        }
    except Exception as e:
        print(f"MCP結果状態確認エラー: {e}")
        raise HTTPException(status_code=500, detail=f"MCP結果状態確認エラー: {str(e)}")

@router.post("/results", response_model=ClaudeResultResponse)
async def push_result(item: ClaudeResult):
    """
    Claude Desktopのレスポンスを保存・処理する
    
    Claude Desktopから送信された結果データを受け取り、
    assets/mcp_resultsディレクトリに{実行UUID}.json形式で保存する。
    結果の種類に応じて追加の処理も実行する。
    """
    try:
        claude_controller = ClaudeController()
        # Claude Controllerを通してMCP結果を処理
        processing_result = await claude_controller.process_mcp_result(item.result)
        
        if processing_result.get("processing_status") == "completed":
            return ClaudeResultResponse(
                success=True,
                execution_id=processing_result["execution_id"],
                result_type=processing_result["result_type"],
                timestamp=processing_result["timestamp"],
                message="Claude Desktopの結果を正常に保存・処理しました",
                processing_status=processing_result["processing_status"]
            )
        else:
            return ClaudeResultResponse(
                success=False,
                execution_id=processing_result.get("execution_id", "unknown"),
                result_type=processing_result.get("result_type", "unknown"),
                timestamp="",
                message=processing_result.get("error", "処理に失敗しました"),
                processing_status=processing_result.get("processing_status", "failed")
            )
            
    except Exception as e:
        return ClaudeResultResponse(
            success=False,
            execution_id="unknown",
            result_type="unknown", 
            timestamp="",
            message=f"エラーが発生しました: {str(e)}",
            processing_status="error"
        )