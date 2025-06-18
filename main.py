from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import openai

openai.api_key = "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"
client = openai.OpenAI(api_key=openai.api_key)

# FastAPI app
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request, "result": None})

@app.post("/analyze-resume", response_class=HTMLResponse)
async def analyze_resume(
    request: Request,
    resume: UploadFile = File(...),
    jd_text: str = Form(...)
):
    import pdfplumber
    import io

    content = await resume.read()
    resume_text = ""

    try:
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            for page in pdf.pages:
                resume_text += page.extract_text() or ""
    except Exception:
        resume_text = content.decode("utf-8", errors="ignore")

    # Limit resume size to avoid token overflow
    trimmed_resume = resume_text[:15000]

    prompt = f"""
You are an intelligent hiring assistant.
Given the Job Description and the Resume below, do the following:

1. Evaluate how well the resume matches the job description.
2. List matched and missing skills.
3. Identify gaps or concerns.
4. Give a "Role Fit Score" (0–100).
5. Write a 3-line summary for the recruiter.

--- Job Description ---
{jd_text}

--- Resume ---
{trimmed_resume}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=700
        )
        result = response.choices[0].message.content
    except Exception as e:
        result = f"Error analyzing resume: {e}"

    return templates.TemplateResponse("dashboard.html", {"request": request, "result": result})
