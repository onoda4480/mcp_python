"""pytest configuration and shared fixtures"""

import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_docs_dir():
    """テスト用の一時ドキュメントディレクトリを作成

    Yields:
        Path: 一時ディレクトリのパス
    """
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir)

    # テスト用ファイルを作成
    (temp_path / "test.txt").write_text("This is a test document.", encoding="utf-8")
    (temp_path / "sample.md").write_text("# Sample Document\n\nHello World!", encoding="utf-8")

    # サブディレクトリとファイル
    sub_dir = temp_path / "subdir"
    sub_dir.mkdir()
    (sub_dir / "nested.txt").write_text("Nested document", encoding="utf-8")

    yield temp_path

    # クリーンアップ
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_document_content():
    """サンプルドキュメントの内容"""
    return """# テストドキュメント

これはテスト用のドキュメントです。

## セクション1
重要なキーワードがここにあります。

## セクション2
別の重要な情報がここにあります。
"""


@pytest.fixture
def large_document_content():
    """大きなドキュメントのコンテンツ（パフォーマンステスト用）"""
    return "\n".join([f"Line {i}: This is test content" for i in range(10000)])
