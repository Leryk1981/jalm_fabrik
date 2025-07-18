// Основные типы для JALM экосистемы
export interface Service {
  id: string
  name: string
  status: 'running' | 'stopped' | 'error' | 'starting'
  type: 'core-runner' | 'research' | 'tula-spec' | 'shablon-spec'
  port: number
  url: string
  health: {
    status: 'healthy' | 'unhealthy' | 'unknown'
    lastCheck: string
    responseTime: number
  }
  metrics: {
    cpu: number
    memory: number
    requests: number
  }
}

export interface Template {
  id: string
  name: string
  description: string
  category: string
  tags: string[]
  version: string
  author: string
  rating: number
  downloads: number
  price: number
  isFree: boolean
  features: string[]
  requirements: string[]
  demoUrl?: string
  documentationUrl?: string
}

export interface Function {
  id: string
  name: string
  description: string
  category: string
  tags: string[]
  version: string
  author: string
  rating: number
  usage: number
  price: number
  isFree: boolean
  parameters: FunctionParameter[]
  returnType: string
  examples: FunctionExample[]
}

export interface FunctionParameter {
  name: string
  type: string
  required: boolean
  description: string
  defaultValue?: any
}

export interface FunctionExample {
  title: string
  description: string
  code: string
  result: string
}

export interface ResearchData {
  id: string
  timestamp: string
  source: string
  type: 'pattern' | 'action' | 'template' | 'function'
  data: any
  metadata: {
    confidence: number
    tags: string[]
    category: string
  }
}

export interface Deployment {
  id: string
  name: string
  template: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress: number
  createdAt: string
  completedAt?: string
  config: Record<string, any>
  logs: DeploymentLog[]
}

export interface DeploymentLog {
  timestamp: string
  level: 'info' | 'warning' | 'error'
  message: string
  details?: any
}

export interface User {
  id: string
  name: string
  email: string
  role: 'admin' | 'user' | 'developer'
  avatar?: string
  preferences: UserPreferences
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'system'
  language: string
  notifications: {
    email: boolean
    push: boolean
    sms: boolean
  }
}

export interface Notification {
  id: string
  type: 'info' | 'success' | 'warning' | 'error'
  title: string
  message: string
  timestamp: string
  read: boolean
  action?: {
    label: string
    url: string
  }
}

// API Response типы
export interface ApiResponse<T> {
  success: boolean
  data: T
  message?: string
  error?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  limit: number
  pages: number
}

// Состояние приложения
export interface AppState {
  user: User | null
  services: Service[]
  notifications: Notification[]
  isLoading: boolean
  error: string | null
}

// Навигация
export interface NavigationItem {
  id: string
  label: string
  path: string
  icon: string
  badge?: number
  children?: NavigationItem[]
}

// Фильтры и поиск
export interface SearchFilters {
  query: string
  category?: string
  tags?: string[]
  priceRange?: [number, number]
  rating?: number
  sortBy?: 'name' | 'rating' | 'downloads' | 'price' | 'date'
  sortOrder?: 'asc' | 'desc'
}

// Графики и аналитика
export interface ChartData {
  labels: string[]
  datasets: {
    label: string
    data: number[]
    backgroundColor?: string
    borderColor?: string
  }[]
}

export interface AnalyticsData {
  totalServices: number
  activeServices: number
  totalTemplates: number
  totalFunctions: number
  totalDeployments: number
  successfulDeployments: number
  failedDeployments: number
  averageResponseTime: number
  totalRequests: number
  chartData: ChartData
} 