import requests
from bs4 import BeautifulSoup

def get_rendered_html(url: str) -> str:
    """
    웹 페이지의 HTML 내용을 가져옵니다
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # 오류 발생시 예외 발생
        return response.text
    except requests.RequestException as e:
        raise Exception(f"페이지 로딩 실패: {str(e)}")

def extract_content(html: str) -> str:
    """
    HTML에서 의미 있는 콘텐츠를 추출합니다
    """
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # 불필요한 요소 제거
        for tag in soup.find_all(['script', 'style']):
            tag.decompose()
            
        # 본문 내용 추출
        text = soup.get_text(separator='\n', strip=True)
        
        # 빈 줄 정리
        text = '\n'.join(line for line in text.split('\n') if line.strip())
        
        return text
    except Exception as e:
        raise Exception(f"콘텐츠 추출 실패: {str(e)}")