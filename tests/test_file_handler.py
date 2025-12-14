"""Tests for SafeFileHandler"""

import pytest
from pathlib import Path
from mcp_server.resources.file_handler import SafeFileHandler


class TestSafeFileHandler:
    """SafeFileHandlerのテスト"""

    def test_init_valid_directory(self, temp_docs_dir):
        """正常なディレクトリで初期化"""
        handler = SafeFileHandler(str(temp_docs_dir))
        assert handler.base_path == temp_docs_dir.resolve()

    def test_init_invalid_directory(self):
        """存在しないディレクトリで初期化"""
        with pytest.raises(ValueError, match="does not exist"):
            SafeFileHandler("/nonexistent/directory")

    def test_init_file_instead_of_directory(self, temp_docs_dir):
        """ファイルパスで初期化（エラー）"""
        file_path = temp_docs_dir / "test.txt"
        with pytest.raises(ValueError, match="not a directory"):
            SafeFileHandler(str(file_path))

    @pytest.mark.asyncio
    async def test_read_valid_file(self, temp_docs_dir):
        """正常なファイル読み込み"""
        handler = SafeFileHandler(str(temp_docs_dir))
        content = await handler.read("test.txt")
        assert content == "This is a test document."

    @pytest.mark.asyncio
    async def test_read_nested_file(self, temp_docs_dir):
        """ネストされたファイルの読み込み"""
        handler = SafeFileHandler(str(temp_docs_dir))
        content = await handler.read("subdir/nested.txt")
        assert content == "Nested document"

    @pytest.mark.asyncio
    async def test_read_nonexistent_file(self, temp_docs_dir):
        """存在しないファイルの読み込み"""
        handler = SafeFileHandler(str(temp_docs_dir))
        with pytest.raises(FileNotFoundError):
            await handler.read("nonexistent.txt")

    @pytest.mark.asyncio
    async def test_path_traversal_attack(self, temp_docs_dir):
        """パストラバーサル攻撃の検出"""
        handler = SafeFileHandler(str(temp_docs_dir))

        # 様々なパストラバーサルパターンをテスト
        malicious_paths = [
            "../../../etc/passwd",
            "subdir/../../etc/passwd",
            "./../outside.txt",
        ]

        for malicious_path in malicious_paths:
            with pytest.raises(ValueError, match="Path traversal detected"):
                await handler.read(malicious_path)

    @pytest.mark.asyncio
    async def test_read_with_max_size(self, temp_docs_dir):
        """ファイルサイズ制限のテスト"""
        handler = SafeFileHandler(str(temp_docs_dir))

        # 正常（制限内）
        content = await handler.read("test.txt", max_size=1000)
        assert len(content) > 0

        # エラー（制限超過）
        with pytest.raises(RuntimeError, match="File too large"):
            await handler.read("test.txt", max_size=10)

    @pytest.mark.asyncio
    async def test_read_with_encoding(self, temp_docs_dir):
        """エンコーディング指定のテスト"""
        handler = SafeFileHandler(str(temp_docs_dir))

        # UTF-8で読み込み
        content = await handler.read("test.txt", encoding="utf-8")
        assert isinstance(content, str)

    def test_list_files_root(self, temp_docs_dir):
        """ルートディレクトリのファイルリスト"""
        handler = SafeFileHandler(str(temp_docs_dir))
        files = handler.list_files(".")

        assert "test.txt" in files
        assert "sample.md" in files
        assert len(files) >= 2

    def test_list_files_with_pattern(self, temp_docs_dir):
        """パターンマッチングでファイルリスト"""
        handler = SafeFileHandler(str(temp_docs_dir))
        md_files = handler.list_files(".", pattern="*.md")

        assert "sample.md" in md_files
        assert "test.txt" not in md_files

    def test_list_files_subdirectory(self, temp_docs_dir):
        """サブディレクトリのファイルリスト"""
        handler = SafeFileHandler(str(temp_docs_dir))
        files = handler.list_files("subdir")

        assert any("nested.txt" in f for f in files)

    def test_list_files_path_traversal(self, temp_docs_dir):
        """list_filesでのパストラバーサル検出"""
        handler = SafeFileHandler(str(temp_docs_dir))

        with pytest.raises(ValueError, match="Path traversal detected"):
            handler.list_files("../")

    def test_list_files_nonexistent_directory(self, temp_docs_dir):
        """存在しないディレクトリのリスト"""
        handler = SafeFileHandler(str(temp_docs_dir))

        with pytest.raises(FileNotFoundError):
            handler.list_files("nonexistent_dir")
