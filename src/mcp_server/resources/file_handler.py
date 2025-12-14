"""安全なファイルハンドラー - パストラバーサル攻撃対策"""

import aiofiles
from pathlib import Path
from typing import Optional


class SafeFileHandler:
    """パストラバーサル攻撃を防ぐ安全なファイルハンドラー

    Args:
        base_dir: 基準ディレクトリ（このディレクトリ外へのアクセスを防止）

    Example:
        >>> handler = SafeFileHandler("/home/user/documents")
        >>> content = await handler.read("report.txt")  # OK
        >>> content = await handler.read("../etc/passwd")  # ValueError
    """

    def __init__(self, base_dir: str):
        self.base_path = Path(base_dir).resolve()

        if not self.base_path.exists():
            raise ValueError(f"Base directory does not exist: {base_dir}")

        if not self.base_path.is_dir():
            raise ValueError(f"Base path is not a directory: {base_dir}")

    async def read(
        self,
        relative_path: str,
        encoding: str = "utf-8",
        max_size: Optional[int] = None
    ) -> str:
        """ファイルを安全に読み込む

        Args:
            relative_path: 基準ディレクトリからの相対パス
            encoding: ファイルエンコーディング（デフォルト: utf-8）
            max_size: 最大ファイルサイズ（バイト）。Noneの場合は制限なし

        Returns:
            ファイル内容

        Raises:
            ValueError: パストラバーサル攻撃を検出した場合
            FileNotFoundError: ファイルが存在しない場合
            RuntimeError: ファイルサイズが制限を超える場合
        """
        # 絶対パスを解決
        full_path = (self.base_path / relative_path).resolve()

        # パストラバーサルチェック
        if not str(full_path).startswith(str(self.base_path)):
            raise ValueError(
                f"Access denied: Path traversal detected for '{relative_path}'"
            )

        # 存在チェック
        if not full_path.exists():
            raise FileNotFoundError(
                f"File not found: {relative_path}"
            )

        # ファイルチェック（ディレクトリ読み込み防止）
        if not full_path.is_file():
            raise ValueError(
                f"Path is not a file: {relative_path}"
            )

        # サイズチェック
        if max_size is not None:
            file_size = full_path.stat().st_size
            if file_size > max_size:
                raise RuntimeError(
                    f"File too large: {file_size} bytes "
                    f"(max: {max_size} bytes)"
                )

        # ファイル読み込み
        try:
            async with aiofiles.open(full_path, 'r', encoding=encoding) as f:
                content = await f.read()
            return content
        except UnicodeDecodeError as e:
            raise RuntimeError(
                f"Failed to decode file with encoding '{encoding}': {e}"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to read file: {e}")

    def list_files(
        self,
        relative_dir: str = ".",
        pattern: str = "*"
    ) -> list[str]:
        """ディレクトリ内のファイルをリストアップ

        Args:
            relative_dir: 基準ディレクトリからの相対パス
            pattern: グロブパターン（例: "*.md", "*.txt"）

        Returns:
            ファイルパスのリスト（基準ディレクトリからの相対パス）

        Raises:
            ValueError: パストラバーサル攻撃を検出した場合
            FileNotFoundError: ディレクトリが存在しない場合
        """
        # 絶対パスを解決
        full_dir = (self.base_path / relative_dir).resolve()

        # パストラバーサルチェック
        if not str(full_dir).startswith(str(self.base_path)):
            raise ValueError(
                f"Access denied: Path traversal detected for '{relative_dir}'"
            )

        # 存在チェック
        if not full_dir.exists():
            raise FileNotFoundError(
                f"Directory not found: {relative_dir}"
            )

        if not full_dir.is_dir():
            raise ValueError(
                f"Path is not a directory: {relative_dir}"
            )

        # ファイルリスト取得
        files = []
        for file_path in full_dir.glob(pattern):
            if file_path.is_file():
                # 基準ディレクトリからの相対パスを計算
                rel_path = file_path.relative_to(self.base_path)
                files.append(str(rel_path))

        return sorted(files)
