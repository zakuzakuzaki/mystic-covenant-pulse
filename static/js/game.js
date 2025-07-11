import { api } from './api.js';
/**
 * ゲームメインクラス
 */
export class SummonBattleGame {
    constructor() {
        this.gameState = {
            phase: 'summon',
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
        this.updateAttackButtonState();
        this.init3DViewers();
        this.loadSummonsList();
    }
    async showWinnerModel(winner) {
        try {
            // 勝者の3Dビューアーを初期化
            const winnerViewer = new globalThis.ThreeJSViewer('winnerViewer');
            // 勝者のモデルファイルパスを取得
            const winnerCreatureId = this.gameState.summonIds[1] && this.gameState.creatures[1]?.name === winner.name
                ? this.gameState.summonIds[1]
                : this.gameState.summonIds[2];
            if (winnerCreatureId) {
                const modelPath = `/assets/${winnerCreatureId}/model.stl`;
                console.log(`勝者のモデルを読み込み中: ${modelPath}`);
                await winnerViewer.loadSTL(modelPath);
                // 勝者の色を金色に
                winnerViewer.setModelColor(0xffd700);
                // 勝利の舞を開始
                this.startVictoryDance(winnerViewer);
                console.log('勝者のモデル表示完了');
            }
        }
        catch (error) {
            console.error('勝者モデル表示エラー:', error);
        }
    }
    startVictoryDance(viewer) {
        if (!viewer.model)
            return;
        const originalY = viewer.model.position.y;
        const startTime = Date.now();
        const dance = () => {
            if (!viewer.model)
                return;
            const elapsed = (Date.now() - startTime) / 1000;
            // 上下に揺れる動き
            const bounce = Math.sin(elapsed * 4) * 2;
            viewer.model.position.y = originalY + bounce;
            // 回転する動き
            viewer.model.rotation.y = elapsed * 2;
            // キラキラ効果（スケーリング）
            const sparkle = 1 + Math.sin(elapsed * 6) * 0.1;
            viewer.model.scale.setScalar(viewer.model.scale.x * sparkle / (viewer.model.scale.x || 1));
            // 5秒間踊り続ける
            if (elapsed < 5) {
                requestAnimationFrame(dance);
            }
            else {
                // 元の位置と回転に戻す
                viewer.model.position.y = originalY;
                viewer.model.rotation.y = 0;
            }
        };
        dance();
    }
    initializeElements() {
        // フェーズ要素
        this.summonPhase = this.getElementById('summonPhase');
        this.battlePhase = this.getElementById('battlePhase');
        this.resultPhase = this.getElementById('resultPhase');
        // 召喚要素
        this.summon1Select = this.getElementById('summon1Select');
        this.summon1Input = this.getElementById('summon1Input');
        this.summon1Btn = this.getElementById('summon1Btn');
        this.summon1Status = this.getElementById('summon1Status');
        this.summon2Select = this.getElementById('summon2Select');
        this.summon2Input = this.getElementById('summon2Input');
        this.summon2Btn = this.getElementById('summon2Btn');
        this.summon2Status = this.getElementById('summon2Status');
        this.startBattleBtn = this.getElementById('startBattleBtn');
        // バトル要素
        this.attackInput = this.getElementById('attackInput');
        this.attackBtn = this.getElementById('attackBtn');
        this.battleLog = this.getElementById('battleLog');
        this.currentTurnDisplay = this.getElementById('currentTurn');
        // 結果要素
        this.winnerDisplay = this.getElementById('winner');
        this.winnerViewer = this.getElementById('winnerViewer');
        this.finishComment = this.getElementById('finishComment');
        this.restartBtn = this.getElementById('restartBtn');
        // ローディング
        this.loading = this.getElementById('loading');
        this.loadingMessage = this.getElementById('loadingMessage');
        // ゲーム状態表示
        this.gamePhase = this.getElementById('gamePhase');
    }
    getElementById(id) {
        const element = document.getElementById(id);
        if (!element) {
            throw new Error(`Element with id '${id}' not found`);
        }
        return element;
    }
    bindEvents() {
        this.summon1Btn.addEventListener('click', () => this.startSummon(1));
        this.summon2Btn.addEventListener('click', () => this.startSummon(2));
        this.summon1Select.addEventListener('change', () => this.onSummonSelect(1));
        this.summon2Select.addEventListener('change', () => this.onSummonSelect(2));
        this.startBattleBtn.addEventListener('click', () => this.startBattle());
        this.attackBtn.addEventListener('click', () => this.performAttack());
        this.attackInput.addEventListener('input', () => this.updateAttackButtonState());
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
            if (!globalThis.viewers.creature1) {
                globalThis.viewers.creature1 = new globalThis.ThreeJSViewer('creature1Viewer');
            }
            if (!globalThis.viewers.creature2) {
                globalThis.viewers.creature2 = new globalThis.ThreeJSViewer('creature2Viewer');
            }
        }, 100);
    }
    showLoading(message) {
        // ローディング表示を削除し、代わりにUI要素をdisabledにする
        this.attackInput.disabled = true;
        this.attackBtn.disabled = true;
        this.attackBtn.textContent = message;
    }
    hideLoading() {
        // UI要素を有効化
        this.attackInput.disabled = false;
        this.attackBtn.disabled = false;
        this.attackBtn.textContent = '攻撃';
    }
    showPollingProgress(attempt, maxAttempts) {
        const pollingProgress = document.getElementById('pollingProgress');
        const progressFill = document.getElementById('progressFill');
        const pollingCount = document.getElementById('pollingCount');
        pollingProgress.classList.remove('hidden');
        const percentage = (attempt / maxAttempts) * 100;
        progressFill.style.width = `${percentage}%`;
        pollingCount.textContent = attempt.toString();
    }
    hidePollingProgress() {
        const pollingProgress = document.getElementById('pollingProgress');
        pollingProgress.classList.add('hidden');
    }
    updateAttackButtonState() {
        const hasText = this.attackInput.value.trim().length > 0;
        this.attackBtn.disabled = !hasText;
    }
    async loadSummonsList() {
        try {
            const result = await api.getSummonsList();
            if (result && result.summons) {
                this.populateSummonSelects(result.summons);
            }
        }
        catch (error) {
            console.error('召喚獣リスト読み込みエラー:', error);
        }
    }
    populateSummonSelects(summons) {
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
        const select = creatureNumber === 1 ? this.summon1Select : this.summon2Select;
        const status = creatureNumber === 1 ? this.summon1Status : this.summon2Status;
        const input = creatureNumber === 1 ? this.summon1Input : this.summon2Input;
        const summonId = select.value;
        if (summonId) {
            input.value = '';
            try {
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
                }
                else {
                    status.innerHTML = '<p style="color: red;">召喚獣データの取得に失敗しました</p>';
                }
            }
            catch (error) {
                console.error('召喚獣選択エラー:', error);
                status.innerHTML = '<p style="color: red;">召喚獣選択エラー</p>';
            }
        }
        else {
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
        select.value = '';
        btn.disabled = true;
        status.innerHTML = '<p>召喚中...</p>';
        this.showLoading('召喚獣を生成中...');
        try {
            const result = await api.createSummon(prompt);
            if (result) {
                this.gameState.summonIds[creatureNumber] = result.summonId;
                status.innerHTML = `<p>召喚ID: ${result.summonId}</p><p>${result.message}</p>`;
                this.waitForSummonComplete(creatureNumber);
            }
            else {
                status.innerHTML = '<p style="color: red;">召喚に失敗しました</p>';
                btn.disabled = false;
            }
        }
        catch (error) {
            console.error('召喚エラー:', error);
            status.innerHTML = '<p style="color: red;">召喚エラーが発生しました</p>';
            btn.disabled = false;
        }
        this.hideLoading();
    }
    async waitForSummonComplete(creatureNumber) {
        const summonId = this.gameState.summonIds[creatureNumber];
        if (!summonId)
            return;
        const status = creatureNumber === 1 ? this.summon1Status : this.summon2Status;
        const checkStatus = async () => {
            try {
                const result = await api.getSummonStatus(summonId);
                if (result) {
                    status.innerHTML = `<p>状態: ${result.status}</p>`;
                    if (result.status === 'completed' && result.stats) {
                        this.gameState.creatures[creatureNumber] = result.stats;
                        status.innerHTML = `
                            <p style="color: green;">召喚完了！</p>
                            <p><strong>${result.stats.name}</strong></p>
                            <p>HP: ${result.stats.hp}</p>
                            <p>必殺技: ${result.stats.specialMove}</p>
                        `;
                        this.checkBattleReady();
                        return;
                    }
                    else if (result.status === 'failed') {
                        status.innerHTML = '<p style="color: red;">召喚に失敗しました</p>';
                        const btn = creatureNumber === 1 ? this.summon1Btn : this.summon2Btn;
                        btn.disabled = false;
                        return;
                    }
                }
                setTimeout(checkStatus, 3000);
            }
            catch (error) {
                console.error('状態確認エラー:', error);
                status.innerHTML = '<p style="color: red;">状態確認エラー</p>';
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
        this.summonPhase.classList.add('hidden');
        this.battlePhase.classList.remove('hidden');
        this.gamePhase.textContent = 'バトル中';
        this.displayCreatureInfo(1);
        this.displayCreatureInfo(2);
        this.load3DModels();
        this.updateTurnDisplay();
        this.addBattleLog('バトル開始！');
    }
    displayCreatureInfo(creatureNumber) {
        const creature = this.gameState.creatures[creatureNumber];
        if (!creature)
            return;
        const nameEl = this.getElementById(`creature${creatureNumber}Name`);
        const specialEl = this.getElementById(`creature${creatureNumber}Special`);
        nameEl.textContent = creature.name;
        specialEl.textContent = creature.specialMove;
        this.updateHP(creatureNumber, creature.hp, creature.hp);
    }
    async load3DModels() {
        this.showLoading('3Dモデルを読み込み中...');
        try {
            const summonId1 = this.gameState.summonIds[1];
            const summonId2 = this.gameState.summonIds[2];
            if (summonId1) {
                const modelPath1 = `/assets/${summonId1}/model.stl`;
                if (globalThis.viewers.creature1) {
                    await globalThis.viewers.creature1.loadSTL(modelPath1);
                    globalThis.viewers.creature1.setModelColor(0xff6b35);
                }
            }
            if (summonId2) {
                const modelPath2 = `/assets/${summonId2}/model.stl`;
                if (globalThis.viewers.creature2) {
                    await globalThis.viewers.creature2.loadSTL(modelPath2);
                    globalThis.viewers.creature2.setModelColor(0x35a0ff);
                }
            }
        }
        catch (error) {
            console.error('3Dモデル読み込みエラー:', error);
        }
        this.hideLoading();
    }
    updateHP(creatureNumber, currentHP, maxHP) {
        const hpEl = this.getElementById(`creature${creatureNumber}HP`);
        const hpTextEl = this.getElementById(`creature${creatureNumber}HPText`);
        const percentage = (currentHP / maxHP) * 100;
        hpEl.style.width = `${Math.max(0, percentage)}%`;
        // HP数値を更新
        hpTextEl.textContent = `${currentHP}/${maxHP}`;
        if (percentage > 60) {
            hpEl.style.background = 'linear-gradient(90deg, #4CAF50, #81C784)';
        }
        else if (percentage > 30) {
            hpEl.style.background = 'linear-gradient(90deg, #FF9800, #FFB74D)';
        }
        else {
            hpEl.style.background = 'linear-gradient(90deg, #F44336, #EF5350)';
        }
    }
    updateTurnDisplay() {
        const creature = this.gameState.creatures[this.gameState.currentTurn];
        if (creature) {
            this.currentTurnDisplay.textContent = `${creature.name}のターン`;
        }
    }
    async performAttack() {
        const attackPrompt = this.attackInput.value.trim();
        if (!attackPrompt) {
            alert('攻撃呪文を入力してください');
            return;
        }
        if (this.attackBtn.disabled) {
            return;
        }
        this.attackBtn.disabled = true;
        this.showLoading('攻撃処理を開始しています...');
        try {
            const attacker = this.gameState.creatures[this.gameState.currentTurn];
            const defender = this.gameState.creatures[this.gameState.currentTurn === 1 ? 2 : 1];
            if (!attacker || !defender)
                return;
            this.addBattleLog(`${attacker.name}が「${attackPrompt}」で攻撃を開始！`);
            this.showLoading('Claude Desktopに攻撃プロンプトを送信中...');
            const attackResult = await api.attack(attackPrompt, attacker, defender);
            if (attackResult && attackResult.result) {
                this.addBattleLog('Claude Desktopに攻撃プロンプトを送信しました');
                this.addBattleLog('Claude Desktopからの結果を待機中...');
                this.showLoading('Claude Desktopからの攻撃結果を待機中...');
                const mcpResult = await api.pollMCPResult(30, 1000, (attempt, maxAttempts) => {
                    this.showPollingProgress(attempt, maxAttempts);
                });
                if (mcpResult && (mcpResult.parsed_data || mcpResult.data)) {
                    console.log('MCP結果を使用して攻撃を処理します');
                    this.showLoading('攻撃結果を処理中...');
                    await this.processMCPAttackResult(mcpResult, attackPrompt);
                }
                else {
                    console.log('MCP結果が取得できないため、攻撃APIの仮結果を使用します');
                    this.addBattleLog('Claude Desktopからの応答がタイムアウトしました');
                    this.addBattleLog('攻撃APIの結果で続行します...');
                    this.showLoading('フォールバック攻撃処理中...');
                    await this.processFallbackAttackResult(attackResult.result, attackPrompt);
                }
            }
            else {
                console.log('攻撃API呼び出しに失敗');
                this.addBattleLog('攻撃リクエストに失敗しました');
                throw new Error('攻撃API呼び出しに失敗しました');
            }
        }
        catch (error) {
            console.error('攻撃エラー:', error);
            this.addBattleLog('攻撃エラーが発生しました');
            const attacker = this.gameState.creatures[this.gameState.currentTurn];
            const defender = this.gameState.creatures[this.gameState.currentTurn === 1 ? 2 : 1];
            if (attacker && defender) {
                await this.performFallbackAttack(attackPrompt, attacker, defender);
            }
        }
        this.attackInput.value = '';
        this.attackBtn.disabled = false;
        this.hideLoading();
        this.hidePollingProgress();
    }
    async processMCPAttackResult(mcpResult, attackPrompt) {
        try {
            console.log('MCP結果を処理中:', mcpResult);
            let battleData = null;
            if (mcpResult.parsed_data) {
                console.log('構造化データを使用:', mcpResult.parsed_data);
                battleData = mcpResult.parsed_data;
            }
            else if (mcpResult.data) {
                console.log('生データを使用:', mcpResult.data);
                battleData = mcpResult.data;
            }
            else {
                console.log('データが見つかりません');
                throw new Error('MCP結果にデータが含まれていません');
            }
            console.log({ battleData });
            if (mcpResult.result_type === 'battle_result' && battleData.battle_result) {
                await this.processBattleResult(battleData.battle_result, attackPrompt);
            }
            else if (mcpResult.result_type === 'attack') {
                await this.processAttackResult(battleData, attackPrompt);
            }
            else if (mcpResult.result_type === 'creature_generation' && battleData.creature_generation) {
                const creature = battleData.creature_generation;
                this.addBattleLog(`召喚獣「${creature.name}」の生成結果を受信しましたが、バトル中のため無視します`);
            }
            else if (mcpResult.result_type === 'model_generation' && battleData.model_generation) {
                this.addBattleLog(`モデル生成結果「${battleData.model_generation.model_path}」を受信しましたが、バトル中のため無視します`);
            }
            else {
                await this.processFallbackBattleData(battleData, attackPrompt);
            }
        }
        catch (error) {
            console.error('MCP結果処理エラー:', error);
            this.addBattleLog('結果処理でエラーが発生しました');
        }
    }
    async processBattleResult(battleResult, attackPrompt) {
        try {
            console.log('バトル結果を処理:', battleResult);
            this.addBattleLog(battleResult.battle_comment || `攻撃「${attackPrompt}」が発動！`);
            if (battleResult.hp_changes && Object.keys(battleResult.hp_changes).length > 0) {
                this.applyHPChanges(battleResult.hp_changes);
            }
            else if (battleResult.attacker_actions && battleResult.attacker_actions.length > 0) {
                const action = battleResult.attacker_actions[0];
                if (action.damage > 0) {
                    const defenderNumber = this.gameState.currentTurn === 1 ? 2 : 1;
                    const defender = this.gameState.creatures[defenderNumber];
                    if (defender) {
                        const newHP = Math.max(0, defender.hp - action.damage);
                        this.gameState.creatures[defenderNumber].hp = newHP;
                        this.updateHP(defenderNumber, newHP, defender.hp + action.damage);
                        if (action.comment) {
                            this.addBattleLog(action.comment);
                        }
                    }
                }
            }
            if (battleResult.battle_end && battleResult.winner) {
                const winnerNumber = battleResult.winner === this.gameState.creatures[1]?.name ? 1 : 2;
                this.endBattle(winnerNumber);
                return;
            }
            const battleEnded = this.checkBattleEnd();
            if (!battleEnded && (battleResult.turn_end !== false)) {
                this.gameState.currentTurn = this.gameState.currentTurn === 1 ? 2 : 1;
                this.updateTurnDisplay();
            }
        }
        catch (error) {
            console.error('バトル結果処理エラー:', error);
            this.addBattleLog('バトル結果処理でエラーが発生しました');
        }
    }
    async processAttackResult(attackData, attackPrompt) {
        try {
            console.log('攻撃結果を処理:', attackData);
            this.addBattleLog(attackData.comment || `攻撃「${attackPrompt}」が発動！`);
            if (attackData.attacker && attackData.attacker.damage !== undefined) {
                const attackerNumber = this.gameState.currentTurn;
                const attacker = this.gameState.creatures[attackerNumber];
                if (attacker) {
                    const oldHP = attacker.hp;
                    const newHP = Math.max(0, attacker.hp + attackData.attacker.damage);
                    this.gameState.creatures[attackerNumber].hp = newHP;
                    this.updateHP(attackerNumber, newHP, oldHP);
                }
            }
            if (attackData.defender && attackData.defender.damage !== undefined) {
                const defenderNumber = this.gameState.currentTurn === 1 ? 2 : 1;
                const defender = this.gameState.creatures[defenderNumber];
                if (defender) {
                    const oldHP = defender.hp;
                    const newHP = Math.max(0, defender.hp + attackData.defender.damage);
                    this.gameState.creatures[defenderNumber].hp = newHP;
                    this.updateHP(defenderNumber, newHP, oldHP);
                    if (newHP <= 0) {
                        this.endBattle(this.gameState.currentTurn);
                        return;
                    }
                }
            }
            const battleEnded = this.checkBattleEnd();
            if (!battleEnded) {
                this.gameState.currentTurn = this.gameState.currentTurn === 1 ? 2 : 1;
                this.updateTurnDisplay();
            }
        }
        catch (error) {
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
                if (mcpData.hp_changes) {
                    this.applyHPChanges(mcpData.hp_changes);
                    this.addBattleLog(comment);
                    const battleEnded = this.checkBattleEnd();
                    if (battleEnded)
                        return;
                    this.gameState.currentTurn = this.gameState.currentTurn === 1 ? 2 : 1;
                    this.updateTurnDisplay();
                }
            }
            else if (typeof mcpData === 'string') {
                comment = mcpData;
                damage = Math.floor(Math.random() * 30) + 10;
            }
            if (damage > 0) {
                const defenderNumber = this.gameState.currentTurn === 1 ? 2 : 1;
                const defender = this.gameState.creatures[defenderNumber];
                if (defender) {
                    const newHP = Math.max(0, defender.hp - damage);
                    this.gameState.creatures[defenderNumber].hp = newHP;
                    this.updateHP(defenderNumber, newHP, defender.hp + damage);
                    this.addBattleLog(comment);
                    if (newHP <= 0) {
                        this.endBattle(this.gameState.currentTurn);
                        return;
                    }
                    this.gameState.currentTurn = this.gameState.currentTurn === 1 ? 2 : 1;
                    this.updateTurnDisplay();
                }
            }
        }
        catch (error) {
            console.error('フォールバック処理エラー:', error);
            this.addBattleLog('フォールバック処理でエラーが発生しました');
        }
    }
    async processFallbackAttackResult(attackResult, attackPrompt) {
        try {
            console.log('攻撃API結果をフォールバック処理:', attackResult);
            const damage = Math.abs(attackResult.defender.damage) || 0;
            const comment = attackResult.comment || `攻撃「${attackPrompt}」が発動！`;
            if (damage > 0) {
                const defenderNumber = this.gameState.currentTurn === 1 ? 2 : 1;
                const defender = this.gameState.creatures[defenderNumber];
                if (defender) {
                    const oldHP = defender.hp;
                    const newHP = Math.max(0, defender.hp - damage);
                    this.gameState.creatures[defenderNumber].hp = newHP;
                    this.updateHP(defenderNumber, newHP, oldHP);
                    this.addBattleLog(comment);
                    if (newHP <= 0) {
                        this.endBattle(this.gameState.currentTurn);
                        return;
                    }
                    this.gameState.currentTurn = this.gameState.currentTurn === 1 ? 2 : 1;
                    this.updateTurnDisplay();
                }
            }
            else {
                this.addBattleLog(comment);
                this.gameState.currentTurn = this.gameState.currentTurn === 1 ? 2 : 1;
                this.updateTurnDisplay();
            }
        }
        catch (error) {
            console.error('攻撃結果フォールバック処理エラー:', error);
            this.addBattleLog('攻撃結果処理でエラーが発生しました');
        }
    }
    async performFallbackAttack(attackPrompt, attacker, defender) {
        try {
            const result = await api.attack(attackPrompt, attacker, defender);
            if (result && result.result) {
                const damage = Math.abs(result.result.defender.damage);
                const comment = result.result.comment;
                const defenderNumber = this.gameState.currentTurn === 1 ? 2 : 1;
                const newHP = Math.max(0, defender.hp - damage);
                this.gameState.creatures[defenderNumber].hp = newHP;
                this.updateHP(defenderNumber, newHP, defender.hp + damage);
                this.addBattleLog(comment);
                if (newHP <= 0) {
                    this.endBattle(this.gameState.currentTurn);
                    return;
                }
                this.gameState.currentTurn = this.gameState.currentTurn === 1 ? 2 : 1;
                this.updateTurnDisplay();
            }
        }
        catch (error) {
            console.error('フォールバック攻撃エラー:', error);
            this.addBattleLog('フォールバック攻撃も失敗しました');
        }
    }
    applyHPChanges(hpChanges) {
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
        if (this.gameState.creatures[1].hp <= 0 && this.gameState.creatures[2].hp <= 0) {
            this.addBattleLog('引き分けです！');
            return true;
        }
        else if (this.gameState.creatures[1].hp <= 0) {
            this.endBattle(2);
            return true;
        }
        else if (this.gameState.creatures[2].hp <= 0) {
            this.endBattle(1);
            return true;
        }
        return false;
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
        if (!winner)
            return;
        this.showLoading('決着処理中...');
        try {
            // 決着処理を実行（勝者の決め台詞を取得）
            const winnerSummonId = this.gameState.summonIds[winnerNumber];
            if (!winnerSummonId)
                return;
            const finishResult = await api.finishBattle(winnerSummonId);
            // 画面を決着画面に切り替え
            this.battlePhase.classList.add('hidden');
            this.resultPhase.classList.remove('hidden');
            this.gamePhase.textContent = 'バトル終了';
            this.winnerDisplay.innerHTML = `🏆 ${winner.name} の勝利！`;
            // 勝者の決め台詞を表示
            const comment = finishResult?.comment || '勝利！';
            this.finishComment.textContent = `「${comment}」`;
            // 勝者の3Dモデルを表示
            await this.showWinnerModel(winner);
            this.addBattleLog(`決着！${winner.name}の勝利: 「${comment}」`);
        }
        catch (error) {
            console.error('決着処理エラー:', error);
            // フォールバック処理
            await this.processFallbackFinishResult(winner);
        }
        this.hideLoading();
    }
    async processFallbackFinishResult(winner) {
        try {
            console.log('フォールバック決着処理:', winner);
            // デフォルトコメント
            const defaultComment = '勝利！';
            // 画面を決着画面に切り替え
            this.battlePhase.classList.add('hidden');
            this.resultPhase.classList.remove('hidden');
            this.gamePhase.textContent = 'バトル終了';
            this.winnerDisplay.innerHTML = `🏆 ${winner.name} の勝利！`;
            this.finishComment.textContent = `「${defaultComment}」`;
            // 勝者の3Dモデルを表示
            await this.showWinnerModel(winner);
            this.addBattleLog(`決着！${winner.name}の勝利`);
        }
        catch (error) {
            console.error('フォールバック決着処理エラー:', error);
            this.addBattleLog('決着処理でエラーが発生しました');
        }
    }
    restart() {
        this.gameState = {
            phase: 'summon',
            creatures: { 1: null, 2: null },
            currentTurn: 1,
            summonIds: { 1: null, 2: null }
        };
        this.resultPhase.classList.add('hidden');
        this.battlePhase.classList.add('hidden');
        this.summonPhase.classList.remove('hidden');
        this.gamePhase.textContent = '召喚準備中';
        this.summon1Input.value = '';
        this.summon2Input.value = '';
        this.attackInput.value = '';
        this.battleLog.innerHTML = '';
        // プルダウンリストをリセット
        this.summon1Select.value = '';
        this.summon2Select.value = '';
        this.summon1Btn.disabled = false;
        this.summon2Btn.disabled = false;
        this.startBattleBtn.disabled = true;
        this.updateAttackButtonState();
        this.summon1Status.innerHTML = '';
        this.summon2Status.innerHTML = '';
        if (globalThis.viewers.creature1) {
            globalThis.viewers.creature1.clearModel();
        }
        if (globalThis.viewers.creature2) {
            globalThis.viewers.creature2.clearModel();
        }
    }
}
//# sourceMappingURL=game.js.map