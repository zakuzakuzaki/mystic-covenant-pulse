# 🔮 召喚獣バトルアプリ

召喚呪文から3D召喚獣を生成してバトルするWebアプリケーションです。

## 📋 機能

- **召喚システム**: 自由な召喚呪文から召喚獣を生成
- **3D表示**: Three.jsを使用した3D召喚獣の表示
- **バトルシステム**: ターン制の攻撃バトル
- **Claude Desktop連携**: pyautoguiを使用したClaude Desktopの自動制御

## 🚀 セットアップ

### 前提条件

- Python 3.8以上
- Node.js 16以上 (TypeScriptコンパイル用)
- Claude Desktop (インストール済み)

### インストール

1. 仮想環境の作成と依存関係のインストール:
```bash
# 仮想環境の作成
python -m venv .env

# 仮想環境の有効化
# Windows
.env\Scripts\activate
# macOS/Linux
source .env/bin/activate

# 依存関係のインストール
pip install -r requirements.txt
```

2. フロントエンド（TypeScript）の依存関係とビルド:
```bash
# frontendディレクトリに移動
cd frontend

# Node.js依存関係のインストール
npm install

# TypeScriptをJavaScriptにコンパイル
npm run build

# 開発時はwatchモードでビルド（自動再コンパイル）
npm run watch
```

3. Claude Desktopの座標設定:
```bash
python scripts/setup_claude.py
```

4. 設定ファイルの確認（必要に応じて編集）:
```bash
# config/app_config.json を編集してサーバー設定などを変更
```

### 起動方法

```bash
# 開発サーバーの起動
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# または
python run.py
```

アプリケーションは http://localhost:8000 で利用できます。

## 📁 プロジェクト構造

```
mystic-covenant-pulse/
├── app/                   # メインアプリケーション
│   ├── __init__.py
│   ├── main.py           # FastAPIアプリケーション
│   ├── api/              # APIエンドポイント
│   │   ├── __init__.py
│   │   ├── models.py     # データモデル
│   │   ├── summons.py    # 召喚API
│   │   └── battle.py     # バトルAPI
│   ├── core/             # 設定とユーティリティ
│   │   ├── __init__.py
│   │   └── config.py     # 設定管理
│   └── services/         # ビジネスロジック
│       ├── __init__.py
│       ├── claude_controller.py  # Claude Desktop制御
│       ├── file_manager.py       # ファイル管理
│       └── mcp_manager.py        # MCP結果管理
├── frontend/              # TypeScriptフロントエンド開発環境
│   ├── package.json      # Node.js依存関係
│   ├── tsconfig.json     # TypeScript設定
│   └── src/              # TypeScriptソースコード
│       ├── types.ts      # 型定義
│       ├── api.ts        # API呼び出しクラス
│       ├── 3d-viewer.ts  # Three.js 3Dビューアー
│       ├── game.ts       # ゲームメインロジック
│       └── main.ts       # エントリーポイント
├── scripts/              # スクリプト類
│   └── setup_claude.py  # Claude Desktop設定
├── static/               # フロントエンド（コンパイル済み）
│   ├── index.html        # メインページ
│   ├── css/style.css     # スタイルシート
│   └── js/               # TypeScriptコンパイル済みJavaScript
│       ├── main.js       # エントリーポイント
│       ├── api.js        # API呼び出し
│       ├── 3d-viewer.js  # 3Dビューアー
│       └── game.js       # ゲームロジック
├── assets/               # 生成されたモデル保存場所
│   ├── {summonId}/       # 召喚獣ごとのディレクトリ
│   │   ├── model.stl     # 3Dモデルファイル
│   │   └── status.json   # ステータス情報
│   └── mcp_results/      # MCP結果ファイル
├── config/               # 設定ファイル
│   ├── app_config.json   # アプリケーション設定
│   └── claude_desktop_config.json  # Claude Desktop座標設定
├── examples/             # サンプルコード
├── tests/               # テスト
├── .gitignore
├── requirements.txt     # 本番依存関係
├── requirements-dev.txt # 開発依存関係
├── run.py              # アプリケーション起動スクリプト
└── README.md
```

## 🎮 使用方法

### 1. 召喚獣の作成

1. 召喚呪文を入力（例：「出でよ神龍 そして願いを叶えたまえ」）
2. 「召喚開始」ボタンをクリック
3. Claude Desktopが自動的にSTLモデルとステータスJSONを生成
4. 2体の召喚獣を作成

### 2. バトル

1. 「バトル開始」ボタンでバトルフェーズに移行
2. 3D表示された召喚獣が表示される
3. 攻撃呪文を入力してターン制バトル
4. HPが0になると勝敗決定

### 3. 結果

- 勝者の決め台詞が表示される
- 「新しいバトル」で再開可能

## 🔧 API仕様

### 召喚API

```http
POST /api/summons
Content-Type: application/json

{
  "prompt": "召喚呪文"
}
```

### 召喚状態確認

```http
GET /api/summons/{summonId}
```

### 攻撃API

```http
POST /api/battle/attack
Content-Type: application/json

{
  "prompt": "攻撃呪文",
  "me": { "name": "...", "hp": 100, ... },
  "enemy": { "name": "...", "hp": 80, ... }
}
```

### 決着API

```http
POST /api/battle/finish
Content-Type: application/json

{
  "winner": { "name": "...", "hp": 50, ... }
}
```

## 🛠️ 開発

### フロントエンド開発

TypeScriptで開発し、JavaScriptにコンパイルして使用します。

```bash
# frontendディレクトリでの開発
cd frontend

# 依存関係のインストール
npm install

# 一回限りのビルド
npm run build

# 開発時のwatch（ファイル変更時に自動ビルド）
npm run watch
```

### TypeScript設定

- **ターゲット**: ES2020
- **モジュール**: ESNext（ES6 modules）
- **出力先**: `../static/js/`
- **型チェック**: 厳密モード有効

### 型安全性

- 全てのAPI呼び出しに型定義
- Three.js用の型定義を使用
- 厳密なNull/Undefinedチェック

### テスト実行

```bash
pytest tests/
```

### コードフォーマット

```bash
black src/
isort src/
flake8 src/
```

## 📝 注意事項

### バックエンド
- Claude Desktopが起動している必要があります
- 初回使用時は`examples/py2claude.py`でClaude Desktopの座標を設定してください
- STLファイルの生成には時間がかかる場合があります
- 生成されたモデルは`assets/{summonId}/`ディレクトリに保存されます

### フロントエンド
- **重要**: フロントエンドを変更する場合は`frontend/src/`のTypeScriptファイルを編集してください
- `static/js/`のJavaScriptファイルは自動生成されるため直接編集しないでください
- フロントエンド変更後は必ず`npm run build`でコンパイルしてください
- 開発時は`npm run watch`で自動ビルドを有効にすることを推奨します
- Three.jsはCDNから読み込まれ、ES6モジュールとして使用されます

## 💾 ファイル管理

### 生成ファイル構造
```
assets/
├── abc123-def456-789/     # 召喚ID
│   ├── model.stl          # 3Dモデル
│   └── status.json        # ステータス
└── xyz789-abc123-456/     # 別の召喚ID
    ├── model.stl
    └── status.json

config/
├── app_config.json              # アプリケーション設定
└── claude_desktop_config.json  # Claude Desktop座標設定（gitignore対象）
```

### APIエンドポイントでのファイルアクセス
- STLファイル: `GET /assets/{summonId}/model.stl`
- ステータス: `GET /assets/{summonId}/status.json`
