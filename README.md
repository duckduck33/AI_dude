# AI Dude - 관심사 기반 대화형 AI

관심사 기반으로 자연스러운 대화를 나눌 수 있는 AI 서비스입니다.

## 🚀 기능

- **관심사 기반 대화**: 사용자의 관심사를 기반으로 AI가 대화를 시작
- **AI 오케스트레이터**: AI1(대화 리더) + AI2(서포트) 역할 분담
- **실시간 채팅**: 부드러운 채팅 인터페이스
- **관심사 대시보드**: 카드 형태의 관심사 토픽 표시

## 🛠️ 기술 스택

### Backend
- **FastAPI**: Python 웹 프레임워크
- **OpenAI GPT-3.5-turbo**: AI 대화 모델
- **Pydantic**: 데이터 검증

### Frontend
- **Next.js 14**: React 프레임워크
- **TypeScript**: 타입 안전성
- **Tailwind CSS**: 스타일링
- **App Router**: 최신 Next.js 라우팅

## 📁 프로젝트 구조

```
AI_dude/
├── backend/
│   ├── main.py              # FastAPI 서버
│   ├── interest.json        # 사용자 관심사 데이터
│   ├── prompt.txt           # AI 프롬프트
│   └── requirements.txt     # Python 의존성
├── frontend/
│   ├── app/                 # Next.js App Router
│   ├── components/          # React 컴포넌트
│   ├── package.json         # Node.js 의존성
│   └── tailwind.config.js   # Tailwind 설정
└── README.md
```

## 🚀 실행 방법

### 1. Backend 실행

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend 실행

```bash
cd frontend
npm install
npm run dev
```

### 3. 환경 설정

`.env` 파일을 생성하고 OpenAI API 키를 설정하세요:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

## 🎯 주요 기능

### AI 오케스트레이터 시스템
- **AI1 (대화 리더)**: 관심사 기반으로 먼저 질문을 던져 대화 시작
- **AI2 (서포트)**: 사용자가 망설일 때 부드럽게 개입하여 대화 유도

### 관심사 기반 대화
- 사용자의 관심사 정보를 JSON 형태로 관리
- 관심사별로 자연스러운 대화 주제 생성

### 모던한 UI/UX
- 반응형 디자인 (모바일/데스크톱)
- 실시간 채팅 인터페이스
- 로딩 애니메이션
- 부드러운 스크롤

## 📝 API 엔드포인트

- `POST /chat`: AI와 대화
- `GET /api/topics`: 관심사 토픽 목록

## 🔧 개발 환경

- Node.js 18+
- Python 3.8+
- OpenAI API 키 필요 