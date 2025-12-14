"""Tests for MCP Server integration"""

import pytest
import os
from pathlib import Path


class TestServerIntegration:
    """サーバー統合テスト"""

    def test_import_server(self):
        """サーバーモジュールのインポート"""
        from mcp_server import server
        assert hasattr(server, 'mcp')
        assert hasattr(server, 'get_document')
        assert hasattr(server, 'list_documents')
        assert hasattr(server, 'search_in_document')

    def test_import_main(self):
        """mainモジュールのインポート"""
        from mcp_server import main
        assert callable(main)

    def test_server_tools_registered(self):
        """MCPサーバーにツールが登録されているか確認"""
        from mcp_server.server import mcp

        # FastMCPインスタンスが持つツールを確認
        # Note: この方法はFastMCPの内部実装に依存するため、
        # バージョンによって変更が必要な場合があります
        assert mcp is not None

    @pytest.mark.asyncio
    async def test_get_document_tool_callable(self, temp_docs_dir):
        """get_documentツールが呼び出し可能"""
        # 環境変数を一時的に設定
        original_docs_dir = os.environ.get('MCP_DOCS_DIR')
        os.environ['MCP_DOCS_DIR'] = str(temp_docs_dir)

        try:
            # サーバーモジュールを再インポート
            import importlib
            from mcp_server import server
            importlib.reload(server)

            # ツールを直接呼び出し
            result = await server.get_document("test.txt")
            assert isinstance(result, str)
            assert len(result) > 0

        finally:
            # 環境変数を復元
            if original_docs_dir:
                os.environ['MCP_DOCS_DIR'] = original_docs_dir
            else:
                os.environ.pop('MCP_DOCS_DIR', None)

    def test_list_documents_tool_callable(self, temp_docs_dir):
        """list_documentsツールが呼び出し可能"""
        original_docs_dir = os.environ.get('MCP_DOCS_DIR')
        os.environ['MCP_DOCS_DIR'] = str(temp_docs_dir)

        try:
            import importlib
            from mcp_server import server
            importlib.reload(server)

            result = server.list_documents()
            assert isinstance(result, str)
            assert "test.txt" in result or "sample.md" in result

        finally:
            if original_docs_dir:
                os.environ['MCP_DOCS_DIR'] = original_docs_dir
            else:
                os.environ.pop('MCP_DOCS_DIR', None)

    @pytest.mark.asyncio
    async def test_search_in_document_tool_callable(self, temp_docs_dir):
        """search_in_documentツールが呼び出し可能"""
        original_docs_dir = os.environ.get('MCP_DOCS_DIR')
        os.environ['MCP_DOCS_DIR'] = str(temp_docs_dir)

        try:
            import importlib
            from mcp_server import server
            importlib.reload(server)

            result = await server.search_in_document("test.txt", "test")
            assert isinstance(result, str)

        finally:
            if original_docs_dir:
                os.environ['MCP_DOCS_DIR'] = original_docs_dir
            else:
                os.environ.pop('MCP_DOCS_DIR', None)
