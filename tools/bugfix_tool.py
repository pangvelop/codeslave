from tools.base_tool import BaseTool
from call_gpt import call_gpt

class BugFixTool(BaseTool):
    name = "BugFixTool"
    description = "코드에서 오류를 찾아 수정 제안을 합니다."

    def __call__(self, code: str) -> str:
        prompt = f"""
다음 Python 코드에서 오류가 있다면 찾고, 수정된 코드를 제안해줘:
```python
{code}
```"""
        return call_gpt(prompt)
