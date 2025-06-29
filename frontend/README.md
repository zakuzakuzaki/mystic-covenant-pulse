# Frontend Development

このディレクトリにはTypeScriptで作成されたフロントエンドコードが含まれています。

## セットアップ

```bash
# frontend ディレクトリに移動
cd frontend

# 依存関係をインストール
npm install

# TypeScriptをコンパイル
npm run build

# 開発モード（ファイル変更を監視）
npm run watch
```

## ビルド

TypeScriptコードは`../static/js/`にコンパイルされます。

## ファイル構成

- `src/types.ts` - 型定義
- `src/api.ts` - API通信クラス
- `src/3d-viewer.ts` - Three.js 3Dビューアー
- `src/game.ts` - メインゲームロジック
- `src/main.ts` - エントリーポイント

## 開発ワークフロー

1. `frontend/src/` でTypeScriptコードを編集
2. `npm run watch` でリアルタイムコンパイル
3. ブラウザで `http://localhost:8000` をリロードして確認

## 型安全性

TypeScriptにより以下の型安全性が確保されています：

- API レスポンスの型チェック
- DOM要素の型安全なアクセス
- ゲーム状態の型管理
- MCP結果データの構造化された型処理