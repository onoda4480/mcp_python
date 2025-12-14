# MCP Document Server

**効率的なドキュメント配信のためのModel Context Protocol (MCP) サーバー**

プロジェクトのドキュメントをAIエージェント（Claude等）に必要に応じて提供し、トークン使用量を最適化します。

## 🎯 目的

- プロジェクトのドキュメントを効率的にAIエージェントに配信
- 必要な時だけコンテキストを読み込み、トークン使用量を削減
- チーム内で簡単に共有できる構成

## 📋 機能

### MCPツール（AIが使用可能な機能）

1. **`get_document`** - 指定されたドキュメントを取得
2. **`list_documents`** - 利用可能なドキュメントのリストを表示
3. **`search_in_document`** - ドキュメント内でキーワードを検索

### セキュリティ機能

- パストラバーサル攻撃対策
- ファイルサイズ制限
- 入力バリデーション
- 安全なエンコーディング処理

## 🚀 クイックスタート

### 必要要件

- Python 3.10以上
- Poetry（推奨）または pip
- Docker（オプション、チーム配布用）

### インストール

#### 1. Poetry を使用（推奨）

```bash
# リポジトリをクローン
git clone <your-repo-url>
cd mcp_python

# 依存関係をインストール
poetry install

# 開発依存関係も含む
poetry install
```

#### 2. pipを使用

```bash
pip install -e .
```

### サーバーの起動

#### ローカル実行

```bash
# ドキュメントディレクトリを指定
export MCP_DOCS_DIR=/path/to/your/documents

# サーバー起動
poetry run python -m mcp_server.main

# または Makefile を使用
make run
```

#### Docker で実行

```bash
# イメージをビルド
docker build -t mcp-document-server:latest .

# 実行（docsディレクトリをマウント）
docker run -it --rm \
  -v $(PWD)/docs:/app/docs:ro \
  mcp-document-server:latest

# または Makefile を使用
make docker-build
make docker-run
```

#### Docker Compose で実行

```bash
docker-compose up -d
```

## 🔧 Claude Desktop との連携

### 設定ファイル

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### ローカル実行の場合

```json
{
  "mcpServers": {
    "document-server": {
      "command": "poetry",
      "args": ["run", "python", "-m", "mcp_server.main"],
      "env": {
        "MCP_DOCS_DIR": "/path/to/your/documents"
      }
    }
  }
}
```

### Docker実行の場合

```json
{
  "mcpServers": {
    "document-server": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-v",
        "/path/to/your/documents:/app/docs:ro",
        "mcp-document-server:latest"
      ]
    }
  }
}
```

## 🧪 テスト

### テストの実行

```bash
# すべてのテストを実行
poetry run pytest

# カバレッジ付きで実行
poetry run pytest --cov=src/mcp_server --cov-report=html

# または Makefile を使用
make test
make test-cov
```

### MCP Inspector でテスト

サーバーをインタラクティブにテストできます：

```bash
npx @modelcontextprotocol/inspector poetry run python -m mcp_server.main

# または Makefile を使用
make inspect
```

## 📁 プロジェクト構造

```
mcp_python/
├── src/
│   └── mcp_server/
│       ├── __init__.py
│       ├── server.py          # メインサーバー
│       ├── main.py            # エントリーポイント
│       ├── tools/
│       │   └── document.py    # ドキュメントツール
│       ├── resources/
│       │   └── file_handler.py # 安全なファイル操作
│       └── utils/
│           └── logging.py     # ロギング設定
├── tests/                     # テストファイル
├── docs/                      # ドキュメントディレクトリ
├── Dockerfile                 # Docker設定
├── docker-compose.yml         # Docker Compose設定
├── pyproject.toml            # プロジェクト設定
├── pytest.ini                # Pytest設定
├── Makefile                  # 便利コマンド
└── README.md
```

## 🛠️ 開発

### コードフォーマット

```bash
# リンター実行
poetry run ruff check src/ tests/

# 自動フォーマット
poetry run ruff format src/ tests/

# または Makefile を使用
make lint
make format
```

### クリーンアップ

```bash
make clean
```

## 📦 チーム配布

### Docker Hub へのプッシュ

```bash
# イメージをビルド
docker build -t your-org/mcp-document-server:latest .

# Docker Hub にログイン
docker login

# プッシュ
docker push your-org/mcp-document-server:latest
```

### チームメンバー側の設定

```bash
# イメージを取得
docker pull your-org/mcp-document-server:latest
```

Claude Desktop の設定：
```json
{
  "mcpServers": {
    "document-server": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-v",
        "/path/to/documents:/app/docs:ro",
        "your-org/mcp-document-server:latest"
      ]
    }
  }
}
```

## ⚠️ 重要な注意事項

### ロギング

**STDIO通信では `print()` は使用禁止です！**

```python
# ❌ これはNG（JSON-RPCメッセージが壊れる）
print("Debug message")

# ✅ これはOK
logger.info("Debug message")  # stderr に出力
```

### ファイルパス

- ドキュメントは `MCP_DOCS_DIR` で指定したディレクトリ以下に配置
- パストラバーサル攻撃を防ぐため、ディレクトリ外へのアクセスは拒否されます

## 📝 使用例

### Claudeでの利用

```
ユーザー: プロジェクトのドキュメントにはどんなものがありますか？

Claude: (list_documentsツールを使用)
以下のドキュメントが利用可能です：
- README.md
- docs/api.md
- docs/setup.md

ユーザー: setup.mdの内容を教えてください

Claude: (get_documentツールを使用してドキュメントを取得し、内容を説明)
```

## 🤝 コントリビューション

プルリクエスト歓迎！

## 📄 ライセンス

[ライセンスを記載してください]

## 🔗 参考リンク

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Claude Desktop](https://claude.ai/download)