import streamlit as st
import datetime
import time
import os
import io
import re
import zipfile

from openai import OpenAI

from converter.fileToMarkdown import extract_text_from_file, split_text_with_overlap, convert_chunk_to_markdown
from converter.htmlToMarkdown import remove_code_block_markers, convert_to_markdown
from converter.txtTransformer import transform_level1_header
from crawler.crawler import get_rendered_html, extract_content
from utils.helpers import auto_download, remove_isolated_code_fences

# HWP 처리 관련 (olefile, hwp5html, html2text 등은 사용하지 않음)

client = OpenAI(api_key="OPENAI_API_KEY")
# openai.api_key = os.getenv("OPENAI_API_KEY")
###############################################
# 웹 크롤링 → Markdown 변환 관련 함수
###############################################


def process_url(url, target_class):
    html = get_rendered_html(url)
    content = extract_content(html, target_class, base_url=url)
    if not content:
        return None, None
    md_text = convert_to_markdown(content)
    md_text = remove_code_block_markers(md_text)

    header_line = None
    for line in md_text.splitlines():
        if line.strip().startswith("#"):
            header_line = line.strip()
            break
    if header_line:
        sanitized_header = re.sub(r'[\\/*?:"<>|]', "", header_line.lstrip("#").strip())
    else:
        sanitized_header = "converted_document"

    now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = f"{sanitized_header}_{now}.md"
    return file_name, md_text

###############################################
# 파일 → Markdown 변환 관련 함수
###############################################
# def extract_text_from_pdf(file):
#     file_bytes = file.read()
#     pdf_io = io.BytesIO(file_bytes)
#     text = ""
#     from pdfminer.layout import LAParams
#     laparams = LAParams(char_margin=2.0, line_margin=0.5, word_margin=0.1, boxes_flow=0.5)
#     with pdfplumber.open(pdf_io, laparams=laparams.__dict__) as pdf:
#         for page in pdf.pages:
#             page_text = page.extract_text()
#             if page_text:
#                 text += page_text + "\n"
#     return text


###############################################
# 통합 Streamlit 앱 메인 함수
###############################################
def main():
    st.title("통합 변환기")
    st.write("웹 크롤링, 파일 변환 및 Markdown → TXT 변환 기능을 제공합니다.")

    # 탭 순서: [Web Crawl, File to Markdown, HWP to HWPX 변환, Markdown to TXT 변환]
    tabs = st.tabs([
        "Web Crawl to Markdown",
        "File to Markdown",
        "Markdown to TXT 변환"
    ])

    # 1. Web Crawl to Markdown 탭
    with tabs[0]:
        st.header("웹 크롤링 → Markdown 변환")
        st.write(
            "여러 URL을 입력하고 (각 줄에 하나씩) 옵션으로 특정 클래스명을 지정하면, "
            "각 URL의 동적 페이지를 렌더링하여 텍스트와 <a>, <img> 등의 HTML 마크업을 그대로 추출한 후, "
            "OpenAI를 통해 Markdown으로 정제한 결과를 다운로드합니다."
        )
        urls_text = st.text_area("크롤링할 URL들을 입력하세요 (각 줄에 하나씩):", "https://example.com")
        target_class = st.text_input("특정 클래스명을 입력하세요 (옵션):", "")
        if st.button("문서 생성 (Web Crawl)"):
            urls = [line.strip() for line in urls_text.splitlines() if line.strip()]
            if not urls:
                st.error("적어도 하나의 URL을 입력하세요.")
            else:
                for url in urls:
                    st.info(f"처리 중: {url}")
                    try:
                        file_name, md_text = process_url(url, target_class.strip() if target_class.strip() else None)
                        if md_text is None:
                            st.warning(f"{url}에서 콘텐츠를 추출하지 못했습니다.")
                            continue
                        st.success(f"{url} -> 생성된 파일: {file_name}")
                        auto_download(md_text, file_name)
                        st.markdown("---")
                        time.sleep(1)
                    except Exception as e:
                        st.error(f"{url} 처리 중 오류 발생: {e}")

    # 2. File to Markdown 탭
    with tabs[1]:
        st.header("파일 → Markdown 변환")
        st.write(
            "PDF, HWP, HWPX, TXT, PPTX, XLSX 파일을 업로드하면 전체 텍스트를 추출하고 청크 단위로 분할한 후, "
            "각 청크를 OpenAI를 통해 Markdown 형식으로 정제합니다. "
            "파일별로 Markdown 및 TXT 다운로드 버튼과 전체 결과 ZIP 파일 다운로드 기능을 제공합니다.\n\n"
            "※ TXT 파일만 업로드한 경우 단순 합본 TXT 파일을 생성합니다."
        )
        overall_download_container = st.container()
        uploaded_files = st.file_uploader(
            "파일 업로드 (PDF, HWP, HWPX, TXT, PPTX, XLSX)",
            type=["pdf", "hwp", "hwpx", "txt", "pptx", "xlsx"],
            accept_multiple_files=True
        )
        if uploaded_files:
            all_txt = all(os.path.splitext(f.name)[1].lower() == ".txt" for f in uploaded_files)
            if all_txt:
                merged_text = ""
                for uploaded_file in uploaded_files:
                    st.write(f"### {uploaded_file.name} 파일 처리 중...")
                    with st.spinner("TXT 파일 내용 읽는 중..."):
                        content = extract_text_from_file(uploaded_file)
                    merged_text += content
                st.success("TXT 파일 합본 생성 완료!")
                st.download_button(
                    label="합본 TXT 파일 다운로드",
                    data=merged_text,
                    file_name="merged_text.txt",
                    mime="text/plain",
                    key="merged_txt_only"
                )
            else:
                results_md = []
                results_txt = []
                for uploaded_file in uploaded_files:
                    st.write(f"### 파일 처리 중: {uploaded_file.name}")
                    with st.spinner("파일에서 텍스트 추출 중..."):
                        full_text = extract_text_from_file(uploaded_file)
                    if not full_text:
                        st.error(f"{uploaded_file.name} 파일의 텍스트 추출에 실패했습니다.")
                        continue
                    chunks = split_text_with_overlap(full_text, chunk_size=1000, overlap=0)
                    st.info(f"{uploaded_file.name} - 총 청크 개수: {len(chunks)}")
                    refined_markdowns = []
                    previous_md = None
                    for idx, chunk in enumerate(chunks):
                        with st.spinner(f"{uploaded_file.name} - 청크 {idx + 1}/{len(chunks)} 처리 중..."):
                            md_chunk = convert_chunk_to_markdown(chunk, previous_md)
                            refined_markdowns.append(md_chunk)
                            previous_md = md_chunk
                        time.sleep(1)
                    final_markdown = "\n\n---\n\n".join(refined_markdowns)
                    final_markdown = remove_isolated_code_fences(final_markdown)
                    base_name = os.path.splitext(uploaded_file.name)[0]
                    md_file_name = f"{base_name}.md"
                    results_md.append((md_file_name, final_markdown))
                    st.success(f"{uploaded_file.name} Markdown 문서 생성 완료: {md_file_name}")
                    st.code(final_markdown, language="markdown")
                    st.download_button(
                        label=f"{md_file_name} 다운로드",
                        data=final_markdown,
                        file_name=md_file_name,
                        mime="text/markdown",
                        key=f"md_{base_name}"
                    )
                    transformed_txt = transform_level1_header(final_markdown)
                    txt_file_name = f"{base_name}.txt"
                    results_txt.append((txt_file_name, transformed_txt))
                    st.download_button(
                        label=f"{txt_file_name} 다운로드 (TXT)",
                        data=transformed_txt,
                        file_name=txt_file_name,
                        mime="text/plain",
                        key=f"txt_{base_name}"
                    )
                    st.markdown("---")
                if results_md:
                    zip_buffer_md = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer_md, "w") as zf:
                        for fname, md_content in results_md:
                            zf.writestr(fname, md_content)
                    zip_buffer_md.seek(0)
                else:
                    zip_buffer_md = None
                if results_txt:
                    merged_txt = "".join(
                        [f"\n{txt_content}" for fname, txt_content in results_txt]
                    )
                    zip_buffer_txt = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer_txt, "w") as zf:
                        for fname, txt_content in results_txt:
                            zf.writestr(fname, txt_content)
                    zip_buffer_txt.seek(0)
                else:
                    zip_buffer_txt = None
                    merged_txt = ""
                with overall_download_container:
                    cols = st.columns([4, 2])
                    with cols[1]:
                        if zip_buffer_md:
                            st.download_button(
                                label="모든 Markdown 파일 ZIP 다운로드",
                                data=zip_buffer_md,
                                file_name="converted_markdown_files.zip",
                                mime="application/zip",
                                key="overall_zip_md"
                            )
                        if zip_buffer_txt:
                            st.download_button(
                                label="모든 TXT 파일 ZIP 다운로드",
                                data=zip_buffer_txt,
                                file_name="converted_txt_files.zip",
                                mime="application/zip",
                                key="overall_zip_txt"
                            )
                        if merged_txt:
                            st.download_button(
                                label="모든 TXT 병합 파일 다운로드",
                                data=merged_txt,
                                file_name="merged_txt.txt",
                                mime="text/plain",
                                key="merged_txt"
                            )


    # 4. Markdown → TXT 변환 탭
    with tabs[2]:
        st.header("Markdown → TXT 변환")
        st.write("업로드한 Markdown(.md) 파일에서 레벨 1 헤더(#)를 '@!@'로 치환하여 텍스트(.txt) 파일로 변환합니다.")
        uploaded_md_files = st.file_uploader("Markdown 파일 업로드", type=["md"], accept_multiple_files=True)
        if uploaded_md_files:
            results = []
            for uploaded_file in uploaded_md_files:
                st.write(f"### 처리 중: {uploaded_file.name}")
                try:
                    md_content = uploaded_file.read().decode("utf-8")
                except Exception as e:
                    st.error(f"{uploaded_file.name} 파일 읽기 오류: {e}")
                    continue
                transformed_content = transform_level1_header(md_content)
                base_name = os.path.splitext(uploaded_file.name)[0]
                file_name = f"{base_name}.txt"
                results.append((file_name, transformed_content))
                st.success(f"{uploaded_file.name} → {file_name} 변환 완료")
                st.download_button(
                    label=f"{file_name} 다운로드",
                    data=transformed_content,
                    file_name=file_name,
                    mime="text/plain"
                )
                st.code(transformed_content, language="plaintext")
                st.markdown("---")
            if len(results) > 1:
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                    for fname, content in results:
                        zip_file.writestr(fname, content)
                zip_buffer.seek(0)
                st.download_button(
                    label="모든 TXT 파일 ZIP 다운로드",
                    data=zip_buffer,
                    file_name="converted_txt_files.zip",
                    mime="application/zip"
                )

if __name__ == "__main__":
    main()
