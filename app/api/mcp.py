"""MCP APIエンドポイント"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from .models import ClaudeResult, ClaudeResultResponse, AttackResultData, AttackResultResponse
from ..services.mcp_manager import mcp_manager

router = APIRouter(tags=["MCP"])

@router.post("/mcp/results", response_model=ClaudeResultResponse, operation_id='save_mcp_result')
async def save_mcp_result(request: ClaudeResult):
    """MCPエージェントの結果を保存"""
    try:
        execution_id = mcp_manager.generate_execution_id()
        result = mcp_manager.save_result(execution_id, request.result)
        
        return ClaudeResultResponse(
            success=True,
            execution_id=result["execution_id"],
            result_type=result["result_type"],
            timestamp=result["timestamp"],
            message="MCP結果を正常に保存しました",
            processing_status="completed"
        )
    except Exception as e:
        return ClaudeResultResponse(
            success=False,
            execution_id="unknown",
            result_type="unknown",
            timestamp="",
            message=f"MCP結果の保存に失敗しました: {str(e)}",
            processing_status="error"
        )

@router.post("/mcp/results/attack", response_model=AttackResultResponse, operation_id='save_attack_result')
async def save_attack_result(request: AttackResultData):
    """攻撃結果を保存"""
    try:
        execution_id = mcp_manager.generate_execution_id()
        result = mcp_manager.save_result(execution_id, request.model_dump_json())
        
        return AttackResultResponse(
            success=True,
            execution_id=result["execution_id"],
            result_type="attack",
            timestamp=result["timestamp"],
            message="攻撃結果を正常に保存しました",
            processing_status="completed"
        )
    except Exception as e:
        return AttackResultResponse(
            success=False,
            execution_id="unknown",
            result_type="attack",
            timestamp="",
            message=f"攻撃結果の保存に失敗しました: {str(e)}",
            processing_status="error"
        )

@router.get("/mcp/result")
async def get_current_mcp_result():
    """現在キューされているMCP結果を取得（取得後削除）"""
    try:
        result = mcp_manager.get_current_result()
        if result is None:
            raise HTTPException(
                status_code=404,
                detail="キューされているMCP結果がありません"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"MCP結果の取得に失敗しました: {str(e)}"
        )

@router.get("/mcp/result/status")
async def get_mcp_result_status():
    """MCP結果キューの状態を確認"""
    try:
        has_result = mcp_manager.has_result()
        return {
            "has_result": has_result,
            "message": "結果がキューされています" if has_result else "キューは空です"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"MCP結果状態確認に失敗しました: {str(e)}"
        )

@router.get("/mcp/result/{execution_id}")
async def get_mcp_result_by_id(execution_id: str):
    """特定の実行IDのMCP結果を取得（取得後削除）"""
    try:
        result = mcp_manager.get_result(execution_id)
        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"実行ID {execution_id} の結果が見つかりません"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"MCP結果の取得に失敗しました: {str(e)}"
        ) 