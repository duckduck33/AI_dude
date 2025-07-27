from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import google.generativeai as genai
import os
import sys
import traceback
import logging
import json
from dotenv import load_dotenv
from prompts import AI1_SYSTEM_PROMPT, AI2_SYSTEM_PROMPT, INITIAL_GREETING_PROMPT, CONVERSATION_PROMPT, TOM_SYSTEM_PROMPT
from keyword_compression import KeywordCompressor
from conversation_logic import conversation_logic

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

# 기본 OpenAI API 키 (환경변수에서)
default_openai_api_key = os.getenv("OPENAI_API_KEY")
if default_openai_api_key:
    logger.info("Default OpenAI API key found in environment")
else:
    logger.warning("No default OpenAI API key found in environment")

# Gemini API 초기화
gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')
    logger.info("Gemini API configured successfully")
else:
    logger.warning("No Gemini API key found in environment")
    gemini_model = None

# 시청기록 데이터 로드
def load_viewing_history():
    try:
        with open('data/viewing_history.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.info("Viewing history loaded successfully")
            return data
    except Exception as e:
        logger.error(f"Error loading viewing history: {e}")
        return None

viewing_history_data = load_viewing_history()

# 통합 대화 히스토리 저장소 (메모리 기반)
conversation_history = {
    "full_conversation": []  # 전체 대화를 순서대로 저장
}

# 압축 시스템 초기화
keyword_compressor = KeywordCompressor()

def add_to_history(speaker: str, message: str, user_message: str = None):
    """대화 히스토리에 메시지 추가 (순서대로)"""
    if user_message:
        conversation_history["full_conversation"].append({
            "role": "user",
            "content": user_message
        })
    
    conversation_history["full_conversation"].append({
        "role": "assistant",
        "speaker": speaker,
        "content": message
    })

def get_recent_context(max_messages: int = 50):
    """최근 대화 맥락 가져오기 (전체 대화) - 30분 대화 지원"""
    return conversation_history["full_conversation"][-max_messages:] if conversation_history["full_conversation"] else []

def clear_history():
    """대화 히스토리 초기화"""
    conversation_history["full_conversation"].clear()

def compress_history():
    """대화 히스토리 스마트 압축 (중요한 대화는 유지)"""
    if len(conversation_history["full_conversation"]) > 100:
        # 최근 30개는 유지, 나머지는 요약
        recent_30 = conversation_history["full_conversation"][-30:]
        older_messages = conversation_history["full_conversation"][:-30]
        
        # 요약 생성 (간단한 버전)
        summary = f"이전 대화 요약: {len(older_messages)}개의 메시지가 있었습니다."
        
        conversation_history["full_conversation"] = [
            {"role": "system", "content": summary}
        ] + recent_30

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
    api_key: str = None

class InitialGreetingRequest(BaseModel):
    api_key: str = None

@app.get("/")
async def root():
    logger.info("=== Root endpoint called ===")
    return {"message": "AI Chat Server", "status": "running"}

@app.get("/health")
async def health_check():
    logger.info("=== Health check endpoint called ===")
    return {"status": "healthy", "default_openai_key_set": bool(default_openai_api_key)}

@app.get("/test")
async def test():
    logger.info("=== Test endpoint called ===")
    return {"message": "Test endpoint working!"}

@app.get("/viewing-history")
async def get_viewing_history():
    logger.info("=== Viewing history endpoint called ===")
    if viewing_history_data:
        return viewing_history_data
    else:
        return {"error": "Viewing history not available"}

@app.post("/clear-conversation")
async def clear_conversation():
    """대화 히스토리 초기화"""
    logger.info("=== Clear conversation endpoint called ===")
    clear_history()
    return {"message": "대화 히스토리가 초기화되었습니다."}

@app.get("/conversation-history")
async def get_conversation_history():
    """현재 대화 히스토리 조회"""
    logger.info("=== Conversation history endpoint called ===")
    return {
        "full_conversation": conversation_history["full_conversation"]
    }

@app.post("/initial-greeting")
async def initial_greeting(request: InitialGreetingRequest):
    logger.info("=== Initial greeting endpoint called ===")
    
    # API 키 결정
    api_key_to_use = request.api_key if request.api_key else default_openai_api_key
    
    try:
        if not api_key_to_use:
            logger.error("No OpenAI API key available")
            return {"response": "OpenAI API 키가 설정되지 않았습니다."}
        
        logger.info("Setting OpenAI API key...")
        openai.api_key = api_key_to_use
        
        # 시청기록 기반 첫 인사 생성 (AI1이 담당)
        if viewing_history_data:
            top_interests = viewing_history_data.get('top_interests', [])
            favorite_category = viewing_history_data.get('favorite_category', '')
            recent_videos = viewing_history_data.get('viewing_history', [])[:3]
            
            viewing_history_info = f"""
- 주요 관심사: {', '.join(top_interests)}
- 가장 좋아하는 카테고리: {favorite_category}
- 최근 시청 영상: {', '.join([video['title'] for video in recent_videos])}
            """
            
            system_prompt = INITIAL_GREETING_PROMPT.format(viewing_history_info=viewing_history_info)
        else:
            system_prompt = "당신은 AI DUDE의 대화 주도자 Jinny입니다. (여성) 사용자에게 자연스럽게 인사해주세요. 반드시 메시지 앞에 '👩 Jinny:'를 붙여서 화자를 명시하세요. 절대 'AI1:'이나 다른 이름을 사용하지 마세요."
        
        logger.info("Calling OpenAI API for initial greeting...")
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "안녕하세요"}
            ]
        )
        
        ai_response = response.choices[0].message.content
        logger.info(f"OpenAI initial greeting: {ai_response}")
        return {"response": ai_response}
        
    except Exception as e:
        logger.error(f"=== Error in initial greeting endpoint ===")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
        logger.error(f"Full traceback:")
        logger.error(traceback.format_exc())
        
        return {"response": "안녕하세요! 저는 AI DUDE입니다. 무엇이든 물어보세요!"}

@app.post("/initial-greeting-2person")
async def initial_greeting_2person(request: InitialGreetingRequest):
    """2인 관심사 기반 대화 초기 인사"""
    logger.info("=== 2-person initial greeting endpoint called ===")
    
    try:
        if not gemini_model:
            logger.error("No Gemini API available")
            return {"response": "Gemini API가 설정되지 않았습니다."}
        
        # 시청기록 기반 첫 인사 생성
        if viewing_history_data:
            top_interests = viewing_history_data.get('top_interests', [])
            favorite_category = viewing_history_data.get('favorite_category', '')
            recent_videos = viewing_history_data.get('viewing_history', [])[:3]
            
            viewing_history_info = f"""
- 주요 관심사: {', '.join(top_interests)}
- 가장 좋아하는 카테고리: {favorite_category}
- 최근 시청 영상: {', '.join([video['title'] for video in recent_videos])}
            """
            
            system_prompt = f"""당신은 AI DUDE의 친근한 영어 대화 파트너입니다.

사용자의 유튜브 시청기록을 분석한 결과를 바탕으로 사용자에게 인사해주세요.

**시청기록 정보:**
{viewing_history_info}

**첫 인사 요구사항:**
1. 사용자에게 친근하게 인사해주세요
2. 구체적인 콘텐츠(예: "나는솔로")를 언급하세요
3. 모든 대화는 영어로 진행하되, 한국어 설명을 포함하세요
4. 친근하고 호기심 많은 톤으로 대화하세요
5. 메시지 앞에 "🤖 AI:"를 붙여서 화자를 명시하세요

**예시:**
"🤖 AI: Hello! I'm your AI conversation partner! (안녕하세요! 저는 당신의 AI 대화 파트너예요!) I noticed you love watching dating shows like 'I'm Solo'! (당신이 '나는솔로' 같은 연애 프로그램을 좋아한다는 걸 알아냈어요!) Which couple impressed you the most? (어떤 커플이 가장 인상적이었나요?)"
"""
        else:
            system_prompt = "당신은 AI DUDE의 친근한 영어 대화 파트너입니다. 사용자에게 자연스럽게 인사해주세요. 메시지 앞에 '🤖 AI:'를 붙여서 화자를 명시하세요."
        
        logger.info("Calling Gemini API for 2-person initial greeting...")
        response = gemini_model.generate_content(
            f"{system_prompt}\n\n사용자: 안녕하세요\n\nAI:"
        )
        
        ai_response = response.text
        logger.info(f"Gemini 2-person initial greeting: {ai_response}")
        return {"response": ai_response}
        
    except Exception as e:
        logger.error(f"=== Error in 2-person initial greeting endpoint ===")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
        logger.error(f"Full traceback:")
        logger.error(traceback.format_exc())
        
        return {"response": "안녕하세요! 저는 AI DUDE입니다. 무엇이든 물어보세요!"}

@app.post("/chat")
async def chat(request: ChatRequest):
    logger.info(f"=== Chat endpoint called ===")
    logger.info(f"Received message: {request.message}")
    
    # API 키 결정 (프론트엔드에서 받은 키 우선, 없으면 환경변수)
    api_key_to_use = request.api_key if request.api_key else default_openai_api_key
    
    try:
        if not api_key_to_use:
            logger.error("No OpenAI API key available")
            return {"response": "OpenAI API 키가 설정되지 않았습니다. 프론트엔드에서 API 키를 입력해주세요."}
        
        if not gemini_model:
            logger.error("No Gemini API available")
            return {"response": "Gemini API가 설정되지 않았습니다."}
        
        logger.info("Setting OpenAI API key...")
        openai.api_key = api_key_to_use
        
        # 시청기록 정보 준비
        if viewing_history_data:
            top_interests = viewing_history_data.get('top_interests', [])
            favorite_category = viewing_history_data.get('favorite_category', '')
            recent_videos = viewing_history_data.get('viewing_history', [])[:3]
            
            viewing_history_info = f"""
- 주요 관심사: {', '.join(top_interests)}
- 가장 좋아하는 카테고리: {favorite_category}
- 최근 시청 영상: {', '.join([video['title'] for video in recent_videos])}
            """
        else:
            viewing_history_info = "시청기록 정보가 없습니다."
        
        # Jinny (OpenAI) 먼저 응답
        logger.info("Calling OpenAI API for Jinny...")
        jinny_system_prompt = f"""{AI1_SYSTEM_PROMPT}

시청기록 정보:
{viewing_history_info}

Jinny가 사용자에게만 응답하세요. Tom에게 말을 걸지 마세요. 메시지 앞에 "👩 Jinny:"를 붙여서 화자를 명시하세요."""
        
        # Jinny 대화 히스토리 준비
        jinny_messages = [{"role": "system", "content": jinny_system_prompt}]
        
        # 압축된 대화 맥락 사용
        compressed_data = keyword_compressor.compress_conversation(
            conversation_history["full_conversation"], 
            keep_recent=8
        )
        
        # 시스템 프롬프트 + 압축된 맥락
        jinny_messages = [{"role": "system", "content": jinny_system_prompt}]
        
        # 압축된 맥락 추가
        if compressed_data["compressed_context"] != "대화가 시작되었습니다.":
            jinny_messages.append({
                "role": "system", 
                "content": f"이전 대화 맥락: {compressed_data['compressed_context']}"
            })
        
        # 최근 메시지 추가
        for msg in compressed_data["recent_messages"]:
            if msg["role"] == "user":
                jinny_messages.append({"role": "user", "content": msg["content"]})
            elif msg["role"] == "assistant":
                jinny_messages.append({"role": "assistant", "content": msg["content"]})
        
        # 현재 사용자 메시지 추가
        jinny_messages.append({"role": "user", "content": request.message})
        
        jinny_response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=jinny_messages
        )
        
        jinny_message = jinny_response.choices[0].message.content
        logger.info(f"Jinny response: {jinny_message}")
        
        # Tom (Gemini) 독립적 응답
        logger.info("Calling Gemini API for Tom...")
        tom_system_prompt = TOM_SYSTEM_PROMPT.format(viewing_history_info=viewing_history_info)
        
        # Tom 대화 히스토리 준비 (전체 대화 맥락)
        recent_context = get_recent_context(50)
        tom_context_text = ""
        if recent_context:
            context_messages = []
            for ctx in recent_context:
                if ctx["role"] == "user":
                    context_messages.append(f"사용자: {ctx['content']}")
                elif ctx["role"] == "assistant":
                    speaker = ctx.get("speaker", "AI")
                    context_messages.append(f"{speaker}: {ctx['content']}")
            tom_context_text = "\n\n최근 대화 맥락:\n" + "\n".join(context_messages)
        
        tom_response = gemini_model.generate_content(
            f"{tom_system_prompt}{tom_context_text}\n\n사용자 메시지: {request.message}\n\nTom이 사용자에게 독립적으로 응답하세요. Jinny의 응답을 참고하되, 별도의 메시지로 작성하세요. 메시지 앞에 '👨 Tom:'을 붙여서 화자를 명시하세요."
        )
        
        tom_message = tom_response.text
        logger.info(f"Tom response: {tom_message}")
        
        # 대화 히스토리에 저장
        add_to_history("jinny", jinny_message, request.message)
        add_to_history("tom", tom_message, request.message)
        
        # 히스토리가 너무 길어지면 압축
        compress_history()
        
        # 이름 호출 감지
        name_detection = conversation_logic.detect_name_call(request.message)
        
        # 대화 로직을 사용해서 자연스러운 응답 생성
        conversation_logic.update_conversation_state(request.message)
        
        # 이름이 호출되었으면 해당 AI만 응답
        if name_detection["is_direct_call"]:
            called_names = name_detection["called_names"]
            if "jinny" in called_names:
                combined_response = jinny_message
                logger.info(f"Jinny called directly: {combined_response}")
            elif "tom" in called_names:
                combined_response = tom_message
                logger.info(f"Tom called directly: {combined_response}")
            else:
                combined_response = conversation_logic.create_response(
                    request.message, jinny_message, tom_message
                )
        else:
            combined_response = conversation_logic.create_response(
                request.message, jinny_message, tom_message
            )
        
        logger.info(f"Response created: {combined_response}")
        return {"response": combined_response}
        
    except Exception as e:
        logger.error(f"=== Error in chat endpoint ===")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
        logger.error(f"Full traceback:")
        logger.error(traceback.format_exc())
        
        # 구체적인 에러 메시지 반환
        if "api_key" in str(e).lower():
            return {"response": "OpenAI API 키 오류입니다. 올바른 API 키를 입력해주세요."}
        elif "rate_limit" in str(e).lower():
            return {"response": "API 호출 한도를 초과했습니다. 잠시 후 다시 시도해주세요."}
        else:
            return {"response": f"오류가 발생했습니다: {str(e)}"}

@app.post("/chat-2person")
async def chat_2person(request: ChatRequest):
    """2인 관심사 기반 대화 (Gemini AI만 사용)"""
    logger.info(f"=== 2-person chat endpoint called ===")
    logger.info(f"Received message: {request.message}")
    
    try:
        if not gemini_model:
            logger.error("No Gemini API available")
            return {"response": "Gemini API가 설정되지 않았습니다."}
        
        # 시청기록 정보 준비
        if viewing_history_data:
            top_interests = viewing_history_data.get('top_interests', [])
            favorite_category = viewing_history_data.get('favorite_category', '')
            recent_videos = viewing_history_data.get('viewing_history', [])[:3]
            
            viewing_history_info = f"""
- 주요 관심사: {', '.join(top_interests)}
- 가장 좋아하는 카테고리: {favorite_category}
- 최근 시청 영상: {', '.join([video['title'] for video in recent_videos])}
            """
        else:
            viewing_history_info = "시청기록 정보가 없습니다."
        
        # Gemini AI 전용 프롬프트
        gemini_system_prompt = f"""당신은 AI DUDE의 친근한 영어 대화 파트너입니다.

**역할과 책임:**
1. 사용자의 관심사를 바탕으로 자연스럽게 대화하세요
2. 모든 대화는 영어로 진행하되, 한국어 설명을 포함하세요
3. 사용자가 어려워할 때 즉시 도움을 제공하세요
4. 영어 학습에 대한 긍정적인 피드백을 제공하세요

**대화 스타일:**
- 따뜻하고 격려하는 톤
- 사용자의 감정을 공감하고 지지
- 자연스러운 대화 연결
- 메시지 앞에 "🤖 AI:"를 붙여서 화자를 명시

**시청기록 정보:**
{viewing_history_info}

**대화 규칙:**
1. 모든 대화는 영어로 진행하되, 이해를 돕기 위해 한국어 설명을 포함하세요
2. 시청기록의 관심사를 바탕으로 대화를 진행하세요
3. 영어 표현을 사용할 때마다 한국어로 의미를 설명해주세요
4. 메시지 앞에 "🤖 AI:"를 붙여서 화자를 명시하세요
5. 친근하고 도움이 되는 톤으로 대화하세요
"""
        
        # Gemini AI 응답
        logger.info("Calling Gemini API for 2-person chat...")
        
        # 압축된 대화 맥락 사용
        compressed_data = keyword_compressor.compress_conversation(
            conversation_history["full_conversation"], 
            keep_recent=8
        )
        
        # 압축된 맥락 추가
        context_text = ""
        if compressed_data["compressed_context"] != "대화가 시작되었습니다.":
            context_text = f"\n\n이전 대화 맥락: {compressed_data['compressed_context']}"
        
        # 최근 메시지 추가
        recent_text = ""
        for msg in compressed_data["recent_messages"]:
            if msg["role"] == "user":
                recent_text += f"사용자: {msg['content']}\n"
            elif msg["role"] == "assistant":
                recent_text += f"AI: {msg['content']}\n"
        
        gemini_response = gemini_model.generate_content(
            f"{gemini_system_prompt}{context_text}\n\n최근 대화:\n{recent_text}\n\n사용자: {request.message}\n\nAI:"
        )
        
        ai_message = gemini_response.text
        logger.info(f"Gemini 2-person response: {ai_message}")
        
        # 대화 히스토리에 저장
        add_to_history("ai", ai_message, request.message)
        compress_history()
        
        return {"response": ai_message}
        
    except Exception as e:
        logger.error(f"=== Error in 2-person chat endpoint ===")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
        logger.error(f"Full traceback:")
        logger.error(traceback.format_exc())
        
        return {"response": f"오류가 발생했습니다: {str(e)}"}

# 서버 시작 시 로그
logger.info("=== AI Chat Server initialized successfully ===")
logger.info("Available endpoints:")
logger.info("  - GET /")
logger.info("  - GET /health")
logger.info("  - GET /test")
logger.info("  - GET /viewing-history")
logger.info("  - POST /initial-greeting")
logger.info("  - POST /initial-greeting-2person")
logger.info("  - POST /chat")
logger.info("  - POST /chat-2person")
logger.info("  - GET /docs (FastAPI documentation)")
