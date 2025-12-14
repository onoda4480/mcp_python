"""ドキュメント操作ツール"""

from typing import Optional
from mcp_server.resources.file_handler import SafeFileHandler
from mcp_server.utils.logging import setup_logging

logger = setup_logging(__name__)


class DocumentTools:
    """ドキュメント関連のMCPツール

    Args:
        documents_dir: ドキュメントのベースディレクトリ
        max_file_size: 最大ファイルサイズ（バイト）
    """

    def __init__(
        self,
        documents_dir: str,
        max_file_size: int = 10 * 1024 * 1024  # 10MB
    ):
        self.file_handler = SafeFileHandler(documents_dir)
        self.max_file_size = max_file_size
        logger.info(f"DocumentTools initialized with base_dir: {documents_dir}")

    async def get_document(
        self,
        path: str,
        encoding: str = "utf-8"
    ) -> str:
        """指定されたドキュメントを取得

        Args:
            path: ドキュメントの相対パス
            encoding: ファイルエンコーディング（utf-8, shift_jis等）

        Returns:
            ドキュメントの内容

        Raises:
            ValueError: 無効なパスまたはエンコーディング
            FileNotFoundError: ファイルが見つからない
            RuntimeError: 読み込みエラーまたはファイルサイズ超過
        """
        logger.info(f"Fetching document: {path} (encoding: {encoding})")

        try:
            # 入力バリデーション
            if not path or path.strip() == "":
                raise ValueError("Path cannot be empty")

            # サポートされているエンコーディングチェック
            supported_encodings = ["utf-8", "shift_jis", "euc-jp", "cp932"]
            if encoding not in supported_encodings:
                raise ValueError(
                    f"Unsupported encoding: {encoding}. "
                    f"Supported: {', '.join(supported_encodings)}"
                )

            # ファイル読み込み
            content = await self.file_handler.read(
                path,
                encoding=encoding,
                max_size=self.max_file_size
            )

            logger.info(
                f"Successfully fetched document: {path} "
                f"({len(content)} characters)"
            )
            return content

        except ValueError as e:
            logger.warning(f"Validation error for {path}: {e}")
            raise
        except FileNotFoundError as e:
            logger.error(f"File not found: {path}")
            raise
        except RuntimeError as e:
            logger.error(f"Runtime error for {path}: {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error fetching {path}: {e}")
            raise RuntimeError(f"Failed to fetch document: {e}")

    def list_documents(
        self,
        directory: str = ".",
        pattern: str = "*"
    ) -> list[str]:
        """ドキュメントのリストを取得

        Args:
            directory: 検索するディレクトリ（基準ディレクトリからの相対パス）
            pattern: ファイル名パターン（例: "*.md", "*.txt"）

        Returns:
            ドキュメントパスのリスト

        Raises:
            ValueError: 無効なパス
            FileNotFoundError: ディレクトリが見つからない
        """
        logger.info(f"Listing documents in: {directory} (pattern: {pattern})")

        try:
            files = self.file_handler.list_files(directory, pattern)
            logger.info(f"Found {len(files)} documents")
            return files

        except Exception as e:
            logger.exception(f"Error listing documents: {e}")
            raise

    async def search_in_document(
        self,
        path: str,
        keyword: str,
        encoding: str = "utf-8"
    ) -> str:
        """ドキュメント内でキーワードを検索

        Args:
            path: ドキュメントの相対パス
            keyword: 検索キーワード
            encoding: ファイルエンコーディング

        Returns:
            キーワードを含む行のリスト（行番号付き）

        Raises:
            ValueError: 無効な入力
            FileNotFoundError: ファイルが見つからない
        """
        logger.info(f"Searching for '{keyword}' in {path}")

        if not keyword or keyword.strip() == "":
            raise ValueError("Keyword cannot be empty")

        # ドキュメント取得
        content = await self.get_document(path, encoding)

        # キーワード検索
        results = []
        lines = content.split('\n')
        for line_num, line in enumerate(lines, start=1):
            if keyword.lower() in line.lower():
                results.append(f"Line {line_num}: {line.strip()}")

        if not results:
            return f"Keyword '{keyword}' not found in {path}"

        logger.info(f"Found {len(results)} matches for '{keyword}' in {path}")
        return "\n".join(results)
