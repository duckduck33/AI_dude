import re
from typing import List, Dict, Set

class KeywordCompressor:
    def __init__(self):
        self.important_keywords = set()
        self.topic_keywords = set()
    
    def extract_keywords(self, text: str) -> List[str]:
        """텍스트에서 중요 키워드 추출"""
        # 영어 단어 추출
        english_words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        
        # 중요 키워드 필터링
        important_words = [
            'like', 'love', 'hate', 'want', 'need', 'think', 'feel',
            'good', 'bad', 'great', 'terrible', 'amazing', 'awful',
            'food', 'movie', 'music', 'book', 'game', 'sport',
            'family', 'friend', 'work', 'study', 'travel', 'cook'
        ]
        
        keywords = []
        for word in english_words:
            if word in important_words or len(word) > 5:
                keywords.append(word)
        
        return list(set(keywords))  # 중복 제거
    
    def compress_conversation(self, messages: List[Dict], keep_recent: int = 8) -> Dict:
        """대화를 키워드로 압축"""
        if len(messages) <= keep_recent:
            return {
                "recent_messages": messages,
                "compressed_context": "대화가 시작되었습니다."
            }
        
        # 최근 메시지는 유지
        recent_messages = messages[-keep_recent:]
        
        # 오래된 메시지에서 키워드 추출
        old_messages = messages[:-keep_recent]
        all_keywords = set()
        
        for msg in old_messages:
            keywords = self.extract_keywords(msg["content"])
            all_keywords.update(keywords)
        
        # 키워드를 문장으로 변환
        if all_keywords:
            compressed_context = f"이전 대화에서 언급된 키워드: {', '.join(list(all_keywords)[:10])}"
        else:
            compressed_context = "이전 대화가 있었습니다."
        
        return {
            "recent_messages": recent_messages,
            "compressed_context": compressed_context
        }
    
    def create_efficient_prompt(self, compressed_data: Dict, user_message: str) -> str:
        """압축된 데이터로 효율적인 프롬프트 생성"""
        recent_text = ""
        for msg in compressed_data["recent_messages"]:
            if msg["role"] == "user":
                recent_text += f"User: {msg['content']}\n"
            elif msg["role"] == "assistant":
                speaker = msg.get("speaker", "AI")
                recent_text += f"{speaker}: {msg['content']}\n"
        
        return f"""이전 대화 맥락: {compressed_data['compressed_context']}

최근 대화:
{recent_text}

User: {user_message}
AI:""" 