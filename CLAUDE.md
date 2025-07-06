# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

Kaggle MCP Serverは、Model Context Protocol (MCP)を通じてKaggle APIの機能をLLMアプリケーションに提供するサーバー実装です。FastMCPフレームワークを使用し、コンペティション、データセット、モデルの管理機能を提供します。

## 開発コマンド

### 環境セットアップ
```bash
# uvを使用した依存関係のインストール
uv sync

# Kaggle API認証の設定（以下のいずれか）
# 方法1: kaggle.jsonファイルを配置
# ~/.kaggle/kaggle.json (Linux/Mac)
# C:\Users\<username>\.kaggle\kaggle.json (Windows)

# 方法2: 環境変数を設定
export KAGGLE_USERNAME=your_username
export KAGGLE_KEY=your_api_key
```

### 実行方法
```bash
# uvを使用した実行
uv run -m kaggle_mcp_server

# 開発モードで実行
uv run mcp dev src/kaggle_mcp_server/server.py

# テストの実行（Kaggle API認証なしでも可能）
uv run python test_server.py

# 直接実行（従来の方法）
python -m kaggle_mcp_server
```

### Claude Desktop統合
```bash
# uvを使用した場合
uv run mcp install src/kaggle_mcp_server/server.py --name "Kaggle MCP Server"
```

## アーキテクチャ概要

### コア構成
- **src/kaggle_mcp_server/server.py** - MCPサーバーのメイン実装。FastMCPを使用してツールとリソースを定義
- **src/kaggle_mcp_server/config.py** - 設定管理。Kaggle API認証情報とデフォルト設定を管理
- **src/kaggle_mcp_server/utils.py** - ユーティリティ関数群。エラーハンドリング、バリデーション、キャッシュ実装を提供
- **pyproject.toml** - プロジェクト設定とuv依存関係管理

### レイヤー構造
1. **プレゼンテーション層** - MCPプロトコルとのインターフェース
2. **ビジネスロジック層** - Kaggle APIの操作ロジック
3. **データアクセス層** - Kaggle APIクライアントとの通信
4. **インフラストラクチャ層** - 設定管理、ユーティリティ、キャッシュ

### 実装されている機能

#### ツール（7個）
- `list_competitions` - コンペティション一覧取得
- `get_competition_details` - コンペティション詳細情報
- `download_competition_files` - コンペティションファイルダウンロード
- `search_datasets` - データセット検索
- `get_dataset_details` - データセット詳細情報
- `download_dataset` - データセットダウンロード
- `list_models` - モデル一覧取得

#### リソース（2個）
- `kaggle://competitions/active` - アクティブなコンペティション
- `kaggle://datasets/popular` - 人気のデータセット

### 重要な実装詳細

#### エラーハンドリング
`src/kaggle_mcp_server/utils.py`の`handle_kaggle_errors`デコレータが全てのKaggle API呼び出しをラップし、統一的なエラー処理を提供。

#### キャッシュ機能
`KaggleAPICache`クラスがTTL付きインメモリキャッシュを実装。デフォルトTTLは300秒。

#### バリデーション
- データセット参照形式: `owner/dataset-name`
- ページネーションパラメータの検証
- ファイル名のサニタイゼーション

#### セキュリティ
- API認証情報の安全な管理
- ファイルパスのサニタイゼーション
- ダウンロードディレクトリの制限

## 開発時の注意点

1. **Kaggle API認証**が必要な機能のテスト時は、有効な認証情報を設定すること
2. **エラーハンドリング**は`handle_kaggle_errors`デコレータを使用すること
3. **新機能追加時**は既存のパターンに従い、適切なバリデーションとエラー処理を実装すること
4. **キャッシュ**は頻繁にアクセスされるリソースに対して使用し、TTLを適切に設定すること

## 関連ドキュメント
- 英語版README: `Kaggle MCP Server.md`
- 日本語版詳細ドキュメント: `Kaggle MCP Server - 詳細ドキュメント.md`
- 設計文書: `kaggle_mcp_design.md`
- Kaggle API調査: `kaggle_api_research.md`
- MCP調査: `mcp_research.md`