# Kaggle MCP Server

🚀 **LLMアプリケーションにKaggle APIの機能をシームレスに提供するModel Context Protocol (MCP) サーバー**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-enabled-green.svg)](https://github.com/jlowin/fastmcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

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

## 🚀 クイックスタート

### インストール

```bash
# uv使用（推奨）
uv sync

# 従来のpip
pip install kaggle fastmcp python-dotenv
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

### Claude Desktop統合

```bash
# MCPサーバーとしてインストール
uv run mcp install src/kaggle_mcp_server/server.py --name "Kaggle MCP Server"
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

## 🔧 設定

### 環境変数
```bash
KAGGLE_USERNAME=あなたのユーザー名    # 必須: Kaggleユーザー名
KAGGLE_KEY=あなたのAPIキー          # 必須: Kaggle APIキー
MCP_CACHE_TTL=300                  # オプション: キャッシュ期間（秒）
MCP_DEBUG=false                    # オプション: デバッグログ有効化
```

### 高度な設定
```bash
# カスタムダウンロードディレクトリ
export KAGGLE_DOWNLOAD_PATH="./data"

# 接続タイムアウト
export KAGGLE_TIMEOUT=30
```

## 🏗️ アーキテクチャ

```
┌─────────────────────────────────────────┐
│           MCPインターフェース層          │  ← FastMCPプロトコル
├─────────────────────────────────────────┤
│         ビジネスロジック層              │  ← Competition/Dataset/Modelサービス
├─────────────────────────────────────────┤
│        インフラストラクチャ層            │  ← 認証、キャッシュ、エラーハンドリング
├─────────────────────────────────────────┤
│         データアクセス層                │  ← Kaggle APIクライアント
└─────────────────────────────────────────┘
```

## 🔒 セキュリティ機能

- ✅ **安全な認証情報管理** - 環境変数による管理
- ✅ **入力値検証** - バリデーションとサニタイゼーション
- ✅ **読み取り専用設計** - データ変更操作なし
- ✅ **安全なファイルパス処理** - ディレクトリ制限付き
- ✅ **エラーメッセージ最適化** - 情報漏洩防止

## ⚡ パフォーマンス最適化

- 🚀 **インテリジェントキャッシュ** - TTLベース無効化
- 🔄 **非同期処理** - 並行操作対応
- 🌐 **コネクションプール** - 効率的なAPI通信
- 📦 **ストリーミングDL** - 大容量ファイル対応

## 🧪 テスト

```bash
# テスト実行（基本テストは認証不要）
uv run python test_server.py

# 認証ありテスト
export KAGGLE_USERNAME=test_user
export KAGGLE_KEY=test_key
python test_server.py
```

## 🚫 現在の制限事項

- **読み取り専用**: データ変更機能なし
- **ファイルサイズ制限**: 大容量DLでタイムアウトの可能性
- **レート制限**: Kaggle API制限に従う
- **ディスカッション未対応**: Kaggle APIが未サポート

## 🗂️ プロジェクト構成

```
kaggle-mcp-server/
├── src/kaggle_mcp_server/
│   ├── server.py          # メインMCPサーバー実装
│   ├── config.py          # 設定管理
│   ├── utils.py           # ユーティリティとエラーハンドリング
│   └── __init__.py
├── docs/                  # ドキュメント
├── tests/                 # テストスイート
├── pyproject.toml         # プロジェクト設定
├── CLAUDE.md             # 開発ガイドライン
├── design.md             # アーキテクチャドキュメント
└── README.md             # このファイル
```

## 🤝 コントリビューション

1. **リポジトリをフォーク**
2. **フィーチャーブランチ作成**: `git checkout -b feature/素晴らしい機能`
3. **変更を加えてテスト追加**
4. **テストスイート実行**: `uv run python test_server.py`
5. **変更をコミット**: `git commit -m '素晴らしい機能を追加'`
6. **ブランチにプッシュ**: `git push origin feature/素晴らしい機能`
7. **プルリクエストを開く**

## 🐛 トラブルシューティング

### 認証問題
```bash
# 認証情報確認
kaggle competitions list

# 環境変数確認
echo $KAGGLE_USERNAME
echo $KAGGLE_KEY
```

### 接続問題
```bash
# Kaggle API接続テスト
python -c "from kaggle.api.kaggle_api_extended import KaggleApi; api = KaggleApi(); api.authenticate(); print('OK')"
```

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

## 📞 サポート

- 📖 **ドキュメント**: [設計文書](docs/design.md)
- 🐛 **課題報告**: [GitHub Issues](https://github.com/your-username/kaggle-mcp-server/issues)
- 💬 **ディスカッション**: [GitHub Discussions](https://github.com/your-username/kaggle-mcp-server/discussions)

---

**❤️ データサイエンスコミュニティのために作られました**