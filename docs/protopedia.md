# 作品タイトル

**MCP(Mystic Covenant Pulse) - AI召喚獣バトルゲーム**

## 作品のURL

https://github.com/zakuzakuzaki/mystic-covenant-pulse

## 概要

**詠唱（プロンプト）で召喚し、3Dバトル！**

本作は、生成AIとBlenderを活用したAI召喚獣バトルゲームです。
ユーザーが詠唱を入力すると、[MCP（Model Context Protocol）](https://docs.anthropic.com/ja/docs/claude-code/mcp)を通じてBlenderで召喚獣の3Dモデルが生成され、Webアプリ上に出現します。さらに、指示によってバトル体験が可能です。召喚獣は仮想空間だけでなく、3Dプリンタを使って現実世界にも"召喚"されます。

## 画像

- 召喚画面のスクリーンショット(プロンプト入力)
- 生成された召喚獣（Blenderもしくは3Dビューワー）
- バトル画面
- 結果表示画面

## 動画

- 召喚から3Dモデル生成までのデモ
- バトルシステムのプレイ動画
- Claude Desktop自動化の様子

## システム構成

### 方針

Claude DesktopがMCPクライアントとして**超優秀**なので、それを活用しています。
ただし、プログラムからClaude Desktopに直接プロンプトなどは渡せません。
そこで、[PyAutoGUI](https://pyautogui.readthedocs.io/en/latest/)を使ってチャット画面にテキストをコピペすることで、プログラムから入力できるようにしています。
Claude Desktopの生成結果はMCPを通じて、プログラムに戻され、3Dモデル生成やバトル処理に活用されます。

### システム構成図

![システム構成図](mcp_diagram.png "システム構成図")

**バックエンド**
- **Python** - FastAPIが簡単にMCP使えるので採用
- **FastAPI** - REST API、MCP サーバー
- **MCP (Model Context Protocol)** - Claude Desktopと連携
- **PyAutoGUI** - GUI操作で、Claude Desktopを操作

**フロントエンド**
- **TypeScript**
- **Three.js** - 召喚獣を3Dレンダリング

## 🔮 詠唱から召喚までのプロセス

1. **ユーザーが呪文（プロンプト）を入力**
2. PyAutoGUIによってClaude Desktopに自動で貼り付け＆送信
3. Claudeが呪文から召喚獣の特徴・名前・技・パラメータなどを自然文で出力
4. その出力をMCPを通してPythonサーバーが受け取る
5. PythonサーバーがBlenderを制御し、3Dモデルを自動生成
6. 生成されたモデルは .stl ファイルとして保存され、同時に .jsonファイルとしてキャラ情報も格納

## ⚔️ バトルシステム（仮想空間）

- Webアプリ上で2体の召喚獣が**対戦**します。
- バトル中は以下の要素を使用：
  - 召喚時に生成されたHPなど
  - 技（例：属性攻撃や特殊スキル）
  - ターン制もしくは自動処理によるアニメーション演出
- Three.jsを用いて、**召喚獣を3Dで表示・演出**します。

## 🖨️ 3Dプリンタによる「現実世界への召喚」

- 召喚獣のSTLモデルはMCP経由で**3Dプリンタに送信**されます。
- 使用しているプリンタには「召喚ゲート」を模した装飾が施されており、
  - 光やエフェクト演出（LED等）
  - 自動印刷トリガー
  - 演出後に実物の召喚獣フィギュアが現れる

という、**現実世界での"召喚儀式"**が成立します。

## 開発素材

- Claude Desktop
- MCP（Model Context Protocol）
- Blender
- PyAutoGUI
- FastAPI
- Three.js
- 3Dプリンタ（Bambu Labなど）

## タグ

- MCP
- Claude Desktop
- Three.js
- FastAPI
- GUI自動化
- 3Dプリント
- 生成AI
- ゲーム

## ストーリー

### 開発背景

アイデアは、[MCP ハッカソン by 生成AIハッカソンvol.05](https://mashupawards.connpass.com/event/357647/)の中で生まれました。
MCPと言えば自動化が注目されていますが、それを面白いに全振りした作品を作りたいと考えました。
呪文を詠唱することでキャラクターが現実空間に出現するという、**"没入体験"**にこだわって設計しています。

### 技術的挑戦

- **GUIによるハッキング**：Claude DesktopをGUI経由で制御するというユニークな連携を実現
- **チャット指示によるゲーム体験**：AIに指示を送り、モデル生成とバトルを自然な流れで一貫して体験可能に
- **3Dプリンタを"召喚機"化**：STL生成と出力の自動化により、仮想から現実へと召喚をつなぐ仕組みを実現

## メンバー登録

開発者: [開発者名]（※追記予定）

## 関連リンク

https://mashupawards.connpass.com/event/357647