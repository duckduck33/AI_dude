import random
from typing import Dict, List

class ConversationLogic:
    def __init__(self):
        self.conversation_state = {
            "last_speaker": None,
            "turn_count": 0,
            "topic": None
        }
    
    def decide_who_speaks(self, user_message: str, jinny_response: str, tom_response: str) -> str:
        """누가 말할지 결정하는 로직"""
        
        # 이름 호출 확인
        user_message_lower = user_message.lower()
        if "jinny" in user_message_lower or "지니" in user_message_lower:
            return "jinny_only"
        elif "tom" in user_message_lower or "톰" in user_message_lower:
            return "tom_only"
        
        # 랜덤 요소 추가 (20% 확률로 랜덤 결정)
        if random.random() < 0.2:
            return random.choice(["jinny_only", "tom_only", "both"])
        
        # 사용자 메시지 길이에 따른 결정
        message_length = len(user_message)
        
        # 짧은 메시지 (1-2단어): 한 명만 응답
        if message_length < 10:
            return random.choice(["jinny_only", "tom_only"])
        
        # 긴 메시지 (질문이나 설명): 둘 다 응답 가능
        elif message_length > 30:
            return "both"
        
        # 중간 길이: 상황에 따라 결정
        else:
            # 이전 화자에 따라 결정
            if self.conversation_state["last_speaker"] == "jinny":
                return "tom_only"  # Tom이 이어서
            elif self.conversation_state["last_speaker"] == "tom":
                return "jinny_only"  # Jinny가 이어서
            else:
                return random.choice(["jinny_only", "tom_only", "both"])
    
    def create_response(self, user_message: str, jinny_response: str, tom_response: str) -> str:
        """최종 응답 생성"""
        
        # 누가 말할지 결정
        speaker_decision = self.decide_who_speaks(user_message, jinny_response, tom_response)
        
        if speaker_decision == "both":
            self.conversation_state["last_speaker"] = "both"
            return f"{jinny_response}\n\n{tom_response}"
        
        elif speaker_decision == "jinny_only":
            self.conversation_state["last_speaker"] = "jinny"
            return jinny_response
        
        else:  # tom_only
            self.conversation_state["last_speaker"] = "tom"
            return tom_response
    
    def update_conversation_state(self, user_message: str):
        """대화 상태 업데이트"""
        self.conversation_state["turn_count"] += 1
        
        # 주제 추출 (간단한 버전)
        if any(word in user_message.lower() for word in ["food", "eat", "hungry"]):
            self.conversation_state["topic"] = "food"
        elif any(word in user_message.lower() for word in ["movie", "show", "watch"]):
            self.conversation_state["topic"] = "entertainment"
        elif any(word in user_message.lower() for word in ["work", "study", "learn"]):
            self.conversation_state["topic"] = "work_study"
    
    def detect_name_call(self, user_message: str) -> Dict:
        """이름 호출 감지 및 분석"""
        user_message_lower = user_message.lower()
        
        # 다양한 이름 패턴 확인
        jinny_patterns = ["jinny", "지니", "지니야", "jinny야"]
        tom_patterns = ["tom", "톰", "톰아", "tom아"]
        
        detected_names = []
        
        for pattern in jinny_patterns:
            if pattern in user_message_lower:
                detected_names.append("jinny")
                break
        
        for pattern in tom_patterns:
            if pattern in user_message_lower:
                detected_names.append("tom")
                break
        
        return {
            "called_names": detected_names,
            "is_direct_call": len(detected_names) > 0,
            "message_without_names": self.remove_names_from_message(user_message)
        }
    
    def remove_names_from_message(self, user_message: str) -> str:
        """메시지에서 이름 제거"""
        # 간단한 이름 제거 (실제로는 더 정교한 NLP 필요)
        user_message_clean = user_message
        name_patterns = ["jinny", "지니", "tom", "톰"]
        
        for pattern in name_patterns:
            user_message_clean = user_message_clean.replace(pattern, "").replace(pattern.capitalize(), "")
        
        return user_message_clean.strip()

# 전역 대화 로직 인스턴스
conversation_logic = ConversationLogic() 