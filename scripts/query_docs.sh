#!/bin/bash
# Amazon Q CLI と MCP サーバーを連携させるラッパースクリプト

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DOCS_DIR="$PROJECT_DIR/docs"

# 使用方法
usage() {
    echo "Usage: $0 <command> [args...]"
    echo ""
    echo "Commands:"
    echo "  list                  - ドキュメント一覧を表示"
    echo "  get <filename>        - ドキュメントを取得"
    echo "  search <file> <word>  - ドキュメント内を検索"
    echo ""
    echo "Examples:"
    echo "  $0 list"
    echo "  $0 get gundam_mobile_suits.md"
    echo "  $0 search gundam_mobile_suits.md ガンダム"
    exit 1
}

# コマンドチェック
if [ $# -lt 1 ]; then
    usage
fi

COMMAND=$1
shift

case $COMMAND in
    list)
        echo "📋 利用可能なドキュメント:"
        cd "$DOCS_DIR" && find . -name "*.md" -type f | sed 's|^\./||' | sort
        ;;

    get)
        if [ $# -lt 1 ]; then
            echo "Error: ファイル名を指定してください"
            usage
        fi
        FILENAME=$1
        FILEPATH="$DOCS_DIR/$FILENAME"

        if [ ! -f "$FILEPATH" ]; then
            echo "Error: ファイルが見つかりません: $FILENAME"
            exit 1
        fi

        echo "📄 ドキュメント: $FILENAME"
        echo "─────────────────────────────────────"
        cat "$FILEPATH"
        ;;

    search)
        if [ $# -lt 2 ]; then
            echo "Error: ファイル名とキーワードを指定してください"
            usage
        fi
        FILENAME=$1
        KEYWORD=$2
        FILEPATH="$DOCS_DIR/$FILENAME"

        if [ ! -f "$FILEPATH" ]; then
            echo "Error: ファイルが見つかりません: $FILENAME"
            exit 1
        fi

        echo "🔍 '$KEYWORD' の検索結果 in $FILENAME:"
        echo "─────────────────────────────────────"
        grep -n -i "$KEYWORD" "$FILEPATH" || echo "キーワードが見つかりませんでした"
        ;;

    *)
        echo "Error: 不明なコマンド: $COMMAND"
        usage
        ;;
esac
