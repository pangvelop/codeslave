from fastapi import FastAPI, Body
from agent import run_tools

app = FastAPI()

@app.post("/analyze")
def analyze_code(code: str = Body(..., embed=True)):
    return run_tools(code)
