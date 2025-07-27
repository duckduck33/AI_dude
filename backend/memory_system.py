import json
from typing import Dict, List, Optional
from datetime import datetime

class ConversationMemory:
    def __init__(self):
        self.short_term = []  # 최근 5-10개 메시지
        self.session_summary = {}  # 현재 세션 요약
        self.user_profile = {}  # 사용자 프로필
        self.vocabulary_notes = []  # 학습한 단어들
        
    def add_message(self, role: str, content: str, speaker: str = None):
        """메시지 추가"""
        self.short_term.append({
            "role": role,
            "content": content,
            "speaker": speaker,
            "timestamp": datetime.now().isoformat()
        })
        
        # 최근 10개만 유지
        if len(self.short_term) > 10:
            self.short_term = self.short_term[-10:]
    
    def update_session_summary(self, topic: str, vocabulary: List[str], user_interests: List[str]):
        """세션 요약 업데이트"""
        self.session_summary = {
            "current_topic": topic,
            "key_vocabulary": vocabulary,
            "user_interests": user_interests,
            "conversation_style": "friendly",
            "last_updated": datetime.now().isoformat()
        }
    
    def get_context_for_ai(self, ai_name: str) -> Dict:
        """AI별 최적화된 컨텍스트 반환"""
        if ai_name == "jinny":
            return {
                "short_term": self.short_term[-5:],  # 최근 5개만
                "session_summary": self.session_summary,
                "user_profile": self.user_profile
            }
        elif ai_name == "tom":
            return {
                "short_term": self.short_term[-3:],  # 최근 3개만
                "session_summary": self.session_summary,
                "vocabulary_notes": self.vocabulary_notes
            }
    
    def extract_keywords(self, text: str) -> List[str]:
        """텍스트에서 키워드 추출"""
        # 간단한 키워드 추출 (실제로는 NLP 라이브러리 사용)
        keywords = []
        common_words = ["like", "love", "hate", "want", "need", "think", "feel"]
        words = text.lower().split()
        for word in words:
            if word in common_words or len(word) > 4:
                keywords.append(word)
        return keywords

# 전역 메모리 인스턴스
conversation_memory = ConversationMemory() 