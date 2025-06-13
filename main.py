from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from crawler.crawler import get_rendered_html, extract_content
from converter.htmlToMarkdown import convert_to_markdown, remove_code_block_markers
from converter.fileToMarkdown import extract_text_from_file, split_text_with_overlap, convert_chunk_to_markdown
from converter.txtTransformer import transform_level1_header
from utils.helpers import remove_isolated_code_fences
import re, datetime, io, zipfile

app = FastAPI()

@app.post("/crawl")
async def api_crawl(url: str = Form(...), target_class: str = Form(None)):
    html = get_rendered_html(url)
    content = extract_content(html, target_class, base_url=url)
    if not content:
        raise HTTPException(404, "No content extracted")
    md = convert_to_markdown(content)
    md = remove_code_block_markers(md)
    return {"md_text": md}

@app.post("/upload-file")
async def api_upload(file: UploadFile = File(...)):
    text = await file.read()
    full = extract_text_from_file(io.BytesIO(text))
    chunks = split_text_with_overlap(full, chunk_size=1000, overlap=0)
    md = ""
    prev = None
    for chunk in chunks:
        m = convert_chunk_to_markdown(chunk, prev)
        md += m + "\n\n---\n\n"
        prev = m
    md = remove_isolated_code_fences(md)
    return {"md_text": md}

@app.post("/upload-txt")
async def api_txt(file: UploadFile = File(...)):
    text = await file.read()
    txt = transform_level1_header(text.decode("utf-8"))
    return StreamingResponse(io.StringIO(txt), media_type="text/plain")

@app.post("/download-zip")
async def api_zip(file: UploadFile = File(...)):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("output.md", (await file.read()))
    buf.seek(0)
    return StreamingResponse(buf, media_type="application/zip",
                             headers={"Content-Disposition":"attachment; filename=output.zip"})
