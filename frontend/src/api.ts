import { 
    SummonListResponse, 
    SummonResponse, 
    SummonStatusResponse, 
    AttackResponse, 
    FinishResponse, 
    CreatureStats, 
    MCPResult, 
    MCPResultStatus,
    SummonBattleAPI as ISummonBattleAPI
} from './types.js';
import { MCP_CONFIG } from './constants.js';

/**
 * API通信クラス
 */
export class SummonBattleAPI implements ISummonBattleAPI {
    private baseURL: string;

    constructor() {
        this.baseURL = '/api';
    }

    /**
     * 召喚獣リスト取得
     */
    async getSummonsList(): Promise<SummonListResponse | null> {
        try {
            const response = await fetch(`${this.baseURL}/summons`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json() as SummonListResponse;
        } catch (error) {
            console.error('召喚獣リスト取得エラー:', error);
            return null;
        }
    }

    /**
     * 召喚リクエスト
     */
    async createSummon(prompt: string): Promise<SummonResponse | null> {
        try {
            const response = await fetch(`${this.baseURL}/summons`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ prompt })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json() as SummonResponse;
        } catch (error) {
            console.error('召喚リクエストエラー:', error);
            return null;
        }
    }

    /**
     * 召喚状態確認
     */
    async getSummonStatus(summonId: string): Promise<SummonStatusResponse | null> {
        try {
            const response = await fetch(`${this.baseURL}/summons/${summonId}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json() as SummonStatusResponse;
        } catch (error) {
            console.error('召喚状態確認エラー:', error);
            return null;
        }
    }

    /**
     * 攻撃リクエスト
     */
    async attack(prompt: string, me: CreatureStats, enemy: CreatureStats): Promise<AttackResponse | null> {
        try {
            const response = await fetch(`${this.baseURL}/battle/attack`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ prompt, me, enemy })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json() as AttackResponse;
        } catch (error) {
            console.error('攻撃リクエストエラー:', error);
            return null;
        }
    }

    /**
     * 勝負決着
     */
    async finishBattle(winner: CreatureStats): Promise<FinishResponse | null> {
        try {
            const response = await fetch(`${this.baseURL}/battle/finish`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ winner })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json() as FinishResponse;
        } catch (error) {
            console.error('決着リクエストエラー:', error);
            return null;
        }
    }

    /**
     * MCP結果をポーリング
     */
    async pollMCPResult(maxAttempts: number = MCP_CONFIG.MAX_ATTEMPTS, interval: number = MCP_CONFIG.POLL_INTERVAL): Promise<MCPResult | null> {
        try {
            console.log(`MCPポーリング開始: 最大${maxAttempts}回試行、${interval}ms間隔`);
            
            for (let attempt = 0; attempt < maxAttempts; attempt++) {
                console.log(`MCPポーリング試行 ${attempt + 1}/${maxAttempts}`);
                
                // MCP結果の状態確認
                const statusResponse = await fetch(`${this.baseURL}/mcp/result/status`);
                if (statusResponse.ok) {
                    const status = await statusResponse.json() as MCPResultStatus;
                    console.log('MCP状態:', status);
                    
                    if (status.has_result) {
                        console.log('MCP結果が見つかりました。取得中...');
                        // 結果を取得
                        const resultResponse = await fetch(`${this.baseURL}/mcp/result`);
                        if (resultResponse.ok) {
                            const result = await resultResponse.json() as MCPResult;
                            console.log('MCP結果取得成功:', result);
                            return result;
                        }
                    }
                }
                
                // 最後の試行でない場合のみ待機
                if (attempt < maxAttempts - 1) {
                    await new Promise(resolve => setTimeout(resolve, interval));
                }
            }
            
            console.log('MCPポーリングタイムアウト');
            throw new Error(MCP_CONFIG.TIMEOUT_MESSAGE);
        } catch (error) {
            console.error('MCP結果ポーリングエラー:', error);
            return null;
        }
    }

    /**
     * MCP結果送信（攻撃プロンプト用）
     */
    async sendMCPResult(resultData: any): Promise<any> {
        try {
            const response = await fetch(`${this.baseURL}/mcp/results`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ result: resultData })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('MCP結果送信エラー:', error);
            return null;
        }
    }

    /**
     * MCP結果状態確認
     */
    async getMCPResultStatus(): Promise<MCPResultStatus | null> {
        try {
            const response = await fetch(`${this.baseURL}/mcp/result/status`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json() as MCPResultStatus;
        } catch (error) {
            console.error('MCP結果状態確認エラー:', error);
            return null;
        }
    }
}

// グローバルAPIインスタンス
export const api = new SummonBattleAPI();