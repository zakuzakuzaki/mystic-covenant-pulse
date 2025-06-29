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

class AttackResponse(BaseModel):
    """攻撃レスポンス"""
    result: 'AttackResultData' = Field(..., description="攻撃結果")

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

class BattleAction(BaseModel):
    """バトルアクション"""
    action_type: str = Field(..., description="アクションタイプ (attack, defend, special)")
    damage: int = Field(0, description="与えるダメージ")
    heal: int = Field(0, description="回復量")
    comment: str = Field(..., description="アクションの説明・台詞")
    critical: bool = Field(False, description="クリティカルヒットかどうか")
    
class BattleResult(BaseModel):
    """バトル結果"""
    attacker_actions: List[BattleAction] = Field(default=[], description="攻撃者のアクション")
    defender_actions: List[BattleAction] = Field(default=[], description="防御者のアクション") 
    hp_changes: Dict[str, int] = Field(default={}, description="HP変更 {creature_number: new_hp}")
    status_effects: Dict[str, List[str]] = Field(default={}, description="ステータス効果")
    battle_comment: str = Field(..., description="バトル全体の描写・コメント")
    turn_end: bool = Field(True, description="ターン終了かどうか")
    battle_end: bool = Field(False, description="バトル終了かどうか")
    winner: Optional[str] = Field(None, description="勝者（バトル終了時）")

class CreatureGeneration(BaseModel):
    """召喚獣生成結果"""
    name: str = Field(..., description="召喚獣名")
    hp: int = Field(..., ge=1, le=1000, description="HP")
    specialMove: str = Field(..., description="必殺技")
    description: str = Field(..., description="召喚獣の説明")
    element: Optional[str] = Field(None, description="属性")
    rarity: Optional[str] = Field(None, description="レアリティ")

class ModelGeneration(BaseModel):
    """3Dモデル生成結果"""
    model_path: str = Field(..., description="生成されたモデルファイルのパス") 
    blender_script: Optional[str] = Field(None, description="Blenderスクリプト")
    generation_time: Optional[float] = Field(None, description="生成時間（秒）")
    model_info: Dict[str, Any] = Field(default={}, description="モデル情報")

class ClaudeResultData(BaseModel):
    """Claude結果データの統合型"""
    result_type: str = Field(..., description="結果タイプ")
    battle_result: Optional[BattleResult] = Field(None, description="バトル結果")
    creature_generation: Optional[CreatureGeneration] = Field(None, description="召喚獣生成結果")
    model_generation: Optional[ModelGeneration] = Field(None, description="モデル生成結果")
    raw_text: Optional[str] = Field(None, description="生テキスト結果")

class ClaudeResult(BaseModel):
    """Claudeのレスポンス"""
    result: str = Field(..., description="Claude Desktopからの結果データ（JSON文字列 - 後方互換性のため）")

class ClaudeResultTyped(BaseModel):
    """型付きClaude結果"""
    data: ClaudeResultData = Field(..., description="構造化された結果データ")

class AttackParticipant(BaseModel):
    """攻撃参加者"""
    damage: int = Field(..., description="ダメージ量")

class AttackResultData(BaseModel):
    """攻撃結果データ"""
    comment: str = Field(..., description="攻撃を放ったときの実況コメント")
    attacker: AttackParticipant = Field(..., description="攻撃者情報")
    defender: AttackParticipant = Field(..., description="防御者情報")
    
    @property
    def damage(self) -> int:
        """後方互換性のためのダメージプロパティ"""
        return abs(self.defender.damage)

class AttackResultResponse(BaseModel):
    """攻撃結果保存のレスポンス"""
    success: bool = Field(..., description="処理成功フラグ")
    execution_id: str = Field(..., description="実行UUID")
    result_type: str = Field(..., description="結果タイプ")
    timestamp: str = Field(..., description="処理時刻")
    message: str = Field(..., description="処理メッセージ")
    processing_status: str = Field(..., description="処理ステータス")

class ClaudeResultResponse(BaseModel):
    """Claude結果保存のレスポンス"""
    success: bool = Field(..., description="処理成功フラグ")
    execution_id: str = Field(..., description="実行UUID")
    result_type: str = Field(..., description="結果タイプ")
    timestamp: str = Field(..., description="処理時刻")
    message: str = Field(..., description="処理メッセージ")
    processing_status: str = Field(..., description="処理ステータス")
    parsed_data: Optional[ClaudeResultData] = Field(None, description="パース済み結果データ")