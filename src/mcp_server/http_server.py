"""MCP Document Server - HTTP API wrapper"""

import os
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from mcp_server.tools.document import DocumentTools
from mcp_server.utils.logging import setup_logging

# ロギング設定
logger = setup_logging(__name__)

# FastAPI アプリ
app = FastAPI(
    title="MCP Document Server API",
    description="HTTP API for MCP Document Server",
    version="0.1.0"
)

# ドキュメントディレクトリ
DOCS_DIR = os.getenv("MCP_DOCS_DIR", str(Path.cwd() / "docs"))
Path(DOCS_DIR).mkdir(parents=True, exist_ok=True)

# DocumentTools インスタンス
doc_tools = DocumentTools(DOCS_DIR)
logger.info(f"HTTP Server initialized with docs directory: {DOCS_DIR}")


# リクエストモデル
class DocumentRequest(BaseModel):
    path: str
    encoding: str = "utf-8"


class ListRequest(BaseModel):
    directory: str = "."
    pattern: str = "*"


class SearchRequest(BaseModel):
    path: str
    keyword: str
    encoding: str = "utf-8"


# エンドポイント
@app.get("/")
async def root():
    """APIルート"""
    return {
        "name": "MCP Document Server API",
        "version": "0.1.0",
        "endpoints": {
            "list": "/api/list",
            "get": "/api/document",
            "search": "/api/search"
        }
    }


@app.get("/health")
async def health():
    """ヘルスチェック"""
    return {"status": "ok", "docs_dir": DOCS_DIR}


@app.post("/api/list")
async def list_documents(request: ListRequest):
    """ドキュメント一覧を取得"""
    try:
        files = doc_tools.list_documents(request.directory, request.pattern)
        return {"success": True, "files": files, "count": len(files)}
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/document")
async def get_document(request: DocumentRequest):
    """ドキュメントを取得"""
    try:
        content = await doc_tools.get_document(request.path, request.encoding)
        return {
            "success": True,
            "path": request.path,
            "content": content,
            "length": len(content)
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Document not found: {request.path}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/search")
async def search_in_document(request: SearchRequest):
    """ドキュメント内を検索"""
    try:
        result = await doc_tools.search_in_document(
            request.path,
            request.keyword,
            request.encoding
        )
        return {
            "success": True,
            "path": request.path,
            "keyword": request.keyword,
            "result": result
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Document not found: {request.path}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error searching document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    logger.info("=" * 60)
    logger.info("Starting MCP Document Server HTTP API")
    logger.info(f"Documents directory: {DOCS_DIR}")
    logger.info("=" * 60)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
