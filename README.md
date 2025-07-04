# AI召喚獣バトルゲーム

召喚呪文から3D召喚獣を生成してバトルするWebアプリケーションです。

##  紹介記事
- https://protopedia.net/prototype/6842

## 機能

- **召喚システム**: 自由な召喚呪文から召喚獣を生成
- **3D表示**: Three.jsを使用した3D召喚獣の表示
- **バトルシステム**: ターン制の攻撃バトル
- **Claude Desktop連携**: pyautoguiを使用したClaude Desktopの自動制御

## セットアップ

### 前提条件

- Python 3.8以上
- Node.js 16以上 (TypeScriptコンパイル用)
- Claude Desktop (インストール済み)

### インストール

1. 仮想環境の作成と依存関係のインストール
```bash
# 仮想環境の作成
python -m venv .env

# 仮想環境の有効化
# Windows
.\.env\Scripts\Activate.ps1
# macOS/Linux
source .env/bin/activate

# 依存関係のインストール
pip install -r requirements.txt
```

2. フロントエンド（TypeScript）の依存関係とビルド
```bash
# frontendディレクトリに移動
cd frontend

# Node.js依存関係のインストール
npm install

# TypeScriptをJavaScriptにコンパイル
npm run build

```

3. Claude Desktopの座標設定
```bash
# 仮想環境の有効化した状態で実施
python scripts/setup_claude.py
```
カウントダウンが始まったら、Claude Desktopのチャット入力欄にマウスを移動。
カウントゼロで座標が記録されます。

4. 設定ファイルの確認（必要に応じて編集）
```bash
config/app_config.json　# 編集してサーバー設定などを変更
```

### 起動方法

```bash
# 開発サーバーの起動 仮想環境の有効化した状態で実施
python run.py
```

アプリケーションは http://localhost:8000 で利用できます。

## プレイ方法

### 1. 召喚獣の作成

1. 召喚呪文を入力（例：「出でよ神龍 そして願いを叶えたまえ」）
2. 「召喚開始」ボタンをクリック
3. Claude Desktopが自動的にSTLモデルとステータスJSONを生成
4. 2体の召喚獣を作成
5. 既に召喚済みの召喚獣も選択可能

### 2. バトル

1. 「バトル開始」ボタンでバトルフェーズに移行
2. 3D表示された召喚獣が表示される
3. 攻撃呪文を入力してターン制バトル
4. HPが0になると負け

### 3. 結果

- 勝者の決め台詞が表示される
- 「新しいバトル」で再開可能

## 注意事項

### バックエンド
- Claude Desktopが起動している必要があります
- Claude Desktopを起動する前に、バックエンドサーバーを起動しておいてください
- 生成されたモデルと設定情報は`assets/{summonId}/`ディレクトリに保存されます

### フロントエンド
- **重要**: フロントエンドを変更する場合は`frontend/src/`のTypeScriptファイルを編集してください
- `static/js/`のJavaScriptファイルは自動生成されるため直接編集しないでください
- フロントエンド変更後は必ず`npm run build`でコンパイルしてください
- 開発時は`npm run watch`で自動ビルドを有効にすることを推奨します
