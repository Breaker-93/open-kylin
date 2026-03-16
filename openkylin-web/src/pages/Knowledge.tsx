import { useState } from 'react'
import {
  BookOpen,
  Plus,
  Search,
  Upload,
  FileText,
  Trash2,
  Settings,
  Play,
  ChevronRight,
  Clock,
} from 'lucide-react'
import { useStore } from '../store'
import { formatDate } from '../lib/utils'

export function Knowledge() {
  const { knowledgeBases, addKnowledgeBase } = useStore()
  const [searchQuery, setSearchQuery] = useState('')
  const [showCreateModal, setShowCreateModal] = useState(false)

  const filteredKBs = knowledgeBases.filter((kb) =>
    kb.name.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const [newKBName, setNewKBName] = useState('')
  const [newKBDesc, setNewKBDesc] = useState('')

  const handleCreate = () => {
    if (!newKBName.trim()) return
    addKnowledgeBase({ name: newKBName, description: newKBDesc })
    setNewKBName('')
    setNewKBDesc('')
    setShowCreateModal(false)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">知识库</h1>
          <p className="text-[#B2BAC2] mt-1">管理 RAG 知识库和文档检索</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-[#00D9FF] to-[#0066FF] rounded-lg text-white hover:opacity-90 transition-opacity"
        >
          <Plus className="w-4 h-4" />
          新建知识库
        </button>
      </div>

      {/* Search */}
      <div className="bg-[#0A1929]/50 rounded-xl p-4 border border-[#00D9FF]/10">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#B2BAC2]" />
          <input
            type="text"
            placeholder="搜索知识库..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-[#0D2137] border border-[#00D9FF]/20 rounded-lg text-white placeholder-[#B2BAC2]/50 focus:outline-none focus:border-[#00D9FF]/50"
          />
        </div>
      </div>

      {/* Knowledge Base List */}
      <div className="space-y-4">
        {filteredKBs.length === 0 ? (
          <div className="text-center py-12 text-[#B2BAC2]/50">
            <BookOpen className="w-16 h-16 mx-auto mb-3 opacity-30" />
            <p>暂无知识库</p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="mt-2 text-[#00D9FF] hover:underline"
            >
              创建第一个知识库
            </button>
          </div>
        ) : (
          filteredKBs.map((kb) => (
            <KnowledgeCard key={kb.id} kb={kb} />
          ))
        )}
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-[#0A1929] rounded-xl p-6 w-full max-w-md border border-[#00D9FF]/20">
            <h3 className="text-xl font-semibold text-white mb-4">新建知识库</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-[#B2BAC2] mb-2">名称</label>
                <input
                  type="text"
                  value={newKBName}
                  onChange={(e) => setNewKBName(e.target.value)}
                  placeholder="输入知识库名称"
                  className="w-full px-4 py-2 bg-[#0D2137] border border-[#00D9FF]/20 rounded-lg text-white placeholder-[#B2BAC2]/50 focus:outline-none focus:border-[#00D9FF]/50"
                />
              </div>
              <div>
                <label className="block text-sm text-[#B2BAC2] mb-2">描述</label>
                <textarea
                  value={newKBDesc}
                  onChange={(e) => setNewKBDesc(e.target.value)}
                  placeholder="输入知识库描述"
                  rows={3}
                  className="w-full px-4 py-2 bg-[#0D2137] border border-[#00D9FF]/20 rounded-lg text-white placeholder-[#B2BAC2]/50 focus:outline-none focus:border-[#00D9FF]/50 resize-none"
                />
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={() => setShowCreateModal(false)}
                className="px-4 py-2 rounded-lg text-[#B2BAC2] hover:bg-[#0D2137] transition-colors"
              >
                取消
              </button>
              <button
                onClick={handleCreate}
                className="px-4 py-2 bg-gradient-to-r from-[#00D9FF] to-[#0066FF] rounded-lg text-white hover:opacity-90 transition-opacity"
              >
                创建
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function KnowledgeCard({
  kb,
}: {
  kb: { id: string; name: string; description: string; documentCount: number; createdAt: string; updatedAt: string }
}) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="bg-[#0A1929]/50 rounded-xl border border-[#00D9FF]/10 hover:border-[#00D9FF]/30 transition-all">
      <div className="p-5">
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-4">
            <div className="p-3 rounded-xl bg-gradient-to-br from-purple-500 to-purple-600">
              <BookOpen className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-white font-semibold">{kb.name}</h3>
              <p className="text-sm text-[#B2BAC2]/70 mt-1">{kb.description}</p>
              <div className="flex items-center gap-4 mt-3 text-xs text-[#B2BAC2]/50">
                <span className="flex items-center gap-1">
                  <FileText className="w-3 h-3" />
                  {kb.documentCount} 文档
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  更新于 {formatDate(kb.updatedAt)}
                </span>
              </div>
            </div>
          </div>
          <button
            onClick={() => setExpanded(!expanded)}
            className="p-2 rounded-lg text-[#B2BAC2] hover:bg-[#0D2137] transition-colors"
          >
            <ChevronRight
              className={`w-5 h-5 transition-transform ${expanded ? 'rotate-90' : ''}`}
            />
          </button>
        </div>

        {/* Actions */}
        <div className="flex gap-2 mt-4 pt-4 border-t border-[#00D9FF]/10">
          <button className="flex-1 flex items-center justify-center gap-1 py-2 rounded-lg bg-[#00D9FF]/10 text-[#00D9FF] hover:bg-[#00D9FF]/20 transition-colors">
            <Upload className="w-4 h-4" />
            上传文档
          </button>
          <button className="flex-1 flex items-center justify-center gap-1 py-2 rounded-lg bg-purple-500/10 text-purple-400 hover:bg-purple-500/20 transition-colors">
            <Play className="w-4 h-4" />
            测试检索
          </button>
          <button className="p-2 rounded-lg text-[#B2BAC2] hover:bg-[#0D2137] transition-colors">
            <Settings className="w-4 h-4" />
          </button>
          <button className="p-2 rounded-lg text-red-400 hover:bg-red-500/10 transition-colors">
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Expanded Content */}
      {expanded && (
        <div className="px-5 pb-5">
          <div className="p-4 rounded-lg bg-[#0D2137]/50">
            <h4 className="text-sm font-medium text-white mb-3">最近文档</h4>
            <div className="space-y-2">
              {[1, 2, 3].map((i) => (
                <div
                  key={i}
                  className="flex items-center justify-between p-2 rounded bg-[#0A1929]/50"
                >
                  <div className="flex items-center gap-2">
                    <FileText className="w-4 h-4 text-[#B2BAC2]/50" />
                    <span className="text-sm text-[#B2BAC2]">文档_{i}.pdf</span>
                  </div>
                  <span className="text-xs text-[#B2BAC2]/50">{formatDate(kb.updatedAt)}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
