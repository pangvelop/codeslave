from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# API 키가 없을 경우 기본값 설정
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인해주세요.")

try:
    client = OpenAI(api_key=api_key)
except Exception as e:
    raise Exception(f"OpenAI 클라이언트 초기화 실패: {e}")