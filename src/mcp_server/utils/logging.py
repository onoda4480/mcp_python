"""STDIO安全なロギング設定"""

import logging
import sys
from pathlib import Path


def setup_logging(name: str, level: int = logging.INFO) -> logging.Logger:
    """STDIO通信に安全なロギングを設定

    Args:
        name: ロガー名
        level: ログレベル

    Returns:
        設定済みロガー

    Note:
        STDIO通信ではstdoutに書き込むとJSON-RPCメッセージが壊れるため、
        stderrとファイルのみに出力します。
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 既存のハンドラをクリア（重複防止）
    logger.handlers.clear()

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # stderr handler（STDIO安全）
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.DEBUG)
    stderr_handler.setFormatter(formatter)
    logger.addHandler(stderr_handler)

    # File handler（永続化用）
    log_dir = Path.home() / '.mcp' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f'{name}.log'

    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 親ロガーへの伝播を防止（重複ログ防止）
    logger.propagate = False

    return logger
