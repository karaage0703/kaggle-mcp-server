# Kaggle MCP Server

🚀 **LLMアプリケーションにKaggle APIの機能をシームレスに提供するModel Context Protocol (MCP) サーバー**

## ✨ 主な機能

### 🏆 コンペティション管理
- **コンペティション一覧取得** - 高度なフィルタリング機能付き
- **詳細情報取得** - 特定のコンペティションの完全な情報
- **ファイルダウンロード** - 進捗表示付きでデータをダウンロード

### 📊 データセット操作
- **データセット検索** - Kaggleの膨大なコレクションから検索
- **メタデータ取得** - ファイル構造を含む詳細な情報
- **ダウンロード** - 自動展開機能付き

### 🤖 モデル探索
- **モデル一覧** - フィルタリング機能付きで探索
- **モデル情報** - パフォーマンス指標とメタデータ

### 📚 スマートリソース
- **アクティブコンペ** - リアルタイム更新されるリソース
- **人気データセット** - 自動キュレーションされた情報
- **トレンドトピック** - 最新の技術動向とテクニック
- **締切カレンダー** - コンペティション締切の一覧
- **初心者ガイド** - 学習パスと推奨コンペ
- **プラットフォーム統計** - Kaggleの統計情報

## 🚀 クイックスタート

### インストール

```bash
# uv使用（推奨）
uv sync
```

### 認証設定

**方法1: 環境変数（推奨）**
```bash
export KAGGLE_USERNAME=あなたのユーザー名
export KAGGLE_KEY=あなたのAPIキー
```

**方法2: 設定ファイル**
```bash
# ~/.kaggle/kaggle.json を作成
{
    "username": "あなたのユーザー名", 
    "key": "あなたのAPIキー"
}
```

> 💡 **API認証情報の取得**: [Kaggleアカウント設定](https://www.kaggle.com/settings/account) → Create New Token

### サーバー起動

```bash
# uv使用
uv run -m kaggle_mcp_server

# 開発モード（ホットリロード付き）
uv run mcp dev src/kaggle_mcp_server/server.py

# 直接実行
python -m kaggle_mcp_server
```

### MCP設定

以下設定をすればMCPサーバとして使えます。

`</path/to/kaggle-mcp-server>`には、Kaggle MCP Serverの絶対パスを指定してください。

```json
{
  "mcpServers": {
    "kaggle-mcp-server": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "</path/to/kaggle-mcp-server>",
        "-m",
        "kaggle_mcp_server"
      ]
    }
  }
}
```

## 🛠️ 利用可能なツール

| ツール | 説明 | 使用例 |
|-------|------|--------|
| `list_competitions` | コンペティション一覧取得 | テーブルデータカテゴリのMLコンペを検索 |
| `get_competition_details` | コンペティション詳細情報 | Titanicコンペの詳細情報を取得 |
| `download_competition_files` | コンペティションファイルDL | 住宅価格予測のトレーニングデータをDL |
| `search_datasets` | データセット検索 | 時系列予測用のデータセットを検索 |
| `get_dataset_details` | データセット詳細とファイル構造 | 特定データセットの構造を調査 |
| `download_dataset` | データセットファイルDL | 練習用の人気データセットを取得 |
| `list_models` | 利用可能なモデル探索 | NLPタスク用の事前学習モデルを検索 |

## 📚 MCPリソース

| リソースURI | 説明 | 自動更新 |
|------------|------|---------|
| `kaggle://competitions/active` | 現在アクティブなコンペティション | ✅ |
| `kaggle://datasets/popular` | トレンドと人気のデータセット | ✅ |
| `kaggle://trends/hot-topics` | トレンディングトピックと技術 | ✅ |
| `kaggle://calendar/deadlines` | コンペティション締切カレンダー | ✅ |
| `kaggle://beginner/getting-started` | 初心者向けガイドと学習パス | ✅ |
| `kaggle://meta/platform-stats` | Kaggleプラットフォーム統計 | ✅ |

## 💻 使用例

### コンペティション検索
```python
# LLMが自動的に使用:
"賞金の良いアクティブな機械学習コンペを教えて"

# 実行されるツール: list_competitions（適切なフィルタ付き）
```

### データセット発見
```python
# 自然言語リクエスト:
"売上予測の練習用に時系列データセットが欲しい"

# 実行フロー: search_datasets → get_dataset_details → download_dataset
```

### クイックデータアクセス
```python
# シンプルなリクエスト:
"Titanicデータセットをダウンロードして"

# 使用ツール: search_datasets → download_dataset（自動展開付き）
```


## 🤝 コントリビューション

1. **リポジトリをフォーク**
2. **フィーチャーブランチ作成**: `git checkout -b feature/素晴らしい機能`
3. **変更を加えてテスト追加**
4. **テストスイート実行**: `uv run python test_server.py`
5. **変更をコミット**: `git commit -m '素晴らしい機能を追加'`
6. **ブランチにプッシュ**: `git push origin feature/素晴らしい機能`
7. **プルリクエストを開く**


### よくあるエラー
- **`401 Unauthorized`**: API認証情報を確認
- **`403 Forbidden`**: コンペがプライベートまたは期限切れ
- **`404 Not Found`**: コンペ/データセットIDが不正
- **`Rate Limited`**: 待機してリトライ、またはAPIクォータ確認

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています - 詳細は[LICENSE](LICENSE)ファイルを参照してください。

## 🙏 謝辞

- **Kaggleチーム** - 優秀なAPIの提供
- **FastMCP** - 堅牢なMCPフレームワーク
- **Model Context Protocol** - LLM統合の標準化
