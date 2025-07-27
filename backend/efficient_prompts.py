from datetime import datetime

def create_efficient_prompt(ai_name: str, context: Dict, user_message: str) -> str:
    """토큰 효율적인 프롬프트 생성"""
    
    if ai_name == "jinny":
        # Jinny용 간결한 프롬프트
        short_term = context.get("short_term", [])
        session_summary = context.get("session_summary", {})
        
        recent_messages = ""
        for msg in short_term[-3:]:  # 최근 3개만
            if msg["role"] == "user":
                recent_messages += f"User: {msg['content']}\n"
            elif msg["role"] == "assistant":
                recent_messages += f"{msg.get('speaker', 'AI')}: {msg['content']}\n"
        
        return f"""You are Jinny, a friendly English conversation partner.

Current topic: {session_summary.get('current_topic', 'general')}
User interests: {', '.join(session_summary.get('user_interests', []))}

Recent conversation:
{recent_messages}

User: {user_message}
Jinny:"""

    elif ai_name == "tom":
        # Tom용 간결한 프롬프트
        short_term = context.get("short_term", [])
        vocabulary = context.get("vocabulary_notes", [])
        
        recent_messages = ""
        for msg in short_term[-2:]:  # 최근 2개만
            if msg["role"] == "user":
                recent_messages += f"User: {msg['content']}\n"
            elif msg["role"] == "assistant":
                recent_messages += f"{msg.get('speaker', 'AI')}: {msg['content']}\n"
        
        return f"""You are Tom, a helpful English conversation assistant.

Recent vocabulary: {', '.join(vocabulary[-5:])}  # 최근 5개 단어만

Recent conversation:
{recent_messages}

User: {user_message}
Tom:"""

def extract_session_info(user_message: str, ai_response: str) -> Dict:
    """세션 정보 추출 (토큰 절약용)"""
    # 간단한 키워드 추출
    keywords = []
    for word in user_message.lower().split():
        if len(word) > 4 and word.isalpha():
            keywords.append(word)
    
    return {
        "keywords": keywords[:5],  # 최대 5개만
        "response_length": len(ai_response),
        "timestamp": datetime.now().isoformat()
    } 