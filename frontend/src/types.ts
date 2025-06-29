// 型定義ファイル

export interface CreatureStats {
    name: string;
    hp: number;
    specialMove: string;
    description: string;
}

export interface SummonListItem {
    summonId: string;
    name: string;
    description: string;
    status: 'pending' | 'generating' | 'completed' | 'failed';
    models?: string;
}

export interface SummonListResponse {
    summons: SummonListItem[];
}

export interface SummonResponse {
    summonId: string;
    status: 'pending' | 'generating' | 'completed' | 'failed';
    message: string;
}

export interface SummonStatusResponse {
    summonId: string;
    status: 'pending' | 'generating' | 'completed' | 'failed';
    models?: string;
    stats?: CreatureStats;
}

export interface AttackResponse {
    result: AttackResultData;
}

export interface FinishResponse {
    comment: string;
}

export interface BattleAction {
    action_type: string;
    damage: number;
    heal: number;
    comment: string;
    critical: boolean;
}

export interface BattleResult {
    attacker_actions: BattleAction[];
    defender_actions: BattleAction[];
    hp_changes: Record<string, number>;
    status_effects: Record<string, string[]>;
    battle_comment: string;
    turn_end: boolean;
    battle_end: boolean;
    winner?: string;
}

export interface CreatureGeneration {
    name: string;
    hp: number;
    specialMove: string;
    description: string;
    element?: string;
    rarity?: string;
}

export interface ModelGeneration {
    model_path: string;
    blender_script?: string;
    generation_time?: number;
    model_info: Record<string, any>;
}

export interface ClaudeResultData {
    result_type: string;
    battle_result?: BattleResult;
    creature_generation?: CreatureGeneration;
    model_generation?: ModelGeneration;
    raw_text?: string;
}

export interface AttackResultData {
    comment: string;
    attacker: {
        damage: number;
    };
    defender: {
        damage: number;
    };
}

export interface MCPResult {
    execution_id: string;
    timestamp: string;
    result_type: string;
    data: any;
    parsed_data?: ClaudeResultData;
}

export interface MCPResultStatus {
    has_result: boolean;
    message: string;
}

export interface GameState {
    phase: 'summon' | 'battle' | 'result';
    creatures: {
        1: CreatureStats | null;
        2: CreatureStats | null;
    };
    currentTurn: 1 | 2;
    summonIds: {
        1: string | null;
        2: string | null;
    };
}

export interface ThreeJSViewer {
    loadSTL(path: string): Promise<void>;
    setModelColor(color: number): void;
    clearModel(): void;
}

export interface ViewerInstances {
    creature1?: ThreeJSViewer;
    creature2?: ThreeJSViewer;
}

// 前方宣言
export interface SummonBattleAPI {
    getSummonsList(): Promise<SummonListResponse | null>;
    createSummon(prompt: string): Promise<SummonResponse | null>;
    getSummonStatus(summonId: string): Promise<SummonStatusResponse | null>;
    attack(prompt: string, me: CreatureStats, enemy: CreatureStats): Promise<AttackResponse | null>;
    finishBattle(winner: CreatureStats): Promise<FinishResponse | null>;
    pollMCPResult(maxAttempts?: number, interval?: number): Promise<MCPResult | null>;
    sendMCPResult(resultData: any): Promise<any>;
    getMCPResultStatus(): Promise<MCPResultStatus | null>;
}

// グローバル変数の型定義
declare global {
    var viewers: ViewerInstances;
    var api: SummonBattleAPI;
}