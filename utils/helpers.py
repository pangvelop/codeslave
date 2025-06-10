import base64
import re

import streamlit as st


def auto_download(markdown_text, file_name):
    b64 = base64.b64encode(markdown_text.encode()).decode()
    download_html = f"""
    <html>
      <body>
        <a id="downloadLink" href="data:text/markdown;base64,{b64}" download="{file_name}" style="display:none">Download</a>
        <script>document.getElementById('downloadLink').click();</script>
      </body>
    </html>
    """
    st.components.v1.html(download_html, height=0)


def fill_missing_cells(table):
    """
    리스트 형태의 테이블(리스트의 리스트)에서, 각 셀의 값이 None 또는 빈 문자열인 경우,
    바로 위 행의 같은 열 값을 채워 넣는 방식으로 보완합니다.
    단, 첫 번째 행(헤더)는 건드리지 않습니다.
    """
    if not table or len(table) < 2:
        return table
    # 첫 번째 행은 헤더로 가정
    for i in range(1, len(table)):
        row = table[i]
        for j in range(len(row)):
            if row[j] in [None, ""]:
                # 바로 위 행에서 값이 있으면 가져오기
                row[j] = table[i - 1][j] if table[i - 1][j] not in [None, ""] else ""
    return table


def remove_code_fence(markdown_text):
    markdown_text = markdown_text.strip()
    if markdown_text.startswith("```"):
        lines = markdown_text.splitlines()
        if lines[0].startswith("```"):
            if lines[-1].strip().startswith("```"):
                markdown_text = "\n".join(lines[1:-1]).strip()
            else:
                markdown_text = "\n".join(lines[1:]).strip()
    return markdown_text


def remove_isolated_code_fences(text):
    return re.sub(r"(?m)^\s*```(markdown)?\s*$", "", text)
