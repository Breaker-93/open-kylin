import { useState } from 'react'
import {
  Puzzle,
  MessageCircle,
  Wrench,
  Database,
  ChevronRight,
  Search,
  Plus,
  Settings,
  Power,
  PowerOff,
} from 'lucide-react'
import { useStore } from '../store'
import type { Plugin } from '../types'

const pluginTypeIcons = {
  channel: MessageCircle,
  tool: Wrench,
  provider: Database,
}

const pluginTypeColors = {
  channel: 'from-blue-500 to-blue-600',
  tool: 'from-purple-500 to-purple-600',
  provider: 'from-amber-500 to-amber-600',
}

export function Plugins() {
  const { plugins, togglePlugin } = useStore()
  const [searchQuery, setSearchQuery] = useState('')
  const [activeTab, setActiveTab] = useState<'all' | 'channel' | 'tool' | 'provider'>('all')

  const filteredPlugins = plugins.filter((p) => {
    const matchesSearch = p.name.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesTab = activeTab === 'all' || p.type === activeTab
    return matchesSearch && matchesTab
  })

  const tabs = [
    { key: 'all', label: '全部', count: plugins.length },
    { key: 'channel', label: '渠道', count: plugins.filter((p) => p.type === 'channel').length },
    { key: 'tool', label: '工具', count: plugins.filter((p) => p.type === 'tool').length },
    { key: 'provider', label: '模型', count: plugins.filter((p) => p.type === 'provider').length },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">插件中心</h1>
          <p className="text-[#B2BAC2] mt-1">管理渠道插件、工具插件和模型供应商</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-[#00D9FF] to-[#0066FF] rounded-lg text-white hover:opacity-90 transition-opacity">
          <Plus className="w-4 h-4" />
          安装插件
        </button>
      </div>

      {/* Search & Tabs */}
      <div className="bg-[#0A1929]/50 rounded-xl p-4 border border-[#00D9FF]/10">
        <div className="flex items-center gap-4 mb-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#B2BAC2]" />
            <input
              type="text"
              placeholder="搜索插件..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-[#0D2137] border border-[#00D9FF]/20 rounded-lg text-white placeholder-[#B2BAC2]/50 focus:outline-none focus:border-[#00D9FF]/50"
            />
          </div>
        </div>

        <div className="flex gap-2">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as typeof activeTab)}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                activeTab === tab.key
                  ? 'bg-[#00D9FF]/20 text-[#00D9FF]'
                  : 'text-[#B2BAC2] hover:bg-[#0D2137]'
              }`}
            >
              {tab.label}
              <span className="ml-2 text-xs opacity-60">({tab.count})</span>
            </button>
          ))}
        </div>
      </div>

      {/* Plugin Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredPlugins.map((plugin) => (
          <PluginCard key={plugin.id} plugin={plugin} onToggle={togglePlugin} />
        ))}
      </div>

      {filteredPlugins.length === 0 && (
        <div className="text-center py-12 text-[#B2BAC2]/50">
          <Puzzle className="w-16 h-16 mx-auto mb-3 opacity-30" />
          <p>没有找到匹配的插件</p>
        </div>
      )}
    </div>
  )
}

function PluginCard({
  plugin,
  onToggle,
}: {
  plugin: Plugin
  onToggle: (id: string) => void
}) {
  const Icon = pluginTypeIcons[plugin.type as keyof typeof pluginTypeIcons]
  const colorClass = pluginTypeColors[plugin.type as keyof typeof pluginTypeColors]

  return (
    <div className="bg-[#0A1929]/50 rounded-xl p-5 border border-[#00D9FF]/10 hover:border-[#00D9FF]/30 transition-all">
      <div className="flex items-start justify-between mb-4">
        <div className={`p-3 rounded-xl bg-gradient-to-br ${colorClass}`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
        <button
          onClick={() => onToggle(plugin.id)}
          className={`p-2 rounded-lg transition-all ${
            plugin.enabled
              ? 'bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30'
              : 'bg-[#0D2137] text-[#B2BAC2] hover:bg-[#0D2137]/80'
          }`}
        >
          {plugin.enabled ? <Power className="w-4 h-4" /> : <PowerOff className="w-4 h-4" />}
        </button>
      </div>

      <h3 className="text-white font-semibold mb-1">{plugin.name}</h3>
      <p className="text-sm text-[#B2BAC2]/70 mb-3 line-clamp-2">{plugin.description}</p>

      <div className="flex items-center justify-between text-xs text-[#B2BAC2]/50">
        <span>v{plugin.version}</span>
        <span
          className={`px-2 py-0.5 rounded-full ${
            plugin.enabled ? 'bg-emerald-500/20 text-emerald-400' : 'bg-[#0D2137]'
          }`}
        >
          {plugin.enabled ? '已启用' : '已禁用'}
        </span>
      </div>

      <button className="w-full mt-4 flex items-center justify-center gap-1 py-2 rounded-lg border border-[#00D9FF]/20 text-[#00D9FF] hover:bg-[#00D9FF]/10 transition-colors">
        <Settings className="w-3 h-3" />
        配置
        <ChevronRight className="w-3 h-3" />
      </button>
    </div>
  )
}
