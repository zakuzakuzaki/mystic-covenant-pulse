// ゲームメインクラス
class SummonBattleGame {
    constructor() {
        this.gameState = {
            phase: 'summon', // summon, battle, result
            creatures: {
                1: null,
                2: null
            },
            currentTurn: 1,
            summonIds: {
                1: null,
                2: null
            }
        };
        
        this.initializeElements();
        this.bindEvents();
        this.init3DViewers();
        this.loadSummonsList();
    }

    initializeElements() {
        // フェーズ要素
        this.summonPhase = document.getElementById('summonPhase');
        this.battlePhase = document.getElementById('battlePhase');
        this.resultPhase = document.getElementById('resultPhase');
        
        // 召喚要素
        this.summon1Select = document.getElementById('summon1Select');
        this.summon1Input = document.getElementById('summon1Input');
        this.summon1Btn = document.getElementById('summon1Btn');
        this.summon1Status = document.getElementById('summon1Status');
        
        this.summon2Select = document.getElementById('summon2Select');
        this.summon2Input = document.getElementById('summon2Input');
        this.summon2Btn = document.getElementById('summon2Btn');
        this.summon2Status = document.getElementById('summon2Status');
        
        this.startBattleBtn = document.getElementById('startBattleBtn');
        
        // バトル要素
        this.attackInput = document.getElementById('attackInput');
        this.attackBtn = document.getElementById('attackBtn');
        this.battleLog = document.getElementById('battleLog');
        this.currentTurnDisplay = document.getElementById('currentTurn');
        
        // 結果要素
        this.winnerDisplay = document.getElementById('winner');
        this.finishComment = document.getElementById('finishComment');
        this.restartBtn = document.getElementById('restartBtn');
        
        // ローディング
        this.loading = document.getElementById('loading');
        this.loadingMessage = document.getElementById('loadingMessage');
        
        // ゲーム状態表示
        this.gamePhase = document.getElementById('gamePhase');
    }

    bindEvents() {
        this.summon1Btn.addEventListener('click', () => this.startSummon(1));
        this.summon2Btn.addEventListener('click', () => this.startSummon(2));
        this.summon1Select.addEventListener('change', () => this.onSummonSelect(1));
        this.summon2Select.addEventListener('change', () => this.onSummonSelect(2));
        this.startBattleBtn.addEventListener('click', () => this.startBattle());
        this.attackBtn.addEventListener('click', () => this.performAttack());
        this.restartBtn.addEventListener('click', () => this.restart());
        
        // Enterキーでの送信
        this.attackInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.performAttack();
            }
        });
    }

    init3DViewers() {
        // バトルフェーズで3Dビューアーを初期化
        setTimeout(() => {
            if (!viewers.creature1) {
                viewers.creature1 = new ThreeJSViewer('creature1Viewer');
            }
            if (!viewers.creature2) {
                viewers.creature2 = new ThreeJSViewer('creature2Viewer');
            }
        }, 100);
    }

    showLoading(message) {
        this.loadingMessage.textContent = message;
        this.loading.classList.remove('hidden');
    }

    hideLoading() {
        this.loading.classList.add('hidden');
    }

    async loadSummonsList() {
        // 召喚獣リストを読み込む
        try {
            const result = await api.getSummonsList();
            if (result && result.summons) {
                this.populateSummonSelects(result.summons);
            }
        } catch (error) {
            console.error('召喚獣リスト読み込みエラー:', error);
        }
    }

    populateSummonSelects(summons) {
        // プルダウンリストに召喚獣を追加
        // 完了済みの召喚獣のみをフィルタリング
        const completedSummons = summons.filter(s => s.status === 'completed');
        
        // 両方のプルダウンをクリア
        this.summon1Select.innerHTML = '<option value="">既存の召喚獣を選択</option>';
        this.summon2Select.innerHTML = '<option value="">既存の召喚獣を選択</option>';
        
        // 完了済み召喚獣を追加
        completedSummons.forEach(summon => {
            const option1 = document.createElement('option');
            option1.value = summon.summonId;
            option1.textContent = `${summon.name} - ${summon.description}`;
            this.summon1Select.appendChild(option1);
            
            const option2 = document.createElement('option');
            option2.value = summon.summonId;
            option2.textContent = `${summon.name} - ${summon.description}`;
            this.summon2Select.appendChild(option2);
        });
    }

    async onSummonSelect(creatureNumber) {
        // 既存召喚獣を選択した時の処理
        const select = creatureNumber === 1 ? this.summon1Select : this.summon2Select;
        const status = creatureNumber === 1 ? this.summon1Status : this.summon2Status;
        const input = creatureNumber === 1 ? this.summon1Input : this.summon2Input;
        
        const summonId = select.value;
        
        if (summonId) {
            // 入力欄をクリア
            input.value = '';
            
            try {
                // 召喚獣詳細を取得
                const result = await api.getSummonStatus(summonId);
                
                if (result && result.stats) {
                    this.gameState.creatures[creatureNumber] = result.stats;
                    this.gameState.summonIds[creatureNumber] = summonId;
                    
                    status.innerHTML = `
                        <p style="color: green;">召喚獣を選択しました</p>
                        <p><strong>${result.stats.name}</strong></p>
                        <p>HP: ${result.stats.hp}</p>
                        <p>必殺技: ${result.stats.specialMove}</p>
                    `;
                    
                    this.checkBattleReady();
                } else {
                    status.innerHTML = '<p style="color: red;">召喚獣データの取得に失敗しました</p>';
                }
            } catch (error) {
                console.error('召喚獣選択エラー:', error);
                status.innerHTML = '<p style="color: red;">召喚獣選択エラー</p>';
            }
        } else {
            // 選択解除
            this.gameState.creatures[creatureNumber] = null;
            this.gameState.summonIds[creatureNumber] = null;
            status.innerHTML = '';
            this.checkBattleReady();
        }
    }

    async startSummon(creatureNumber) {
        const input = creatureNumber === 1 ? this.summon1Input : this.summon2Input;
        const btn = creatureNumber === 1 ? this.summon1Btn : this.summon2Btn;
        const status = creatureNumber === 1 ? this.summon1Status : this.summon2Status;
        const select = creatureNumber === 1 ? this.summon1Select : this.summon2Select;
        
        const prompt = input.value.trim();
        
        if (!prompt) {
            alert('召喚呪文を入力してください');
            return;
        }
        
        // プルダウン選択をクリア
        select.value = '';
        
        btn.disabled = true;
        status.innerHTML = '<p>召喚中...</p>';
        
        this.showLoading('召喚獣を生成中...');
        
        try {
            // 召喚リクエスト
            const result = await api.createSummon(prompt);
            
            if (result) {
                this.gameState.summonIds[creatureNumber] = result.summonId;
                status.innerHTML = `<p>召喚ID: ${result.summonId}</p><p>${result.message}</p>`;
                
                // 召喚完了を待機
                this.waitForSummonComplete(creatureNumber);
            } else {
                status.innerHTML = '<p style=\"color: red;\">召喚に失敗しました</p>';
                btn.disabled = false;
            }
        } catch (error) {
            console.error('召喚エラー:', error);
            status.innerHTML = '<p style=\"color: red;\">召喚エラーが発生しました</p>';
            btn.disabled = false;
        }
        
        this.hideLoading();
    }

    async waitForSummonComplete(creatureNumber) {
        const summonId = this.gameState.summonIds[creatureNumber];
        const status = creatureNumber === 1 ? this.summon1Status : this.summon2Status;
        
        const checkStatus = async () => {
            try {
                const result = await api.getSummonStatus(summonId);
                
                if (result) {
                    status.innerHTML = `<p>状態: ${result.status}</p>`;
                    
                    if (result.status === 'completed' && result.stats) {
                        this.gameState.creatures[creatureNumber] = result.stats;
                        status.innerHTML = `
                            <p style=\"color: green;\">召喚完了！</p>
                            <p><strong>${result.stats.name}</strong></p>
                            <p>HP: ${result.stats.hp}</p>
                            <p>必殺技: ${result.stats.specialMove}</p>
                        `;
                        this.checkBattleReady();
                        return;
                    } else if (result.status === 'failed') {
                        status.innerHTML = '<p style=\"color: red;\">召喚に失敗しました</p>';
                        const btn = creatureNumber === 1 ? this.summon1Btn : this.summon2Btn;
                        btn.disabled = false;
                        return;
                    }
                }
                
                // まだ完了していない場合は3秒後に再チェック
                setTimeout(checkStatus, 3000);
                
            } catch (error) {
                console.error('状態確認エラー:', error);
                status.innerHTML = '<p style=\"color: red;\">状態確認エラー</p>';
            }
        };
        
        checkStatus();
    }

    checkBattleReady() {
        if (this.gameState.creatures[1] && this.gameState.creatures[2]) {
            this.startBattleBtn.disabled = false;
            this.gamePhase.textContent = 'バトル準備完了';
        }
    }

    startBattle() {
        this.gameState.phase = 'battle';
        
        // フェーズ切り替え
        this.summonPhase.classList.add('hidden');
        this.battlePhase.classList.remove('hidden');
        this.gamePhase.textContent = 'バトル中';
        
        // 召喚獣情報の表示
        this.displayCreatureInfo(1);
        this.displayCreatureInfo(2);
        
        // 3Dモデルの読み込み
        this.load3DModels();
        
        this.updateTurnDisplay();
        this.addBattleLog('バトル開始！');
    }

    displayCreatureInfo(creatureNumber) {
        const creature = this.gameState.creatures[creatureNumber];
        const nameEl = document.getElementById(`creature${creatureNumber}Name`);
        const hpEl = document.getElementById(`creature${creatureNumber}HP`);
        const specialEl = document.getElementById(`creature${creatureNumber}Special`);
        
        nameEl.textContent = creature.name;
        specialEl.textContent = creature.specialMove;
        this.updateHP(creatureNumber, creature.hp, creature.hp);
    }

    async load3DModels() {
        this.showLoading('3Dモデルを読み込み中...');
        
        try {
            // 実際の召喚獣のSTLファイルパスを取得
            const summonId1 = this.gameState.summonIds[1];
            const summonId2 = this.gameState.summonIds[2];
            
            const modelPath1 = `/assets/${summonId1}/model.stl`;
            const modelPath2 = `/assets/${summonId2}/model.stl`;
            
            if (viewers.creature1 && summonId1) {
                await viewers.creature1.loadSTL(modelPath1);
                viewers.creature1.setModelColor(0xff6b35);
            }
            
            if (viewers.creature2 && summonId2) {
                await viewers.creature2.loadSTL(modelPath2);
                viewers.creature2.setModelColor(0x35a0ff);
            }
        } catch (error) {
            console.error('3Dモデル読み込みエラー:', error);
        }
        
        this.hideLoading();
    }

    updateHP(creatureNumber, currentHP, maxHP) {
        const hpEl = document.getElementById(`creature${creatureNumber}HP`);
        const percentage = (currentHP / maxHP) * 100;
        hpEl.style.width = `${Math.max(0, percentage)}%`;
        
        // HP色の変更
        if (percentage > 60) {
            hpEl.style.background = 'linear-gradient(90deg, #4CAF50, #81C784)';
        } else if (percentage > 30) {
            hpEl.style.background = 'linear-gradient(90deg, #FF9800, #FFB74D)';
        } else {
            hpEl.style.background = 'linear-gradient(90deg, #F44336, #EF5350)';
        }
    }

    updateTurnDisplay() {
        const creatureName = this.gameState.creatures[this.gameState.currentTurn].name;
        this.currentTurnDisplay.textContent = `${creatureName}のターン`;
    }

    async performAttack() {
        const attackPrompt = this.attackInput.value.trim();
        
        if (!attackPrompt) {
            alert('攻撃呪文を入力してください');
            return;
        }
        
        // 二重実行防止
        if (this.attackBtn.disabled) {
            return;
        }
        
        this.attackBtn.disabled = true;
        this.showLoading('Claude Desktopで攻撃処理中...');
        
        try {
            const attacker = this.gameState.creatures[this.gameState.currentTurn];
            const defender = this.gameState.creatures[this.gameState.currentTurn === 1 ? 2 : 1];
            
            this.addBattleLog(`${attacker.name}が「${attackPrompt}」で攻撃を開始！`);
            
            // まず /api/battle/attack を実行してClaude Desktopに攻撃プロンプトを送信
            console.log('攻撃API呼び出し開始...');
            const attackResult = await api.attack(attackPrompt, attacker, defender);
            
            if (attackResult && attackResult.result) {
                this.addBattleLog('Claude Desktopに攻撃プロンプトを送信しました');
                this.addBattleLog('Claude Desktopからの結果を待機中...');
                
                // MCPサーバから結果をポーリング
                const mcpResult = await api.pollMCPResult(30, 1000); // 30秒間、1秒間隔でポーリング
                
                if (mcpResult && (mcpResult.parsed_data || mcpResult.data)) {
                    console.log('MCP結果を使用して攻撃を処理します');
                    await this.processMCPAttackResult(mcpResult, attackPrompt);
                } else {
                    console.log('MCP結果が取得できないため、攻撃APIの仮結果を使用します');
                    this.addBattleLog('Claude Desktopからの応答がタイムアウトしました');
                    this.addBattleLog('攻撃APIの結果で続行します...');
                    
                    // 攻撃APIの結果をフォールバックとして使用
                    await this.processFallbackAttackResult(attackResult.result, attackPrompt);
                }
            } else {
                console.log('攻撃API呼び出しに失敗');
                this.addBattleLog('攻撃リクエストに失敗しました');
                throw new Error('攻撃API呼び出しに失敗しました');
            }
            
        } catch (error) {
            console.error('攻撃エラー:', error);
            this.addBattleLog('攻撃エラーが発生しました');
            
            // フォールバック処理: 攻撃APIを再実行
            const attacker = this.gameState.creatures[this.gameState.currentTurn];
            const defender = this.gameState.creatures[this.gameState.currentTurn === 1 ? 2 : 1];
            await this.performFallbackAttack(attackPrompt, attacker, defender);
        }
        
        this.attackInput.value = '';
        this.attackBtn.disabled = false;
        this.hideLoading();
    }

    async processMCPAttackResult(mcpResult, attackPrompt) {
        try {
            console.log('MCP結果を処理中:', mcpResult);
            
            // 構造化データがある場合は優先して使用
            let battleData = null;
            if (mcpResult.parsed_data) {
                console.log('構造化データを使用:', mcpResult.parsed_data);
                battleData = mcpResult.parsed_data;
            } else if (mcpResult.data) {
                console.log('生データを使用:', mcpResult.data);
                battleData = mcpResult.data;
            } else {
                console.log('データが見つかりません');
                throw new Error('MCP結果にデータが含まれていません');
            }
            console.log({battleData});
            // バトル結果の処理
            if (mcpResult.result_type === 'battle_result' && battleData.battle_result) {
                await this.processBattleResult(battleData.battle_result, attackPrompt);
            } else if (mcpResult.result_type === 'attack') {
                await this.processAttackResult(battleData, attackPrompt);
            } else if (mcpResult.result_type === 'creature_generation' && mcpResult.creature_generation) {
                const creature = battleData.creature_generation;
                this.addBattleLog(`召喚獣「${creature.name}」の生成結果を受信しましたが、バトル中のため無視します`);
            } else if (mcpResult.result_type === 'model_generation' && mcpResult.model_generation) {
                this.addBattleLog(`モデル生成結果「${mcpResult.model_generation.model_path}」を受信しましたが、バトル中のため無視します`);
            } else {
                // 従来形式または不明な形式の場合はフォールバック処理
                await this.processFallbackBattleData(battleData, attackPrompt);
            }
            
        } catch (error) {
            console.error('MCP結果処理エラー:', error);
            this.addBattleLog('結果処理でエラーが発生しました');
        }
    }
    
    async processBattleResult(battleResult, attackPrompt) {
        try {
            console.log('バトル結果を処理:', battleResult);
            
            // バトルコメントを表示
            this.addBattleLog(battleResult.battle_comment || `攻撃「${attackPrompt}」が発動！`);
            
            // HP変更を適用
            if (battleResult.hp_changes && Object.keys(battleResult.hp_changes).length > 0) {
                this.applyHPChanges(battleResult.hp_changes);
            } else if (battleResult.attacker_actions && battleResult.attacker_actions.length > 0) {
                // アクションベースのダメージ処理
                const action = battleResult.attacker_actions[0];
                if (action.damage > 0) {
                    const defenderNumber = this.gameState.currentTurn === 1 ? 2 : 1;
                    const defender = this.gameState.creatures[defenderNumber];
                    const newHP = Math.max(0, defender.hp - action.damage);
                    
                    this.gameState.creatures[defenderNumber].hp = newHP;
                    this.updateHP(defenderNumber, newHP, defender.hp + action.damage);
                    
                    if (action.comment) {
                        this.addBattleLog(action.comment);
                    }
                }
            }
            
            // バトル終了判定
            if (battleResult.battle_end && battleResult.winner) {
                const winnerNumber = battleResult.winner === this.gameState.creatures[1].name ? 1 : 2;
                this.endBattle(winnerNumber);
                return;
            }
            
            // 個別HP確認してバトル継続の場合のみターン交代
            const battleEnded = this.checkBattleEnd();
            
            // ターン終了の場合はターン交代（バトルが終了していない場合のみ）
            if (!battleEnded && (battleResult.turn_end !== false)) {
                this.gameState.currentTurn = this.gameState.currentTurn === 1 ? 2 : 1;
                this.updateTurnDisplay();
            }
            
        } catch (error) {
            console.error('バトル結果処理エラー:', error);
            this.addBattleLog('バトル結果処理でエラーが発生しました');
        }
    }
    
    async processAttackResult(attackData, attackPrompt) {
        try {
            console.log('攻撃結果を処理:', attackData);
            
            // コメントを表示
            this.addBattleLog(attackData.comment || `攻撃「${attackPrompt}」が発動！`);
            
            // 攻撃者のダメージ処理
            if (attackData.attacker && attackData.attacker.damage !== undefined) {
                const attackerNumber = this.gameState.currentTurn;
                const attacker = this.gameState.creatures[attackerNumber];
                const oldHP = attacker.hp;
                const newHP = Math.max(0, attacker.hp + attackData.attacker.damage);
                
                this.gameState.creatures[attackerNumber].hp = newHP;
                this.updateHP(attackerNumber, newHP, oldHP);
            }
            
            // 防御者のダメージ処理
            if (attackData.defender && attackData.defender.damage !== undefined) {
                const defenderNumber = this.gameState.currentTurn === 1 ? 2 : 1;
                const defender = this.gameState.creatures[defenderNumber];
                const oldHP = defender.hp;
                const newHP = Math.max(0, defender.hp + attackData.defender.damage);
                
                this.gameState.creatures[defenderNumber].hp = newHP;
                this.updateHP(defenderNumber, newHP, oldHP);
                
                // 防御者のHPが0以下になった場合、勝敗判定
                if (newHP <= 0) {
                    this.endBattle(this.gameState.currentTurn);
                    return;
                }
            }
            
            // 個別HP確認してバトル継続の場合のみターン交代
            const battleEnded = this.checkBattleEnd();
            
            // ターン交代（バトルが終了していない場合のみ）
            if (!battleEnded) {
                this.gameState.currentTurn = this.gameState.currentTurn === 1 ? 2 : 1;
                this.updateTurnDisplay();
            }
            
        } catch (error) {
            console.error('攻撃結果処理エラー:', error);
            this.addBattleLog('攻撃結果処理でエラーが発生しました');
        }
    }
    
    async processFallbackBattleData(mcpData, attackPrompt) {
        try {
            console.log('フォールバック処理でMCPデータを解析:', mcpData);
            
            let damage = 0;
            let comment = '';
            
            if (typeof mcpData === 'object') {
                damage = mcpData.damage || 0;
                comment = mcpData.comment || `攻撃「${attackPrompt}」が発動！`;
                
                // HP変更の指示がある場合
                if (mcpData.hp_changes) {
                    this.applyHPChanges(mcpData.hp_changes);
                    this.addBattleLog(comment);
                    
                    // 勝敗判定
                    const battleEnded = this.checkBattleEnd();
                    if (battleEnded) return;
                    
                    // ターン交代
                    this.gameState.currentTurn = this.gameState.currentTurn === 1 ? 2 : 1;
                    this.updateTurnDisplay();
                }
            } else if (typeof mcpData === 'string') {
                // 文字列の場合はコメントとして使用し、ランダムダメージを適用
                comment = mcpData;
                damage = Math.floor(Math.random() * 30) + 10;
            }
            
            // 通常のダメージ処理
            if (damage > 0) {
                const defenderNumber = this.gameState.currentTurn === 1 ? 2 : 1;
                const defender = this.gameState.creatures[defenderNumber];
                const newHP = Math.max(0, defender.hp - damage);
                
                this.gameState.creatures[defenderNumber].hp = newHP;
                this.updateHP(defenderNumber, newHP, defender.hp + damage);
                this.addBattleLog(comment);
                
                // 勝敗判定
                if (newHP <= 0) {
                    this.endBattle(this.gameState.currentTurn);
                    return;
                }
                
                // ターン交代
                this.gameState.currentTurn = this.gameState.currentTurn === 1 ? 2 : 1;
                this.updateTurnDisplay();
            }
            
        } catch (error) {
            console.error('フォールバック処理エラー:', error);
            this.addBattleLog('フォールバック処理でエラーが発生しました');
        }
    }
    
    async processFallbackAttackResult(attackResult, attackPrompt) {
        try {
            console.log('攻撃API結果をフォールバック処理:', attackResult);
            
            const damage = attackResult.damage || 0;
            const comment = attackResult.comment || `攻撃「${attackPrompt}」が発動！`;
            
            // ダメージ適用
            if (damage > 0) {
                const defenderNumber = this.gameState.currentTurn === 1 ? 2 : 1;
                const defender = this.gameState.creatures[defenderNumber];
                const oldHP = defender.hp;
                const newHP = Math.max(0, defender.hp - damage);
                
                this.gameState.creatures[defenderNumber].hp = newHP;
                this.updateHP(defenderNumber, newHP, oldHP);
                this.addBattleLog(comment);
                
                // 勝敗判定
                if (newHP <= 0) {
                    this.endBattle(this.gameState.currentTurn);
                    return;
                }
                
                // ターン交代
                this.gameState.currentTurn = this.gameState.currentTurn === 1 ? 2 : 1;
                this.updateTurnDisplay();
            } else {
                this.addBattleLog(comment);
                // ダメージがない場合でもターン交代
                this.gameState.currentTurn = this.gameState.currentTurn === 1 ? 2 : 1;
                this.updateTurnDisplay();
            }
            
        } catch (error) {
            console.error('攻撃結果フォールバック処理エラー:', error);
            this.addBattleLog('攻撃結果処理でエラーが発生しました');
        }
    }

    async performFallbackAttack(attackPrompt, attacker, defender) {
        try {
            const result = await api.attack(attackPrompt, attacker, defender);
            
            if (result && result.result) {
                const damage = result.result.damage;
                const comment = result.result.comment;
                
                // ダメージ適用
                const defenderNumber = this.gameState.currentTurn === 1 ? 2 : 1;
                const newHP = Math.max(0, defender.hp - damage);
                this.gameState.creatures[defenderNumber].hp = newHP;
                
                // UI更新
                this.updateHP(defenderNumber, newHP, defender.hp + damage);
                this.addBattleLog(comment);
                
                // 勝敗判定
                if (newHP <= 0) {
                    this.endBattle(this.gameState.currentTurn);
                    return;
                }
                
                // ターン交代
                this.gameState.currentTurn = this.gameState.currentTurn === 1 ? 2 : 1;
                this.updateTurnDisplay();
            }
        } catch (error) {
            console.error('フォールバック攻撃エラー:', error);
            this.addBattleLog('フォールバック攻撃も失敗しました');
        }
    }

    applyHPChanges(hpChanges) {
        // HP変更を適用（MCPから具体的なHP指示がある場合）
        for (const [creatureNumber, newHP] of Object.entries(hpChanges)) {
            const num = parseInt(creatureNumber);
            if (this.gameState.creatures[num]) {
                const oldHP = this.gameState.creatures[num].hp;
                this.gameState.creatures[num].hp = Math.max(0, newHP);
                this.updateHP(num, this.gameState.creatures[num].hp, oldHP);
            }
        }
    }

    checkBattleEnd() {
        // 両方の召喚獣のHP状態をチェック
        if (this.gameState.creatures[1].hp <= 0 && this.gameState.creatures[2].hp <= 0) {
            this.addBattleLog('引き分けです！');
            // 引き分け処理
            return true; // バトル終了
        } else if (this.gameState.creatures[1].hp <= 0) {
            this.endBattle(2);
            return true; // バトル終了
        } else if (this.gameState.creatures[2].hp <= 0) {
            this.endBattle(1);
            return true; // バトル終了
        }
        return false; // バトル継続
    }

    addBattleLog(message) {
        const logEntry = document.createElement('p');
        logEntry.textContent = message;
        this.battleLog.appendChild(logEntry);
        this.battleLog.scrollTop = this.battleLog.scrollHeight;
    }

    async endBattle(winnerNumber) {
        this.gameState.phase = 'result';
        
        const winner = this.gameState.creatures[winnerNumber];
        
        // 決め台詞を取得
        this.showLoading('決着処理中...');
        
        try {
            const finishResult = await api.finishBattle(winner);
            const comment = finishResult?.comment || '勝利！';
            
            // 結果画面に移行
            this.battlePhase.classList.add('hidden');
            this.resultPhase.classList.remove('hidden');
            this.gamePhase.textContent = 'バトル終了';
            
            this.winnerDisplay.innerHTML = `🏆 ${winner.name} の勝利！`;
            this.finishComment.textContent = `「${comment}」`;
            
        } catch (error) {
            console.error('決着処理エラー:', error);
            this.finishComment.textContent = '勝利！';
        }
        
        this.hideLoading();
    }

    restart() {
        // ゲーム状態をリセット
        this.gameState = {
            phase: 'summon',
            creatures: { 1: null, 2: null },
            currentTurn: 1,
            summonIds: { 1: null, 2: null }
        };
        
        // UI要素をリセット
        this.resultPhase.classList.add('hidden');
        this.battlePhase.classList.add('hidden');
        this.summonPhase.classList.remove('hidden');
        this.gamePhase.textContent = '召喚準備中';
        
        // 入力フィールドとボタンをリセット
        this.summon1Input.value = '';
        this.summon2Input.value = '';
        this.attackInput.value = '';
        this.battleLog.innerHTML = '';
        
        this.summon1Btn.disabled = false;
        this.summon2Btn.disabled = false;
        this.startBattleBtn.disabled = true;
        
        this.summon1Status.innerHTML = '';
        this.summon2Status.innerHTML = '';
        
        // 3Dビューアーをクリア
        if (viewers.creature1) {
            viewers.creature1.clearModel();
        }
        if (viewers.creature2) {
            viewers.creature2.clearModel();
        }
    }
}

// ゲーム開始
document.addEventListener('DOMContentLoaded', () => {
    const game = new SummonBattleGame();
});