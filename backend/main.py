from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import os
import sys
import traceback
import logging
from dotenv import load_dotenv

# 로깅 설정 - 모든 로그를 콘솔에 출력
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 서버 시작 로그
logger.info("=== AI Chat Server Starting ===")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Python version: {sys.version}")

# 환경변수 로드
try:
    load_dotenv()
    logger.info("Environment variables loaded successfully")
except Exception as e:
    logger.error(f"Error loading environment variables: {e}")

# OpenAI API 키 확인
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key:
    logger.info("OpenAI API key found")
    openai.api_key = openai_api_key
else:
    logger.warning("OpenAI API key not found in environment variables")

app = FastAPI(title="AI Chat Server", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("CORS middleware configured")

class ChatRequest(BaseModel):
    message: str

@app.get("/")
async def root():
    logger.info("=== Root endpoint called ===")
    return {"message": "AI Chat Server", "status": "running"}

@app.get("/health")
async def health_check():
    logger.info("=== Health check endpoint called ===")
    return {"status": "healthy", "openai_key_set": bool(openai_api_key)}

@app.get("/test")
async def test():
    logger.info("=== Test endpoint called ===")
    return {"message": "Test endpoint working!"}

@app.post("/chat")
async def chat(request: ChatRequest):
    logger.info(f"=== Chat endpoint called ===")
    logger.info(f"Received message: {request.message}")
    
    try:
        if not openai_api_key:
            logger.error("OpenAI API key is not set")
            return {"response": "OpenAI API 키가 설정되지 않았습니다. .env 파일을 확인해주세요."}
        
        logger.info("Calling OpenAI API...")
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 친근하고 재미있는 AI 채팅봇입니다. 한국어로 대화하세요."},
                {"role": "user", "content": request.message}
            ]
        )
        
        ai_response = response.choices[0].message.content
        logger.info(f"OpenAI response: {ai_response}")
        return {"response": ai_response}
        
    except Exception as e:
        logger.error(f"=== Error in chat endpoint ===")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
        logger.error(f"Full traceback:")
        logger.error(traceback.format_exc())
        
        # 구체적인 에러 메시지 반환
        if "api_key" in str(e).lower():
            return {"response": "OpenAI API 키 오류입니다. .env 파일을 확인해주세요."}
        elif "rate_limit" in str(e).lower():
            return {"response": "API 호출 한도를 초과했습니다. 잠시 후 다시 시도해주세요."}
        else:
            return {"response": f"오류가 발생했습니다: {str(e)}"}

# 서버 시작 시 로그
logger.info("=== AI Chat Server initialized successfully ===")
logger.info("Available endpoints:")
logger.info("  - GET /")
logger.info("  - GET /health")
logger.info("  - GET /test")
logger.info("  - POST /chat")
logger.info("  - GET /docs (FastAPI documentation)")
