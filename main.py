from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(
  title = "Project Tokenwise Backend",
  description = "Backend server for the TokenWise application, managing AI model interactions.",
  version = '0.1.0'
)

@app.get("/")
def read_root():
  return {"message": "Welcome to the TokenWIse Backend!"}


@app.get("/health")
def health_check():
  return JSONResponse(content = {"status": "ok"})