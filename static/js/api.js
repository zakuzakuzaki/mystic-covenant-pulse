// API通信クラス
class SummonBattleAPI {
    constructor() {
        this.baseURL = '/api';
    }

    // 召喚獣リスト取得
    async getSummonsList() {
        try {
            const response = await fetch(`${this.baseURL}/summons`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('召喚獣リスト取得エラー:', error);
            return null;
        }
    }

    // 召喚リクエスト
    async createSummon(prompt) {
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
            
            return await response.json();
        } catch (error) {
            console.error('召喚リクエストエラー:', error);
            return null;
        }
    }

    // 召喚状態確認
    async getSummonStatus(summonId) {
        try {
            const response = await fetch(`${this.baseURL}/summons/${summonId}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('召喚状態確認エラー:', error);
            return null;
        }
    }

    // 攻撃リクエスト
    async attack(prompt, me, enemy) {
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
            
            return await response.json();
        } catch (error) {
            console.error('攻撃リクエストエラー:', error);
            return null;
        }
    }

    // 勝負決着
    async finishBattle(winner) {
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
            
            return await response.json();
        } catch (error) {
            console.error('決着リクエストエラー:', error);
            return null;
        }
    }

    // MCP結果をポーリング
    async pollMCPResult(maxAttempts = 30, interval = 1000) {
        try {
            console.log(`MCPポーリング開始: 最大${maxAttempts}回試行、${interval}ms間隔`);
            
            for (let attempt = 0; attempt < maxAttempts; attempt++) {
                console.log(`MCPポーリング試行 ${attempt + 1}/${maxAttempts}`);
                
                // MCP結果の状態確認
                const statusResponse = await fetch(`${this.baseURL}/mcp/result/status`);
                if (statusResponse.ok) {
                    const status = await statusResponse.json();
                    console.log('MCP状態:', status);
                    
                    if (status.has_result) {
                        console.log('MCP結果が見つかりました。取得中...');
                        // 結果を取得
                        const resultResponse = await fetch(`${this.baseURL}/mcp/result`);
                        if (resultResponse.ok) {
                            const result = await resultResponse.json();
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
            throw new Error('MCP結果のポーリングがタイムアウトしました');
        } catch (error) {
            console.error('MCP結果ポーリングエラー:', error);
            return null;
        }
    }

    // MCP結果送信（攻撃プロンプト用）
    async sendMCPResult(resultData) {
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

    // MCP結果状態確認
    async getMCPResultStatus() {
        try {
            const response = await fetch(`${this.baseURL}/mcp/result/status`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('MCP結果状態確認エラー:', error);
            return null;
        }
    }
}

// グローバルAPIインスタンス
const api = new SummonBattleAPI();