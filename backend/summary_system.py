import openai
from typing import List, Dict

class ConversationSummarizer:
    def __init__(self, api_key: str):
        self.api_key = api_key
        openai.api_key = api_key
    
    def summarize_conversation(self, messages: List[Dict]) -> str:
        """대화 요약 생성"""
        if len(messages) < 5:
            return "대화가 시작되었습니다."
        
        # 대화 내용을 텍스트로 변환
        conversation_text = ""
        for msg in messages:
            if msg["role"] == "user":
                conversation_text += f"User: {msg['content']}\n"
            elif msg["role"] == "assistant":
                speaker = msg.get("speaker", "AI")
                conversation_text += f"{speaker}: {msg['content']}\n"
        
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "대화를 2-3문장으로 요약해주세요. 주요 주제와 핵심 내용만 포함하세요."},
                    {"role": "user", "content": f"다음 대화를 요약해주세요:\n\n{conversation_text}"}
                ],
                max_tokens=100
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"대화 요약: {len(messages)}개의 메시지가 있었습니다."
    
    def compress_old_messages(self, messages: List[Dict], keep_recent: int = 10) -> List[Dict]:
        """오래된 메시지 압축"""
        if len(messages) <= keep_recent:
            return messages
        
        # 최근 메시지는 유지
        recent_messages = messages[-keep_recent:]
        
        # 오래된 메시지는 요약
        old_messages = messages[:-keep_recent]
        summary = self.summarize_conversation(old_messages)
        
        # 요약 + 최근 메시지 반환
        return [
            {"role": "system", "content": f"이전 대화 요약: {summary}"},
            *recent_messages
        ] 