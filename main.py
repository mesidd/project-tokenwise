import os
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

load_dotenv()

app = FastAPI(
  title = "Project TokenWise Backend",
  description = "Backend server for the TokenWise application, managing AI model interactions.",
  version = "0.1.0"
)

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
  raise ValueError("GOOGLE_API_KEY environment variable not set!")
genai.configure(api_key = api_key)

app.add_middleware(
  CORSMiddleware,
  allow_origins = ['http://localhost:3000'],
  allow_credentials = True,
  allow_methods = ["*"],
  allow_headers = ["*"]
)

class ChatMessage(BaseModel):
  role: str
  content:str

class ChatRequest(BaseModel):
  messages: List[ChatMessage]

def format_gemini_history(messages: List[ChatMessage]):
  history = []
  for msg in messages[:-1]:
    history.append({"role": msg.role, "parts": [{"text": msg.content}]})
  return history

@app.get("/health")
def health_check():
  return {"status": "ok"}

@app.post("/chat/naive")
async def chat_naive(request: ChatRequest):
  try:
    user_prompt = request.messages[-1].content
    history = format_gemini_history(request.messages)
    model = genai.GenerativeModel('gemini-2.5-flash')
    chat = model.start_chat(history = history)

    async def stream_generator():
      def on_stream(chunk):
        yield f"data: {chunk.text}\n\n"

      for token in chat.send_message(user_prompt, stream=True):
        if token.text:
          yield f"data: {token.text}\n\n"

    return StreamingResponse(stream_generator(), media_type = "text/event-stream")
  except Exception as e:
    print(f"An error occured : {e}")
    return {"error": "An internal error occured."}