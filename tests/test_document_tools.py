"""Tests for DocumentTools"""

import pytest
from pathlib import Path
from mcp_server.tools.document import DocumentTools


class TestDocumentTools:
    """DocumentToolsのテスト"""

    @pytest.fixture
    def doc_tools(self, temp_docs_dir):
        """DocumentToolsインスタンス"""
        return DocumentTools(str(temp_docs_dir))

    @pytest.mark.asyncio
    async def test_get_document_success(self, doc_tools):
        """ドキュメント取得成功"""
        content = await doc_tools.get_document("test.txt")
        assert content == "This is a test document."

    @pytest.mark.asyncio
    async def test_get_document_empty_path(self, doc_tools):
        """空のパスでエラー"""
        with pytest.raises(ValueError, match="cannot be empty"):
            await doc_tools.get_document("")

    @pytest.mark.asyncio
    async def test_get_document_invalid_encoding(self, doc_tools):
        """サポートされていないエンコーディングでエラー"""
        with pytest.raises(ValueError, match="Unsupported encoding"):
            await doc_tools.get_document("test.txt", encoding="invalid-encoding")

    @pytest.mark.asyncio
    async def test_get_document_not_found(self, doc_tools):
        """存在しないドキュメントでエラー"""
        with pytest.raises(FileNotFoundError):
            await doc_tools.get_document("nonexistent.txt")

    def test_list_documents_all(self, doc_tools):
        """すべてのドキュメントをリスト"""
        files = doc_tools.list_documents()
        assert len(files) >= 2
        assert "test.txt" in files
        assert "sample.md" in files

    def test_list_documents_with_pattern(self, doc_tools):
        """パターン指定でリスト"""
        md_files = doc_tools.list_documents(pattern="*.md")
        assert "sample.md" in md_files
        assert "test.txt" not in md_files

    def test_list_documents_subdirectory(self, doc_tools):
        """サブディレクトリのリスト"""
        files = doc_tools.list_documents("subdir")
        assert len(files) >= 1
        assert any("nested.txt" in f for f in files)

    @pytest.mark.asyncio
    async def test_search_in_document_found(self, doc_tools, temp_docs_dir):
        """キーワード検索成功"""
        # 検索可能なコンテンツを持つファイルを作成
        search_file = temp_docs_dir / "search_test.txt"
        search_file.write_text(
            "Line 1: Hello\nLine 2: World\nLine 3: Hello again",
            encoding="utf-8"
        )

        result = await doc_tools.search_in_document("search_test.txt", "Hello")
        assert "Line 1:" in result
        assert "Line 3:" in result
        assert "Line 2:" not in result

    @pytest.mark.asyncio
    async def test_search_in_document_not_found(self, doc_tools):
        """キーワードが見つからない"""
        result = await doc_tools.search_in_document("test.txt", "nonexistent")
        assert "not found" in result

    @pytest.mark.asyncio
    async def test_search_in_document_empty_keyword(self, doc_tools):
        """空のキーワードでエラー"""
        with pytest.raises(ValueError, match="cannot be empty"):
            await doc_tools.search_in_document("test.txt", "")

    @pytest.mark.asyncio
    async def test_search_case_insensitive(self, doc_tools, temp_docs_dir):
        """大文字小文字を区別しない検索"""
        search_file = temp_docs_dir / "case_test.txt"
        search_file.write_text("Line 1: HELLO\nLine 2: hello", encoding="utf-8")

        result = await doc_tools.search_in_document("case_test.txt", "hello")
        assert "Line 1:" in result
        assert "Line 2:" in result

    @pytest.mark.asyncio
    async def test_get_document_max_size_limit(self, doc_tools, temp_docs_dir):
        """最大ファイルサイズの制限テスト"""
        # 小さいmax_sizeのDocumentToolsを作成
        small_doc_tools = DocumentTools(str(temp_docs_dir), max_file_size=10)

        # 通常のファイル読み込みでサイズ超過エラー
        with pytest.raises(RuntimeError, match="too large"):
            await small_doc_tools.get_document("test.txt")
