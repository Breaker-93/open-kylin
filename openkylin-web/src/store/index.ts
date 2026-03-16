import { create } from 'zustand'
import type { Session, Plugin, KnowledgeBase, ModelProvider, AgentStatus, Message } from '../types'
import { generateId } from '../lib/utils'

interface AppState {
  // Agent状态
  agentStatus: AgentStatus
  setAgentStatus: (status: Partial<AgentStatus>) => void

  // 会话
  sessions: Session[]
  currentSession: Session | null
  addSession: (session: Omit<Session, 'id' | 'createdAt' | 'updatedAt'>) => void
  setCurrentSession: (session: Session | null) => void
  addMessage: (sessionId: string, message: Omit<Message, 'id' | 'timestamp'>) => void

  // 插件
  plugins: Plugin[]
  togglePlugin: (id: string) => void
  addPlugin: (plugin: Omit<Plugin, 'id'>) => void

  // 知识库
  knowledgeBases: KnowledgeBase[]
  addKnowledgeBase: (kb: Omit<KnowledgeBase, 'id' | 'createdAt' | 'updatedAt' | 'documentCount'>) => void

  // 模型
  providers: ModelProvider[]
  setProvider: (provider: Partial<ModelProvider> & { id: string }) => void
  activeProvider: string | null
  setActiveProvider: (id: string) => void
}

export const useStore = create<AppState>((set) => ({
  // Agent状态
  agentStatus: {
    running: false,
    model: 'gpt-4',
    sessionCount: 0,
    messageCount: 0,
    uptime: '0:00:00',
  },
  setAgentStatus: (status) =>
    set((state) => ({ agentStatus: { ...state.agentStatus, ...status } })),

  // 会话
  sessions: [],
  currentSession: null,
  addSession: (session) =>
    set((state) => {
      const newSession: Session = {
        ...session,
        id: generateId(),
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        messages: [],
      }
      return {
        sessions: [newSession, ...state.sessions],
        currentSession: newSession,
      }
    }),
  setCurrentSession: (session) => set({ currentSession: session }),
  addMessage: (sessionId, message) =>
    set((state) => {
      const newMessage: Message = {
        ...message,
        id: generateId(),
        timestamp: new Date().toISOString(),
      }
      const sessions = state.sessions.map((s) =>
        s.id === sessionId
          ? { ...s, messages: [...s.messages, newMessage], updatedAt: new Date().toISOString() }
          : s
      )
      const currentSession =
        state.currentSession?.id === sessionId
          ? { ...state.currentSession, messages: [...state.currentSession.messages, newMessage] }
          : state.currentSession
      return { sessions, currentSession }
    }),

  // 插件
  plugins: [
    {
      id: '1',
      name: '控制台渠道',
      type: 'channel',
      description: '本地控制台输入输出',
      enabled: true,
      version: '1.0.0',
    },
    {
      id: '2',
      name: '钉钉机器人',
      type: 'channel',
      description: '钉钉自定义机器人接入',
      enabled: false,
      version: '1.0.0',
    },
    {
      id: '3',
      name: '飞书机器人',
      type: 'channel',
      description: '飞书自定义机器人接入',
      enabled: false,
      version: '1.0.0',
    },
    {
      id: '4',
      name: '搜索工具',
      type: 'tool',
      description: '网络搜索工具',
      enabled: true,
      version: '1.0.0',
    },
    {
      id: '5',
      name: '计算器',
      type: 'tool',
      description: '数学计算工具',
      enabled: true,
      version: '1.0.0',
    },
  ],
  togglePlugin: (id) =>
    set((state) => ({
      plugins: state.plugins.map((p) => (p.id === id ? { ...p, enabled: !p.enabled } : p)),
    })),
  addPlugin: (plugin) =>
    set((state) => ({
      plugins: [...state.plugins, { ...plugin, id: generateId() }],
    })),

  // 知识库
  knowledgeBases: [
    {
      id: '1',
      name: '产品文档',
      description: '产品使用文档和API参考',
      documentCount: 156,
      createdAt: '2024-01-15T10:00:00Z',
      updatedAt: '2024-01-20T15:30:00Z',
    },
    {
      id: '2',
      name: '常见问题',
      description: '用户常见问题解答',
      documentCount: 89,
      createdAt: '2024-01-10T08:00:00Z',
      updatedAt: '2024-01-18T12:00:00Z',
    },
  ],
  addKnowledgeBase: (kb) =>
    set((state) => ({
      knowledgeBases: [
        ...state.knowledgeBases,
        {
          ...kb,
          id: generateId(),
          documentCount: 0,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
      ],
    })),

  // 模型
  providers: [
    {
      id: '1',
      name: 'OpenAI',
      type: 'openai',
      apiKey: '',
      model: 'gpt-4',
      enabled: true,
    },
    {
      id: '2',
      name: 'Ollama',
      type: 'ollama',
      baseUrl: 'http://localhost:11434',
      model: 'llama2',
      enabled: false,
    },
  ],
  setProvider: (provider) =>
    set((state) => ({
      providers: state.providers.map((p) => (p.id === provider.id ? { ...p, ...provider } : p)),
    })),
  activeProvider: '1',
  setActiveProvider: (id) => set({ activeProvider: id }),
}))
