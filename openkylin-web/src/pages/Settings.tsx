import { useState } from 'react'
import {
  Key,
  Bot,
  Globe,
  Bell,
  Shield,
  Palette,
  Save,
  Eye,
  EyeOff,
  Check,
  ChevronRight,
} from 'lucide-react'
import { useStore } from '../store'

const tabs = [
  { key: 'model', label: '模型配置', icon: Bot },
  { key: 'api', label: 'API 密钥', icon: Key },
  { key: 'channel', label: '渠道设置', icon: Globe },
  { key: 'notification', label: '通知', icon: Bell },
  { key: 'security', label: '安全', icon: Shield },
  { key: 'appearance', label: '外观', icon: Palette },
]

export function Settings() {
  const [activeTab, setActiveTab] = useState('model')

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">设置</h1>
        <p className="text-[#B2BAC2] mt-1">配置模型、渠道和系统参数</p>
      </div>

      <div className="flex gap-6">
        {/* Sidebar */}
        <div className="w-56 bg-[#0A1929]/50 rounded-xl border border-[#00D9FF]/10 p-2">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all ${
                activeTab === tab.key
                  ? 'bg-[#00D9FF]/10 text-[#00D9FF]'
                  : 'text-[#B2BAC2] hover:bg-[#0D2137] hover:text-white'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              <span className="text-sm font-medium">{tab.label}</span>
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="flex-1 bg-[#0A1929]/50 rounded-xl border border-[#00D9FF]/10 p-6">
          {activeTab === 'model' && <ModelSettings />}
          {activeTab === 'api' && <ApiKeySettings />}
          {activeTab === 'channel' && <ChannelSettings />}
          {activeTab === 'notification' && <NotificationSettings />}
          {activeTab === 'security' && <SecuritySettings />}
          {activeTab === 'appearance' && <AppearanceSettings />}
        </div>
      </div>
    </div>
  )
}

function ModelSettings() {
  const { providers, activeProvider, setActiveProvider, setProvider } = useStore()

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-white mb-1">模型配置</h3>
        <p className="text-sm text-[#B2BAC2]/70">选择和配置 AI 模型</p>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-sm text-[#B2BAC2] mb-2">当前模型</label>
          <select
            value={activeProvider || ''}
            onChange={(e) => setActiveProvider(e.target.value)}
            className="w-full px-4 py-2 bg-[#0D2137] border border-[#00D9FF]/20 rounded-lg text-white focus:outline-none focus:border-[#00D9FF]/50"
          >
            {providers.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} - {p.model}
              </option>
            ))}
          </select>
        </div>

        {providers.map((provider) => (
          <div
            key={provider.id}
            className={`p-4 rounded-xl border ${
              activeProvider === provider.id
                ? 'border-[#00D9FF]/50 bg-[#00D9FF]/5'
                : 'border-[#00D9FF]/10'
            }`}
          >
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-white font-medium">{provider.name}</h4>
              {activeProvider === provider.id && (
                <span className="px-2 py-0.5 rounded-full bg-[#00D9FF]/20 text-[#00D9FF] text-xs">
                  使用中
                </span>
              )}
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs text-[#B2BAC2]/70 mb-1">模型</label>
                <input
                  type="text"
                  value={provider.model}
                  onChange={(e) => setProvider({ id: provider.id, model: e.target.value })}
                  className="w-full px-3 py-1.5 bg-[#0D2137] border border-[#00D9FF]/20 rounded-lg text-white text-sm"
                />
              </div>
              {provider.baseUrl && (
                <div>
                  <label className="block text-xs text-[#B2BAC2]/70 mb-1">Base URL</label>
                  <input
                    type="text"
                    value={provider.baseUrl}
                    onChange={(e) => setProvider({ id: provider.id, baseUrl: e.target.value })}
                    className="w-full px-3 py-1.5 bg-[#0D2137] border border-[#00D9FF]/20 rounded-lg text-white text-sm"
                  />
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      <button className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-[#00D9FF] to-[#0066FF] rounded-lg text-white hover:opacity-90 transition-opacity">
        <Save className="w-4 h-4" />
        保存配置
      </button>
    </div>
  )
}

function ApiKeySettings() {
  const [showKey, setShowKey] = useState(false)

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-white mb-1">API 密钥</h3>
        <p className="text-sm text-[#B2BAC2]/70">管理各平台的 API 密钥</p>
      </div>

      <div className="space-y-4">
        <div className="p-4 rounded-xl border border-[#00D9FF]/10">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Key className="w-4 h-4 text-[#00D9FF]" />
              <span className="text-white font-medium">OpenAI API Key</span>
            </div>
            <button
              onClick={() => setShowKey(!showKey)}
              className="text-[#B2BAC2] hover:text-white transition-colors"
            >
              {showKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
          <input
            type={showKey ? 'text' : 'password'}
            placeholder="sk-..."
            className="w-full px-4 py-2 bg-[#0D2137] border border-[#00D9FF]/20 rounded-lg text-white placeholder-[#B2BAC2]/50"
          />
        </div>

        <div className="p-4 rounded-xl border border-[#00D9FF]/10">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Key className="w-4 h-4 text-purple-400" />
              <span className="text-white font-medium"> Anthropic API Key</span>
            </div>
            <button className="text-[#B2BAC2] hover:text-white transition-colors">
              <Eye className="w-4 h-4" />
            </button>
          </div>
          <input
            type="password"
            placeholder="sk-ant-..."
            className="w-full px-4 py-2 bg-[#0D2137] border border-[#00D9FF]/20 rounded-lg text-white placeholder-[#B2BAC2]/50"
          />
        </div>
      </div>

      <button className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-[#00D9FF] to-[#0066FF] rounded-lg text-white hover:opacity-90 transition-opacity">
        <Save className="w-4 h-4" />
        保存密钥
      </button>
    </div>
  )
}

function ChannelSettings() {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-white mb-1">渠道设置</h3>
        <p className="text-sm text-[#B2BAC2]/70">配置消息接收渠道</p>
      </div>

      <div className="space-y-3">
        {[
          { name: '控制台', desc: '本地控制台输入输出', enabled: true },
          { name: '钉钉', desc: '钉钉自定义机器人', enabled: false },
          { name: '飞书', desc: '飞书自定义机器人', enabled: false },
          { name: '企业微信', desc: '企业微信应用消息', enabled: false },
        ].map((channel) => (
          <div
            key={channel.name}
            className="flex items-center justify-between p-4 rounded-xl border border-[#00D9FF]/10"
          >
            <div>
              <h4 className="text-white font-medium">{channel.name}</h4>
              <p className="text-xs text-[#B2BAC2]/70">{channel.desc}</p>
            </div>
            <button className="flex items-center gap-2 text-[#B2BAC2] hover:text-white transition-colors">
              <span className="text-sm">{channel.enabled ? '已启用' : '配置'}</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}

function NotificationSettings() {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-white mb-1">通知设置</h3>
        <p className="text-sm text-[#B2BAC2]/70">配置系统通知方式</p>
      </div>

      <div className="space-y-4">
        {[
          { label: '新消息通知', desc: '收到新消息时推送通知' },
          { label: '错误告警', desc: '系统错误时发送告警' },
          { label: '每日报告', desc: '每日发送运行报告' },
        ].map((item) => (
          <div
            key={item.label}
            className="flex items-center justify-between p-4 rounded-xl border border-[#00D9FF]/10"
          >
            <div>
              <h4 className="text-white font-medium">{item.label}</h4>
              <p className="text-xs text-[#B2BAC2]/70">{item.desc}</p>
            </div>
            <button className="w-12 h-6 rounded-full bg-[#00D9FF] relative">
              <span className="absolute right-1 top-1 w-4 h-4 rounded-full bg-white" />
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}

function SecuritySettings() {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-white mb-1">安全设置</h3>
        <p className="text-sm text-[#B2BAC2]/70">保护你的账户和数据安全</p>
      </div>

      <div className="space-y-4">
        <div className="p-4 rounded-xl border border-[#00D9FF]/10">
          <h4 className="text-white font-medium mb-3">两因素认证</h4>
          <p className="text-sm text-[#B2BAC2]/70 mb-3">
            为你的账户添加额外的安全保护
          </p>
          <button className="px-4 py-2 rounded-lg border border-[#00D9FF]/30 text-[#00D9FF] hover:bg-[#00D9FF]/10 transition-colors">
            启用 2FA
          </button>
        </div>

        <div className="p-4 rounded-xl border border-[#00D9FF]/10">
          <h4 className="text-white font-medium mb-3">会话管理</h4>
          <p className="text-sm text-[#B2BAC2]/70 mb-3">查看和管理当前登录的设备</p>
          <button className="px-4 py-2 rounded-lg border border-[#00D9FF]/30 text-[#00D9FF] hover:bg-[#00D9FF]/10 transition-colors">
            查看会话
          </button>
        </div>
      </div>
    </div>
  )
}

function AppearanceSettings() {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-white mb-1">外观设置</h3>
        <p className="text-sm text-[#B2BAC2]/70">自定义界面外观</p>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-sm text-[#B2BAC2] mb-2">主题</label>
          <div className="grid grid-cols-3 gap-3">
            <button className="p-4 rounded-xl border-2 border-[#00D9FF] bg-[#0D2137]">
              <div className="text-white text-sm font-medium">深色</div>
            </button>
            <button className="p-4 rounded-xl border border-[#00D9FF]/20 bg-white/5">
              <div className="text-[#B2BAC2] text-sm font-medium">浅色</div>
            </button>
            <button className="p-4 rounded-xl border border-[#00D9FF]/20 bg-white/5">
              <div className="text-[#B2BAC2] text-sm font-medium">自动</div>
            </button>
          </div>
        </div>

        <div>
          <label className="block text-sm text-[#B2BAC2] mb-2">语言</label>
          <select className="w-full px-4 py-2 bg-[#0D2137] border border-[#00D9FF]/20 rounded-lg text-white">
            <option>简体中文</option>
            <option>English</option>
          </select>
        </div>
      </div>

      <button className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-[#00D9FF] to-[#0066FF] rounded-lg text-white hover:opacity-90 transition-opacity">
        <Check className="w-4 h-4" />
        保存设置
      </button>
    </div>
  )
}
