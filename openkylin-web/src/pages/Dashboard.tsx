import { Bot, MessageSquare, Clock, Activity, Play, Square } from 'lucide-react'
import { useStore } from '../store'
import { XAxis, YAxis, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts'

const mockChartData = [
  { time: '00:00', messages: 12 },
  { time: '04:00', messages: 8 },
  { time: '08:00', messages: 25 },
  { time: '12:00', messages: 45 },
  { time: '16:00', messages: 38 },
  { time: '20:00', messages: 28 },
  { time: '24:00', messages: 15 },
]

const recentActivities = [
  { id: 1, action: '处理用户消息', time: '2分钟前', status: 'success' },
  { id: 2, action: '调用搜索工具', time: '5分钟前', status: 'success' },
  { id: 3, action: '知识库检索', time: '8分钟前', status: 'success' },
  { id: 4, action: '模型响应生成', time: '10分钟前', status: 'success' },
  { id: 5, action: '新会话创建', time: '15分钟前', status: 'success' },
]

export function Dashboard() {
  const { agentStatus, setAgentStatus, sessions } = useStore()

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">仪表盘</h1>
          <p className="text-[#B2BAC2] mt-1">实时监控 AI 智能体运行状态</p>
        </div>
        <button
          onClick={() => setAgentStatus({ running: !agentStatus.running })}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${
            agentStatus.running
              ? 'bg-red-500/20 text-red-400 hover:bg-red-500/30'
              : 'bg-[#00D9FF]/20 text-[#00D9FF] hover:bg-[#00D9FF]/30'
          }`}
        >
          {agentStatus.running ? (
            <>
              <Square className="w-4 h-4" /> 停止服务
            </>
          ) : (
            <>
              <Play className="w-4 h-4" /> 启动服务
            </>
          )}
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={Bot}
          label="Agent 状态"
          value={agentStatus.running ? '运行中' : '已停止'}
          color={agentStatus.running ? 'text-emerald-400' : 'text-red-400'}
          bgColor={agentStatus.running ? 'bg-emerald-500/10' : 'bg-red-500/10'}
        />
        <StatCard
          icon={MessageSquare}
          label="活跃会话"
          value={String(sessions.length || 0)}
          color="text-[#00D9FF]"
          bgColor="bg-[#00D9FF]/10"
        />
        <StatCard
          icon={Activity}
          label="今日消息"
          value="186"
          color="text-purple-400"
          bgColor="bg-purple-500/10"
        />
        <StatCard
          icon={Clock}
          label="运行时间"
          value={agentStatus.uptime}
          color="text-amber-400"
          bgColor="bg-amber-500/10"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-[#0A1929]/50 rounded-xl p-5 border border-[#00D9FF]/10">
          <h3 className="text-lg font-semibold text-white mb-4">消息趋势</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={mockChartData}>
                <defs>
                  <linearGradient id="colorMessages" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00D9FF" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#00D9FF" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="time" stroke="#B2BAC2" fontSize={12} />
                <YAxis stroke="#B2BAC2" fontSize={12} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0A1929',
                    border: '1px solid #00D9FF20',
                    borderRadius: '8px',
                  }}
                  labelStyle={{ color: '#fff' }}
                />
                <Area
                  type="monotone"
                  dataKey="messages"
                  stroke="#00D9FF"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#colorMessages)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-[#0A1929]/50 rounded-xl p-5 border border-[#00D9FF]/10">
          <h3 className="text-lg font-semibold text-white mb-4">最近活动</h3>
          <div className="space-y-3">
            {recentActivities.map((activity) => (
              <div
                key={activity.id}
                className="flex items-center justify-between p-3 rounded-lg bg-[#0D2137]/50 hover:bg-[#0D2137]/70 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-emerald-400" />
                  <span className="text-[#B2BAC2]">{activity.action}</span>
                </div>
                <span className="text-xs text-[#B2BAC2]/60">{activity.time}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-[#0A1929]/50 rounded-xl p-5 border border-[#00D9FF]/10">
        <h3 className="text-lg font-semibold text-white mb-4">快速操作</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <QuickActionButton label="新建会话" color="from-[#00D9FF] to-[#0066FF]" />
          <QuickActionButton label="导入知识库" color="from-purple-500 to-purple-600" />
          <QuickActionButton label="配置插件" color="from-amber-500 to-amber-600" />
          <QuickActionButton label="查看日志" color="from-emerald-500 to-emerald-600" />
        </div>
      </div>
    </div>
  )
}

function StatCard({
  icon: Icon,
  label,
  value,
  color,
  bgColor,
}: {
  icon: typeof Bot
  label: string
  value: string
  color: string
  bgColor: string
}) {
  return (
    <div className="bg-[#0A1929]/50 rounded-xl p-5 border border-[#00D9FF]/10 hover:border-[#00D9FF]/30 transition-all">
      <div className="flex items-center gap-4">
        <div className={`p-3 rounded-xl ${bgColor}`}>
          <Icon className={`w-6 h-6 ${color}`} />
        </div>
        <div>
          <p className="text-sm text-[#B2BAC2]">{label}</p>
          <p className={`text-2xl font-bold ${color}`}>{value}</p>
        </div>
      </div>
    </div>
  )
}

function QuickActionButton({ label, color }: { label: string; color: string }) {
  return (
    <button className={`p-4 rounded-xl bg-gradient-to-r ${color} hover:opacity-90 transition-opacity`}>
      <span className="text-white font-medium">{label}</span>
    </button>
  )
}
