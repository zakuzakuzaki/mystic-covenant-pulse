// フロントエンド定数定義

// MCP関連定数
export const MCP_CONFIG = {
    MAX_ATTEMPTS: 30,
    POLL_INTERVAL: 1000, // 1秒
    TIMEOUT_MESSAGE: 'MCP結果のポーリングがタイムアウトしました'
} as const;

// ゲーム関連定数
export const GAME_CONFIG = {
    DEFAULT_HP: 100,
    MIN_HP: 1,
    MAX_HP: 1000
} as const;

// UI関連定数
export const UI_CONFIG = {
    BATTLE_LOG_MAX_ENTRIES: 50,
    FADE_DURATION: 300
} as const;