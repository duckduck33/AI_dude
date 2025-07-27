'use client'

import { useState, useEffect } from 'react'

interface Topic {
  id: number
  topic: string
  imageUrl: string
}

interface InterestDashboardProps {
  onStartChat: () => void
}

export default function InterestDashboard({ onStartChat }: InterestDashboardProps) {
  const [topics, setTopics] = useState<Topic[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchTopics = async () => {
      try {
        const response = await fetch('/api/topics')
        const data = await response.json()
        setTopics(data)
      } catch (error) {
        console.error('Error fetching topics:', error)
        // 기본 데이터로 폴백
        setTopics([
          { id: 1, topic: "진격의 거인", imageUrl: "/anime.jpg" },
          { id: 2, topic: "마션", imageUrl: "/movie.jpg" },
          { id: 3, topic: "인터스텔라", imageUrl: "/sf.jpg" },
          { id: 4, topic: "SF 영화", imageUrl: "/scifi.jpg" },
          { id: 5, topic: "일본 애니메이션", imageUrl: "/japan.jpg" }
        ])
      } finally {
        setLoading(false)
      }
    }

    fetchTopics()
  }, [])

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-800 mb-4">관심사 대시보드</h2>
        <p className="text-gray-600">당신의 관심사를 기반으로 AI와 대화해보세요</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {topics.map((topic) => (
          <div
            key={topic.id}
            className="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow cursor-pointer"
            onClick={onStartChat}
          >
            <div className="h-48 bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center">
              <div className="text-white text-center">
                <h3 className="text-xl font-semibold mb-2">{topic.topic}</h3>
                <p className="text-blue-100">클릭하여 대화 시작</p>
              </div>
            </div>
            <div className="p-4">
              <h4 className="font-semibold text-gray-800 mb-2">{topic.topic}</h4>
              <p className="text-gray-600 text-sm">
                이 주제에 대해 AI와 대화해보세요
              </p>
            </div>
          </div>
        ))}
      </div>

      <div className="text-center">
        <button
          onClick={onStartChat}
          className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-8 py-3 rounded-lg text-lg font-semibold hover:from-blue-600 hover:to-purple-700 transition-all transform hover:scale-105 shadow-lg"
        >
          대화 시작하기
        </button>
      </div>
    </div>
  )
} 