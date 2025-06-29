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
}

// グローバルAPIインスタンス
const api = new SummonBattleAPI();