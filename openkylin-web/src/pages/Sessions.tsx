import { useState } from 'react'
import { Plus, MessageCircle, Trash2, Search, Send } from 'lucide-react'
import { useStore } from '../store'
import { formatDate } from '../lib/utils'


export function Sessions() {
  const { sessions, currentSession, addSession, setCurrentSession, addMessage } = useStore()
  const [searchQuery, setSearchQuery] = useState('')
  const [inputMessage, setInputMessage] = useState('')

  const filteredSessions = sessions.filter((s) =>
    s.title.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const handleNewSession = () => {
    addSession({
      title: `新会话 ${sessions.length + 1}`,
      channel: 'console',
      messages: [],
    })
  }

  const handleSendMessage = () => {
    if (!inputMessage.trim() || !currentSession) return

    addMessage(currentSession.id, {
      role: 'user',
      content: inputMessage,
      channel: 'console',
    })

    setInputMessage('')

    // 模拟AI响应
    setTimeout(() => {
      addMessage(currentSession.id, {
        role: 'assistant',
        content: '你好！我是 OpenKylin AI 助手。我已收到你的消息，正在处理中...',
        channel: 'console',
      })
    }, 1000)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="h-[calc(100vh-3rem)] flex gap-6">
      {/* Session List */}
      <div className="w-80 flex flex-col bg-[#0A1929]/50 rounded-xl border border-[#00D9FF]/10">
        <div className="p-4 border-b border-[#00D9FF]/10">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-semibold text-white">会话列表</h2>
            <button
              onClick={handleNewSession}
              className="p-2 rounded-lg bg-[#00D9FF]/20 text-[#00D9FF] hover:bg-[#00D9FF]/30 transition-colors"
            >
              <Plus className="w-4 h-4" />
            </button>
          </div>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#B2BAC2]" />
            <input
              type="text"
              placeholder="搜索会话..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-[#0D2137] border border-[#00D9FF]/20 rounded-lg text-white placeholder-[#B2BAC2]/50 focus:outline-none focus:border-[#00D9FF]/50"
            />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {filteredSessions.length === 0 ? (
            <div className="text-center py-8 text-[#B2BAC2]/50">
              <MessageCircle className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p>暂无会话</p>
              <button
                onClick={handleNewSession}
                className="mt-2 text-[#00D9FF] hover:underline"
              >
                创建第一个会话
              </button>
            </div>
          ) : (
            filteredSessions.map((session) => (
              <button
                key={session.id}
                onClick={() => setCurrentSession(session)}
                className={`w-full text-left p-3 rounded-lg transition-all ${
                  currentSession?.id === session.id
                    ? 'bg-[#00D9FF]/10 border border-[#00D9FF]/30'
                    : 'hover:bg-[#0D2137]/50 border border-transparent'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-white font-medium truncate">{session.title}</span>
                  <span className="text-xs text-[#B2BAC2]/50">
                    {session.messages.length}
                  </span>
                </div>
                <p className="text-xs text-[#B2BAC2]/60 mt-1">
                  {formatDate(session.updatedAt)}
                </p>
              </button>
            ))
          )}
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col bg-[#0A1929]/50 rounded-xl border border-[#00D9FF]/10">
        {currentSession ? (
          <>
            {/* Chat Header */}
            <div className="p-4 border-b border-[#00D9FF]/10 flex items-center justify-between">
              <div>
                <h3 className="text-white font-semibold">{currentSession.title}</h3>
                <p className="text-xs text-[#B2BAC2]/60">
                  渠道: {currentSession.channel} · {currentSession.messages.length} 条消息
                </p>
              </div>
              <button className="p-2 rounded-lg text-red-400 hover:bg-red-500/10 transition-colors">
                <Trash2 className="w-4 h-4" />
              </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {currentSession.messages.length === 0 ? (
                <div className="h-full flex items-center justify-center text-[#B2BAC2]/50">
                  <div className="text-center">
                    <MessageCircle className="w-16 h-16 mx-auto mb-3 opacity-30" />
                    <p>开始发送消息开始对话</p>
                  </div>
                </div>
              ) : (
                currentSession.messages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[70%] p-3 rounded-xl ${
                        msg.role === 'user'
                          ? 'bg-[#00D9FF]/20 text-white'
                          : 'bg-[#0D2137] text-[#B2BAC2]'
                      }`}
                    >
                      <p className="whitespace-pre-wrap">{msg.content}</p>
                      <p className="text-xs text-[#B2BAC2]/40 mt-2">
                        {formatDate(msg.timestamp)}
                      </p>
                    </div>
                  </div>
                ))
              )}
            </div>

            {/* Input */}
            <div className="p-4 border-t border-[#00D9FF]/10">
              <div className="flex gap-3">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="输入消息..."
                  className="flex-1 px-4 py-3 bg-[#0D2137] border border-[#00D9FF]/20 rounded-xl text-white placeholder-[#B2BAC2]/50 focus:outline-none focus:border-[#00D9FF]/50"
                />
                <button
                  onClick={handleSendMessage}
                  className="px-4 py-3 bg-gradient-to-r from-[#00D9FF] to-[#0066FF] rounded-xl text-white hover:opacity-90 transition-opacity"
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>
            </div>
          </>
        ) : (
          <div className="h-full flex items-center justify-center text-[#B2BAC2]/50">
            <div className="text-center">
              <MessageCircle className="w-16 h-16 mx-auto mb-3 opacity-30" />
              <p>选择或创建会话开始对话</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
