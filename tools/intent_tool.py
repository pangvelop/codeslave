from tools.base_tool import BaseTool
from call_gpt import call_gpt

class CodeIntentTool(BaseTool):
    name = "CodeIntentTool"
    description = "코드의 의도와 목적을 설명합니다."

    def __call__(self, code: str) -> str:
        prompt = f"""
다음 Python 코드가 어떤 목적과 동작을 갖는지 설명해줘:
```python
{code}
```"""
        return call_gpt(prompt)
