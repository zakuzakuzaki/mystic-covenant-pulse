// メインエントリーポイント
import { SummonBattleAPI } from './api.js';
import { ThreeJSViewer, viewers } from './3d-viewer.js';
import { SummonBattleGame } from './game.js';

// グローバル変数の設定

// APIインスタンスをグローバルに設定
const api = new SummonBattleAPI();
(globalThis as any).api = api;

// Viewersをグローバルに設定
(globalThis as any).viewers = viewers;

// ThreeJSViewerクラスをグローバルに設定
(globalThis as any).ThreeJSViewer = ThreeJSViewer;

// ゲーム開始
document.addEventListener('DOMContentLoaded', () => {
    new SummonBattleGame();
});