from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any
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

# 1. 파일 크롤링 엔드포인트
@app.post("/api/crawl")
async def crawl_url(url: str = Form(...)):
    """
    웹 페이지 크롤링을 수행하는 엔드포인트
    """
    try:
        # await 제거
        html_content = get_rendered_html(url)
        extracted_content = extract_content(html_content)
        return {"content": extracted_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"크롤링 실패: {str(e)}")

# 2. 문서 변환 엔드포인트
@app.post("/api/convert")
async def convert_document(
    file: UploadFile = File(...),
    format: str = Form(default="markdown")
):
    """
    업로드된 문서를 지정된 형식으로 변환
    """
    try:
        content = await file.read()
        text = extract_text_from_file(content)
        
        if format == "markdown":
            converted = convert_to_markdown(text)
        else:
            raise HTTPException(status_code=400, detail="지원하지 않는 변환 형식입니다")
        
        return {"converted_content": converted}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"변환 실패: {str(e)}")

# 3. 코드 분석 엔드포인트
@app.post("/api/analyze")
async def analyze_code(
    code: str = Form(...),
    analysis_type: str = Form(default="all")
):
    """
    코드 분석을 수행하는 엔드포인트
    """
    try:
        response = await client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "코드 분석을 수행하는 전문가입니다."},
                {"role": "user", "content": f"다음 코드를 분석해주세요: \n\n{code}"}
            ]
        )
        return {"analysis": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 실패: {str(e)}")

# 4. 코드 수정 엔드포인트
@app.post("/api/refactor")
async def refactor_code(
    code: str = Form(...),
    instructions: Optional[str] = Form(None)
):
    """
    코드 수정을 수행하는 엔드포인트
    """
    try:
        prompt = f"다음 코드를 개선해주세요: \n\n{code}"
        if instructions:
            prompt += f"\n\n수정 지침: {instructions}"
            
        response = await client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "코드 리팩토링을 수행하는 전문가입니다."},
                {"role": "user", "content": prompt}
            ]
        )
        return {"refactored_code": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"수정 실패: {str(e)}")

# 에러 핸들링
@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    return {"error": str(exc)}, 500

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)