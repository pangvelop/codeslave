import re

from crawl import client


def remove_code_block_markers(text: str) -> str:
    text = re.sub(r'^```(?:\w+)?\n', '', text)
    text = re.sub(r'\n```$', '', text)
    return text


def convert_to_markdown(text):
    prompt = (
            "다음 텍스트에서 문맥상 필요없는 부분이나 읽기 어려운 부분, 그리고 javascript 등 코딩 코드를 제거하고 "
            "적절한 헤딩, 단락, 리스트 등을 사용하여 잘 구조화된 Markdown 문서를 만들어줘."
            "단, 마지막에 추가적인 요약이나 정리 멘트는 생략해줘:\n\n" + text
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # 필요에 따라 모델 변경 가능
        messages=[
            {"role": "system", "content": "너는 평문을 Markdown 형식으로 정제하는 전문가야. 응답은 마크다운 형식 그대로여야 해."},
            {"role": "user", "content": prompt}
        ]
    )
    markdown_text = response.choices[0].message.content
    return markdown_text
