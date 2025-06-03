from tools.base_tool import BaseTool
from call_gpt import call_gpt

class RefactorSuggestionTool(BaseTool):
    name = "RefactorSuggestionTool"
    description = "더 깔끔하고 효율적인 코드로 리팩토링하는 방법을 제안합니다."

    def __call__(self, code: str) -> str:
        prompt = f"""
다음 Python 코드를 리팩토링해서 더 효율적이고 읽기 좋게 만들어줘:
```python
{code}
```"""
        return call_gpt(prompt)
