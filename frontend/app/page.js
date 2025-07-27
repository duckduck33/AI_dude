'use client'

import { useState, useEffect, useRef } from 'react'

export default function Home() {
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [currentView, setCurrentView] = useState('main') // main, chat
  const [currentMenu, setCurrentMenu] = useState('') // 현재 선택된 메뉴
  const [openaiApiKey, setOpenaiApiKey] = useState('')
  const [googleApiKey, setGoogleApiKey] = useState('')
  const [showApiKeyModal, setShowApiKeyModal] = useState(false)
  const [viewingHistory, setViewingHistory] = useState(null)
  const messagesEndRef = useRef(null)

  // 로컬 스토리지에서 API 키 로드
  useEffect(() => {
    const savedOpenaiApiKey = localStorage.getItem('ai_dude_openai_api_key')
    const savedGoogleApiKey = localStorage.getItem('ai_dude_google_api_key')
    if (savedOpenaiApiKey) {
      setOpenaiApiKey(savedOpenaiApiKey)
    }
    if (savedGoogleApiKey) {
      setGoogleApiKey(savedGoogleApiKey)
    }
  }, [])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // 시청기록 데이터 로드
  useEffect(() => {
    if (currentView === 'chat') {
      fetchViewingHistory()
    }
  }, [currentView])

  const fetchViewingHistory = async () => {
    try {
      const response = await fetch('http://localhost:8001/viewing-history')
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      setViewingHistory(data)
    } catch (error) {
      console.error('Error fetching viewing history:', error)
      // 시청기록 가져오기 실패 시에도 채팅은 계속 가능하도록
    }
  }

  // 페이지 로드 시 AI가 먼저 인사
  useEffect(() => {
    if (currentView === 'chat') {
      // AI에게 첫 인사 요청
            const requestInitialGreeting = async () => {
        try {
          // 2인 대화인 경우 Gemini AI 초기 인사
          if (currentMenu === 'interest-2') {
            const response = await fetch('http://localhost:8001/initial-greeting-2person', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                api_key: googleApiKey
              }),
            })

            if (!response.ok) {
              throw new Error(`HTTP error! status: ${response.status}`)
            }

            const data = await response.json()

            if (data.response) {
              const initialMessage = {
                id: Date.now().toString(),
                content: data.response,
                sender: 'ai',
                timestamp: new Date()
              }
              setMessages([initialMessage])
            }
          } else {
            // 3인 대화인 경우 기존 방식
            const response = await fetch('http://localhost:8001/initial-greeting', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                api_key: openaiApiKey
              }),
            })

            if (!response.ok) {
              throw new Error(`HTTP error! status: ${response.status}`)
            }

            const data = await response.json()

            if (data.response) {
              const initialMessage = {
                id: Date.now().toString(),
                content: data.response,
                sender: 'ai',
                timestamp: new Date()
              }
              setMessages([initialMessage])
            }
          }
        } catch (error) {
          console.error('Error requesting initial greeting:', error)
          // 에러 시 서버 연결 문제 메시지
          const initialMessage = {
            id: Date.now().toString(),
            content: "서버에 연결할 수 없습니다. 백엔드 서버(포트 8001)가 실행 중인지 확인해주세요.",
            sender: 'ai',
            timestamp: new Date()
          }
          setMessages([initialMessage])
        }
      }
      
      requestInitialGreeting()
    }
  }, [currentView, viewingHistory, openaiApiKey, googleApiKey])

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return

    const userMessage = {
      id: Date.now().toString(),
      content: inputMessage,
      sender: 'user',
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      // 현재 메뉴에 따라 다른 엔드포인트 사용
      const endpoint = currentMenu === 'interest-2' ? '/chat-2person' : '/chat'
      
      const response = await fetch(`http://localhost:8001${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          message: inputMessage,
          api_key: currentMenu === 'interest-2' ? googleApiKey : openaiApiKey
        }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()

      if (data.response) {
        const aiMessage = {
          id: (Date.now() + 1).toString(),
          content: data.response,
          sender: 'ai',
          timestamp: new Date()
        }
        setMessages(prev => [...prev, aiMessage])
      }
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        content: '서버에 연결할 수 없습니다. 백엔드 서버(포트 8001)가 실행 중인지 확인해주세요.',
        sender: 'ai',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const menuItems = [
    {
      id: 'interest-3',
      title: '3인 관심사 기반 대화',
      description: 'Jinny와 Tom이 함께하는 맞춤형 대화',
      icon: '👥',
      color: 'from-blue-500 to-blue-600'
    },
    {
      id: 'interest-2',
      title: '2인 관심사 기반 대화',
      description: 'Gemini AI와 1:1 맞춤형 대화',
      icon: '🤖',
      color: 'from-indigo-500 to-indigo-600'
    },
    {
      id: 'schedule',
      title: '스케줄 기반 대화',
      description: '구글 캘린더를 활용한 일정 기반 대화',
      icon: '📅',
      color: 'from-green-500 to-green-600'
    },
    {
      id: 'score',
      title: '스코어',
      description: '나의 영어 학습 진도와 성취도 확인',
      icon: '🏆',
      color: 'from-purple-500 to-purple-600'
    },
    {
      id: 'game',
      title: '영어게임',
      description: '재미있는 영어 학습 게임으로 실력 향상',
      icon: '🎮',
      color: 'from-orange-500 to-orange-600'
    }
  ]

  const handleMenuClick = (menuId) => {
    // 3인 대화: API 키 2개 모두 필요
    if (menuId === 'interest-3' && (!openaiApiKey || !googleApiKey)) {
      alert('3인 대화를 위해서는 API 키 2개 모두 필요합니다. 우측 상단의 API 키 버튼을 클릭하여 설정해주세요.')
      return
    }
    
    // 2인 대화: Google API 키 필요
    if (menuId === 'interest-2' && !googleApiKey) {
      alert('2인 대화를 위해서는 Google API 키가 필요합니다. 우측 상단의 API 키 버튼을 클릭하여 설정해주세요.')
      return
    }
    
    setCurrentView('chat')
    setCurrentMenu(menuId)
  }

  const handleApiKeyChange = () => {
    setShowApiKeyModal(true)
  }

  const handleBackToMain = () => {
    setCurrentView('main')
    setCurrentMenu('')
    setMessages([])
    setViewingHistory(null)
  }

  const handleApiKeySubmit = () => {
    if (openaiApiKey.trim() || googleApiKey.trim()) {
      // API 키를 로컬 스토리지에 저장
      if (openaiApiKey.trim()) {
        localStorage.setItem('ai_dude_openai_api_key', openaiApiKey)
      }
      if (googleApiKey.trim()) {
        localStorage.setItem('ai_dude_google_api_key', googleApiKey)
      }
      setShowApiKeyModal(false)
    }
  }

  // API 키 모달
  if (showApiKeyModal) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-2xl p-8 max-w-lg w-full mx-4 shadow-2xl">
          <div className="text-center mb-6">
            <h3 className="text-2xl font-bold text-gray-800 mb-2">🔑 API 키 입력</h3>
            <p className="text-gray-600">사용할 API 키들을 입력해주세요</p>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                OpenAI API Key (ChatGPT)
              </label>
              <input
                type="password"
                value={openaiApiKey}
                onChange={(e) => setOpenaiApiKey(e.target.value)}
                placeholder="sk-..."
                className="w-full border border-gray-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500"
              />
              <p className="text-xs text-gray-500 mt-1">3인 대화에서 Jinny가 사용합니다</p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Google API Key (Gemini)
              </label>
              <input
                type="password"
                value={googleApiKey}
                onChange={(e) => setGoogleApiKey(e.target.value)}
                placeholder="AIza..."
                className="w-full border border-gray-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent text-gray-900 placeholder-gray-500"
              />
              <p className="text-xs text-gray-500 mt-1">2인 대화와 3인 대화의 Tom이 사용합니다</p>
            </div>
          </div>
          
          <div className="flex space-x-3 mt-6">
            <button
              onClick={() => setShowApiKeyModal(false)}
              className="flex-1 bg-gray-200 text-gray-800 px-4 py-3 rounded-xl hover:bg-gray-300 transition-colors"
            >
              취소
            </button>
            <button
              onClick={handleApiKeySubmit}
              disabled={!openaiApiKey.trim() && !googleApiKey.trim()}
              className="flex-1 bg-blue-500 text-white px-4 py-3 rounded-xl hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              저장
            </button>
          </div>
          
          <div className="mt-4 text-xs text-gray-500 text-center">
            API 키는 브라우저에만 저장되며 서버로 전송됩니다
          </div>
        </div>
      </div>
    )
  }

  if (currentView === 'chat') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="container mx-auto px-4 py-8">
          {/* 헤더 */}
          <div className="flex items-center justify-between mb-6">
            <button
              onClick={handleBackToMain}
              className="flex items-center text-gray-600 hover:text-gray-800 transition-colors"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              뒤로가기
            </button>
            <h1 className="text-2xl font-bold text-gray-800">AI DUDE</h1>
            <div className="flex items-center space-x-2">
              <span className="text-xs text-gray-500">API 키 설정됨</span>
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <button
                onClick={handleApiKeyChange}
                className="text-xs text-blue-500 hover:text-blue-700 underline"
              >
                변경
              </button>
            </div>
          </div>

          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
              {/* 채팅 헤더 */}
              <div className="bg-gradient-to-r from-blue-500 to-purple-600 px-6 py-4">
                <h2 className="text-white text-xl font-semibold">
                  {currentMenu === 'interest-3' ? '3인 관심사 기반 대화' : 
                   currentMenu === 'interest-2' ? '2인 관심사 기반 대화' :
                   currentMenu === 'schedule' ? '스케줄 기반 대화' :
                   currentMenu === 'score' ? '스코어' : '영어게임'}
                </h2>
                <p className="text-blue-100 text-sm">
                  {currentMenu === 'interest-3' ? 'Jinny와 Tom이 함께하는 맞춤형 대화' :
                   currentMenu === 'interest-2' ? 'Gemini AI와 1:1 맞춤형 대화' :
                   '유튜브 시청 기록을 분석한 맞춤형 대화'}
                </p>
                
                {/* 시청기록 정보 표시 */}
                {viewingHistory && (currentMenu === 'interest-3' || currentMenu === 'interest-2') && (
                  <div className="mt-3 p-3 bg-white/20 rounded-lg">
                    <div className="text-white text-sm">
                      <div className="flex items-center mb-1">
                        <span className="font-semibold">📺 시청기록 분석:</span>
                      </div>
                      <div className="text-blue-100 text-xs">
                        <div>• 주요 관심사: {viewingHistory.top_interests?.join(', ')}</div>
                        <div>• 선호 카테고리: {viewingHistory.favorite_category}</div>
                        <div>• 총 시청시간: {viewingHistory.total_watch_time}</div>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* 메시지 영역 */}
              <div className="h-96 overflow-y-auto p-4 space-y-4">
                {currentMenu === 'interest-3' && (!openaiApiKey || !googleApiKey) && (
                  <div className="flex justify-center">
                    <div className="bg-red-100 border border-red-400 text-red-800 px-4 py-3 rounded-lg max-w-md">
                      <div className="flex items-center">
                        <span className="text-red-600 mr-2">🚨</span>
                        <div>
                          <p className="font-medium">API 키 2개 모두 필요합니다</p>
                          <p className="text-sm">3인 대화를 위해서는 OpenAI API 키와 Google API 키가 모두 필요합니다. 우측 상단의 API 키 버튼을 클릭하여 설정해주세요.</p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                
                {currentMenu === 'interest-2' && !googleApiKey && (
                  <div className="flex justify-center">
                    <div className="bg-red-100 border border-red-400 text-red-800 px-4 py-3 rounded-lg max-w-md">
                      <div className="flex items-center">
                        <span className="text-red-600 mr-2">🚨</span>
                        <div>
                          <p className="font-medium">Google API 키가 필요합니다</p>
                          <p className="text-sm">2인 대화를 위해서는 Google API 키가 필요합니다. 우측 상단의 API 키 버튼을 클릭하여 설정해주세요.</p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                
                {messages.map((message) => (
                  <div key={message.id} className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div
                      className={`max-w-xs lg:max-w-md px-4 py-2 rounded-2xl ${
                        message.sender === 'user'
                          ? 'bg-blue-500 text-white'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      <p className="text-sm">{message.content}</p>
                      <p className={`text-xs mt-1 ${
                        message.sender === 'user' ? 'text-blue-100' : 'text-gray-500'
                      }`}>
                        {message.timestamp.toLocaleTimeString('ko-KR', {
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </p>
                    </div>
                  </div>
                ))}
                
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-100 rounded-2xl px-4 py-2 max-w-xs">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                    </div>
                  </div>
                )}
                
                <div ref={messagesEndRef} />
              </div>

              {/* 입력 영역 */}
              <div className="border-t border-gray-200 p-4">
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="메시지를 입력하세요..."
                    className="flex-1 border border-gray-300 rounded-xl px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500"
                    disabled={isLoading}
                  />
                  <button
                    onClick={sendMessage}
                    disabled={!inputMessage.trim() || isLoading}
                    className="bg-blue-500 text-white px-6 py-2 rounded-xl hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    전송
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 relative">
      {/* 우측 상단 API 키 버튼 */}
      <div className="absolute top-4 right-4 z-10">
        <button
          onClick={() => setShowApiKeyModal(true)}
          className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg shadow-lg transition-colors flex items-center space-x-2"
        >
          <span className="text-sm">🔑</span>
          <span className="text-sm font-medium">
            {openaiApiKey || googleApiKey ? 'API 키 설정됨' : 'API 키 입력'}
          </span>
        </button>
      </div>

      {/* 우측 하단 개발 문의 버튼 */}
      <div className="absolute bottom-4 right-4 z-10">
        <a
          href="https://pf.kakao.com/_xlLxcfxj/chat"
          target="_blank"
          rel="noopener noreferrer"
          className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg shadow-lg transition-colors flex items-center space-x-2"
        >
          <span className="text-sm">💬</span>
          <span className="text-sm font-medium">잠코딩개발문의</span>
        </a>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* 헤더 */}
        <header className="text-center mb-12">
          <div className="mb-6">
            <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent mb-4">
              AI DUDE
            </h1>
            <div className="w-24 h-1 bg-gradient-to-r from-blue-500 to-purple-500 mx-auto rounded-full"></div>
          </div>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto leading-relaxed">
            2명의 AI친구가 사용자의 유튜브시청기록과 구글 캘린더를 분석해서 사용자의 관심사를 파악하고 대화를 거는 신개념 영어회화 어플입니다
          </p>
        </header>

        {/* 메뉴 그리드 */}
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {menuItems.map((item) => (
              <div
                key={item.id}
                onClick={() => handleMenuClick(item.id)}
                className="group cursor-pointer transform transition-all duration-300 hover:scale-105 hover:shadow-2xl"
              >
                <div className={`bg-gradient-to-br ${item.color} rounded-3xl p-8 shadow-lg group-hover:shadow-2xl transition-all duration-300`}>
                  <div className="text-center">
                    <div className="text-6xl mb-4 transform group-hover:scale-110 transition-transform duration-300">
                      {item.icon}
                    </div>
                    <h3 className="text-2xl font-bold text-white mb-3">
                      {item.title}
                    </h3>
                    <p className="text-blue-100 text-sm leading-relaxed">
                      {item.description}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 하단 설명 */}
        <div className="text-center mt-12">
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg">
            <h3 className="text-xl font-semibold text-gray-800 mb-3">
              🚀 AI DUDE와 함께 영어 실력 향상하기
            </h3>
            <p className="text-gray-600">
              개인화된 학습 경험으로 더욱 효과적인 영어 학습을 경험해보세요
            </p>
          </div>
        </div>
      </div>
    </div>
  )
} 