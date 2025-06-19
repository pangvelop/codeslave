from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 새로운 import 구문 추가
from utils import (
    client,
    auto_download,
    remove_isolated_code_fences,
    fill_missing_cells,
    remove_code_fence
)

from converter import (
    convert_to_markdown,
    remove_code_block_markers,
    extract_text_from_file,
    split_text_with_overlap,
    convert_chunk_to_markdown,
    transform_level1_header
)

from crawler import get_rendered_html, extract_content

app = FastAPI(title="문서 변환 API")

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 에러 핸들링
@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    return {"error": str(exc)}, 500

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)