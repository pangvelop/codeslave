from tools.intent_tool import CodeIntentTool
from tools.bugfix_tool import BugFixTool
from tools.refactor_tool import RefactorSuggestionTool

TOOLS = [
    CodeIntentTool(),
    BugFixTool(),
    RefactorSuggestionTool()
]

def run_tools(code: str):
    result = {}
    for tool in TOOLS:
        try:
            result[tool.name] = tool(code)
        except Exception as e:
            result[tool.name] = f"⚠️ 에러: {e}"
    return result
