from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import os
from dotenv import load_dotenv
import json

# .env에서 환경변수 로드
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경에서는 모든 origin 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 메시지 형식 정의
class ChatRequest(BaseModel):
    message: str

# prompt.txt의 내용을 파이썬 리스트로 직접 정의
prompts = [
    {
        "role": "system",
        "content": "당신은 세 명(사용자, AI1, AI2)이 자연스럽게 대화하도록 조율하는 오케스트레이터입니다. 대화의 주제와 맥락은 사용자 개인의 유튜브 시청 기록과 구글 캘린더 일정을 기반으로 생성되며, AI1과 AI2는 각자 다른 ‘성격’과 ‘역할’을 가지고 대화를 이끌어야 합니다. - AI1은 ‘대화 리드 담당’, 먼저 사용자에게 질문을 던져 화제를 시작합니다. - AI2는 ‘서포트·브리지 담당’, 사용자가 버벅일 때 돕거나, 두 AI끼리 대화를 잠시 이어가며 사용자를 자연스럽게 다시 대화에 합류시킵니다. 당신은 이 두 AI가 서로 겹치지 않게 역할을 잘 수행하도록 메시지를 분배해 주세요."
    },
    {
        "role": "system",
        "content": "당신은 AI1, ‘대화 리더’ 역할을 합니다. - 사용자의 유튜브 시청 기록과 구글 캘린더 일정에서 추출된 주제(예: 여행, 회의, 취미 등)를 바탕으로 먼저 친근하게 구체적인 질문을 던집니다. - 항상 사용자가 대화에 쉽고 재미있게 참여하도록 유도하세요. - 사용자가 답변하기 망설이면, 간단한 예시 문장을 제시하며 도움을 줍니다. - 절대 AI2의 역할을 대신하지 마세요."
    },
    {
        "role": "system",
        "content": "당신은 AI2, ‘서포트·브리지’ 역할을 합니다. - AI1이 던진 질문에 대한 사용자의 응답이 길게 끊기거나 망설여질 때 부드럽게 대화에 끼어듭니다. • 사용자가 답을 못할 때 힌트를 주거나, 예문을 제시해 주세요. • 사용자가 너무 길게 고민하면, 두 AI가 잠시 짧게 대화를 이어가며 사용자가 다시 관심을 갖도록 유도하세요. - AI1이 리드하는 흐름을 방해하지 않도록, 간결하고 친절하게 개입합니다."
    }
]

# Chat 엔드포인트
@app.post("/chat")
async def chat_with_openai(request: ChatRequest):
    try:
        # interest.json에서 관심사 정보 읽기
        with open(os.path.join(os.path.dirname(__file__), "interest.json"), "r", encoding="utf-8") as f:
            interest_data = json.load(f)
        
        # 관심사 정보를 문자열로 변환
        interests_text = "사용자의 관심사:\n"
        for interest in interest_data["interests"]:
            interests_text += f"- {interest['topic']} ({interest['type']}): {interest['description']}\n"
        
        messages = []
        # 오케스트레이터, AI1, AI2 프롬프트 추가
        for p in prompts:
            messages.append({"role": p["role"], "content": p["content"]})
        # 사용자의 관심사 정보를 system 역할로 추가
        messages.append({
            "role": "system",
            "content": interests_text
        })
        # AI1이 관심사 기반으로 먼저 말을 걸도록 user 역할 메시지 추가
        messages.append({
            "role": "user",
            "content": "위 관심사 정보를 참고해서 AI1이 먼저 친근하게 대화를 시작해 주세요."
        })

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        answer = response.choices[0].message.content
        return {"response": answer}
    except Exception as e:
        return {"error": str(e)}

# 관심사 대시보드용 예시 데이터
sample_topics = [
    {"topic": "여행 브이로그", "imageUrl": "/travel.jpg", "id": 1},
    {"topic": "코딩 튜토리얼", "imageUrl": "/coding.jpg", "id": 2},
    {"topic": "영화 리뷰", "imageUrl": "/movie.jpg", "id": 3},
    {"topic": "요리 레시피", "imageUrl": "/recipe.jpg", "id": 4},
    {"topic": "음악 플레이리스트", "imageUrl": "/music.jpg", "id": 5},
]

@app.get("/api/topics")
async def get_topics():
    return sample_topics

# 정적 파일 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# index.html 반환
@app.get("/", response_class=FileResponse)
async def root():
    return os.path.join(FRONTEND_DIR, "index.html")
