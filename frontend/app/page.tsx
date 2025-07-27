'use client'

import { useState } from 'react'
import ChatInterface from '../components/ChatInterface'
import InterestDashboard from '../components/InterestDashboard'

export default function Home() {
  const [currentView, setCurrentView] = useState<'chat' | 'dashboard'>('dashboard')

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">AI Dude</h1>
          <p className="text-gray-600">관심사 기반 대화형 AI</p>
        </header>

        <nav className="flex justify-center mb-8">
          <div className="bg-white rounded-lg shadow-md p-1">
            <button
              onClick={() => setCurrentView('dashboard')}
              className={`px-6 py-2 rounded-md transition-colors ${
                currentView === 'dashboard'
                  ? 'bg-blue-500 text-white'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              관심사 대시보드
            </button>
            <button
              onClick={() => setCurrentView('chat')}
              className={`px-6 py-2 rounded-md transition-colors ${
                currentView === 'chat'
                  ? 'bg-blue-500 text-white'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              대화하기
            </button>
          </div>
        </nav>

        <main>
          {currentView === 'dashboard' ? (
            <InterestDashboard onStartChat={() => setCurrentView('chat')} />
          ) : (
            <ChatInterface />
          )}
        </main>
      </div>
    </div>
  )
} 