"""APIモデル定義"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class SummonStatus(str, Enum):
    """召喚状態"""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"

class CreatureStats(BaseModel):
    """召喚獣ステータス"""
    name: str = Field(..., description="召喚獣名")
    hp: int = Field(..., ge=1, le=1000, description="HP")
    specialMove: str = Field(..., description="必殺技")
    description: str = Field(..., description="説明")

class SummonRequest(BaseModel):
    """召喚リクエスト"""
    prompt: str = Field(..., min_length=1, max_length=500, description="召喚呪文")

class SummonResponse(BaseModel):
    """召喚レスポンス"""
    summonId: str = Field(..., description="召喚ID")
    status: SummonStatus = Field(..., description="召喚状態")
    message: str = Field(..., description="メッセージ")

class SummonStatusResponse(BaseModel):
    """召喚状態レスポンス"""
    summonId: str = Field(..., description="召喚ID")
    status: SummonStatus = Field(..., description="召喚状態")
    models: Optional[str] = Field(None, description="モデルファイルパス")
    stats: Optional[CreatureStats] = Field(None, description="召喚獣ステータス")

class AttackRequest(BaseModel):
    """攻撃リクエスト"""
    prompt: str = Field(..., min_length=1, max_length=200, description="攻撃呪文")
    me: CreatureStats = Field(..., description="自分の召喚獣")
    enemy: CreatureStats = Field(..., description="敵の召喚獣")

class AttackResult(BaseModel):
    """攻撃結果"""
    damage: int = Field(..., description="ダメージ量")
    comment: str = Field(..., description="攻撃コメント")

class AttackResponse(BaseModel):
    """攻撃レスポンス"""
    result: AttackResult = Field(..., description="攻撃結果")

class FinishRequest(BaseModel):
    """勝負決着リクエスト"""
    winner: CreatureStats = Field(..., description="勝者の召喚獣")

class FinishResponse(BaseModel):
    """勝負決着レスポンス"""
    comment: str = Field(..., description="決め台詞")

class SummonListItem(BaseModel):
    """召喚獣リストアイテム"""
    summonId: str = Field(..., description="召喚ID")
    name: str = Field(..., description="召喚獣名")
    description: str = Field(..., description="説明")
    status: SummonStatus = Field(..., description="召喚状態")
    models: Optional[str] = Field(None, description="モデルファイルパス")

class SummonListResponse(BaseModel):
    """召喚獣リストレスポンス"""
    summons: List[SummonListItem] = Field(..., description="召喚獣リスト")