export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
  channel?: string
}

export interface Session {
  id: string
  title: string
  messages: Message[]
  createdAt: string
  updatedAt: string
  channel: string
}

export interface Plugin {
  id: string
  name: string
  type: 'channel' | 'tool' | 'provider'
  description: string
  enabled: boolean
  version: string
  author?: string
  config?: Record<string, unknown>
}

export interface Channel extends Plugin {
  type: 'channel'
  platform: 'dingtalk' | 'feishu' | 'wecom' | 'telegram' | 'discord' | 'slack' | 'console'
}

export interface Tool extends Plugin {
  type: 'tool'
  parameters?: {
    name: string
    type: string
    required: boolean
    description: string
  }[]
}

export interface KnowledgeBase {
  id: string
  name: string
  description: string
  documentCount: number
  createdAt: string
  updatedAt: string
}

export interface ModelProvider {
  id: string
  name: string
  type: 'openai' | 'ollama' | 'anthropic' | 'deepseek' | 'qwen'
  apiKey?: string
  baseUrl?: string
  model: string
  enabled: boolean
}

export interface AgentStatus {
  running: boolean
  model: string
  sessionCount: number
  messageCount: number
  uptime: string
}

export interface WorkflowNode {
  id: string
  type: 'agent' | 'tool' | 'condition' | 'transform'
  name: string
  config: Record<string, unknown>
}

export interface Workflow {
  id: string
  name: string
  nodes: WorkflowNode[]
  edges: { source: string; target: string }[]
  enabled: boolean
  createdAt: string
}
