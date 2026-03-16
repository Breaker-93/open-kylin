import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  MessageSquare,
  Puzzle,
  BookOpen,
  Settings,
  Bot,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react'
import { cn } from '../lib/utils'
import { useState } from 'react'

const navItems = [
  { path: '/', icon: LayoutDashboard, label: '仪表盘' },
  { path: '/sessions', icon: MessageSquare, label: '会话管理' },
  { path: '/plugins', icon: Puzzle, label: '插件中心' },
  { path: '/knowledge', icon: BookOpen, label: '知识库' },
  { path: '/settings', icon: Settings, label: '设置' },
]

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false)

  return (
    <aside
      className={cn(
        'fixed left-0 top-0 h-screen bg-gradient-to-b from-[#0A1929] to-[#0D2137] border-r border-[#00D9FF]/20 transition-all duration-300 z-50',
        collapsed ? 'w-16' : 'w-64'
      )}
    >
      <div className="flex flex-col h-full">
        {/* Logo */}
        <div className="flex items-center gap-3 p-4 border-b border-[#00D9FF]/10">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#00D9FF] to-[#0066FF] flex items-center justify-center shadow-lg shadow-[#00D9FF]/20">
            <Bot className="w-6 h-6 text-white" />
          </div>
          {!collapsed && (
            <div className="flex flex-col">
              <span className="text-lg font-bold text-white">OpenKylin</span>
              <span className="text-xs text-[#00D9FF]/70">AI 智能体框架</span>
            </div>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-3 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200',
                  isActive
                    ? 'bg-[#00D9FF]/10 text-[#00D9FF] shadow-lg shadow-[#00D9FF]/5'
                    : 'text-[#B2BAC2] hover:bg-[#00D9FF]/5 hover:text-white'
                )
              }
            >
              <item.icon className="w-5 h-5 flex-shrink-0" />
              {!collapsed && <span className="font-medium">{item.label}</span>}
            </NavLink>
          ))}
        </nav>

        {/* Collapse Button */}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-3 border-t border-[#00D9FF]/10 text-[#B2BAC2] hover:text-[#00D9FF] transition-colors"
        >
          {collapsed ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
        </button>
      </div>
    </aside>
  )
}
