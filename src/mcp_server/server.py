"""MCP Document Server - メインサーバー実装"""

import os
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from mcp_server.tools.document import DocumentTools
from mcp_server.utils.logging import setup_logging

# ロギング設定
logger = setup_logging(__name__)

# MCPサーバーインスタンス作成
mcp = FastMCP("document-server")

# ドキュメントディレクトリの設定
# 環境変数から取得、なければカレントディレクトリ/docs
DOCS_DIR = os.getenv("MCP_DOCS_DIR", str(Path.cwd() / "docs"))

# DocumentToolsインスタンス作成
try:
    # ディレクトリが存在しない場合は作成
    Path(DOCS_DIR).mkdir(parents=True, exist_ok=True)
    doc_tools = DocumentTools(DOCS_DIR)
    logger.info(f"DocumentTools initialized with directory: {DOCS_DIR}")
except Exception as e:
    logger.error(f"Failed to initialize DocumentTools: {e}")
    raise


@mcp.tool()
async def get_document(path: str, encoding: str = "utf-8") -> str:
    """指定されたドキュメントを取得

    Args:
        path: ドキュメントの相対パス（例: "README.md", "guides/setup.md"）
        encoding: ファイルエンコーディング（デフォルト: utf-8）

    Returns:
        ドキュメントの内容

    Example:
        >>> content = await get_document("README.md")
        >>> content = await get_document("docs/api.md", encoding="utf-8")
    """
    logger.debug(f"Tool call: get_document(path={path}, encoding={encoding})")
    try:
        return await doc_tools.get_document(path, encoding)
    except Exception as e:
        error_msg = f"Error getting document: {str(e)}"
        logger.error(error_msg)
        return error_msg


@mcp.tool()
def list_documents(directory: str = ".", pattern: str = "*") -> str:
    """利用可能なドキュメントのリストを取得

    Args:
        directory: 検索するディレクトリ（デフォルト: "."）
        pattern: ファイル名パターン（例: "*.md", "*.txt"）（デフォルト: "*"）

    Returns:
        ドキュメントパスのリスト（改行区切り）

    Example:
        >>> files = list_documents()  # すべてのファイル
        >>> md_files = list_documents(pattern="*.md")  # Markdownファイルのみ
        >>> guide_files = list_documents(directory="guides")  # guidesディレクトリ内
    """
    logger.debug(f"Tool call: list_documents(directory={directory}, pattern={pattern})")
    try:
        files = doc_tools.list_documents(directory, pattern)
        if not files:
            return f"No documents found in '{directory}' matching pattern '{pattern}'"
        return "\n".join(files)
    except Exception as e:
        error_msg = f"Error listing documents: {str(e)}"
        logger.error(error_msg)
        return error_msg


@mcp.tool()
async def search_in_document(
    path: str,
    keyword: str,
    encoding: str = "utf-8"
) -> str:
    """ドキュメント内でキーワードを検索

    Args:
        path: ドキュメントの相対パス
        keyword: 検索するキーワード
        encoding: ファイルエンコーディング（デフォルト: utf-8）

    Returns:
        キーワードを含む行のリスト（行番号付き）

    Example:
        >>> results = await search_in_document("README.md", "installation")
        >>> results = await search_in_document("api.md", "endpoint")
    """
    logger.debug(
        f"Tool call: search_in_document(path={path}, keyword={keyword}, "
        f"encoding={encoding})"
    )
    try:
        return await doc_tools.search_in_document(path, keyword, encoding)
    except Exception as e:
        error_msg = f"Error searching in document: {str(e)}"
        logger.error(error_msg)
        return error_msg


def main():
    """サーバーのエントリーポイント"""
    logger.info("=" * 60)
    logger.info("Starting MCP Document Server")
    logger.info(f"Documents directory: {DOCS_DIR}")
    logger.info("=" * 60)

    try:
        # STDIOトランスポートでサーバーを起動
        mcp.run(transport='stdio')
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.exception(f"Server error: {e}")
        raise


if __name__ == "__main__":
    main()
