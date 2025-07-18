import { 
  ServerIcon, 
  ShoppingBagIcon, 
  ChartBarIcon, 
  RocketLaunchIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline'

const stats = [
  { name: 'Активные сервисы', value: '4', icon: ServerIcon, change: '+2', changeType: 'positive' },
  { name: 'Шаблоны', value: '12', icon: ShoppingBagIcon, change: '+3', changeType: 'positive' },
  { name: 'Функции', value: '28', icon: ChartBarIcon, change: '+5', changeType: 'positive' },
  { name: 'Деплойменты', value: '8', icon: RocketLaunchIcon, change: '+1', changeType: 'positive' },
]

const recentDeployments = [
  { id: 1, name: 'Booking App', status: 'completed', progress: 100, time: '2 мин назад' },
  { id: 2, name: 'E-commerce Platform', status: 'running', progress: 75, time: '5 мин назад' },
  { id: 3, name: 'Analytics Dashboard', status: 'failed', progress: 45, time: '10 мин назад' },
]

const serviceStatus = [
  { name: 'Core Runner', status: 'running', health: 'healthy' },
  { name: 'Research API', status: 'running', health: 'healthy' },
  { name: 'Tula Spec', status: 'running', health: 'healthy' },
  { name: 'Shablon Spec', status: 'stopped', health: 'unhealthy' },
]

function getStatusIcon(status: string) {
  switch (status) {
    case 'completed':
      return <CheckCircleIcon className="h-5 w-5 text-green-500" />
    case 'running':
      return <div className="h-5 w-5 rounded-full bg-blue-500 animate-pulse" />
    case 'failed':
      return <XCircleIcon className="h-5 w-5 text-red-500" />
    default:
      return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />
  }
}

function getHealthColor(health: string) {
  switch (health) {
    case 'healthy':
      return 'text-green-600 bg-green-100'
    case 'unhealthy':
      return 'text-red-600 bg-red-100'
    default:
      return 'text-yellow-600 bg-yellow-100'
  }
}

export function Dashboard() {
  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>
        <p className="text-gray-600">Обзор состояния JALM экосистемы</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((item) => (
          <div key={item.name} className="card p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <item.icon className="h-8 w-8 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">{item.name}</dt>
                  <dd className="flex items-baseline">
                    <div className="text-2xl font-semibold text-gray-900">{item.value}</div>
                    <div className={`ml-2 flex items-baseline text-sm font-semibold ${
                      item.changeType === 'positive' ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {item.change}
                    </div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Recent Deployments */}
        <div className="card">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Последние деплойменты</h3>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {recentDeployments.map((deployment) => (
                <div key={deployment.id} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    {getStatusIcon(deployment.status)}
                    <div>
                      <p className="text-sm font-medium text-gray-900">{deployment.name}</p>
                      <p className="text-xs text-gray-500">{deployment.time}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-16 bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${
                          deployment.status === 'completed' ? 'bg-green-500' :
                          deployment.status === 'running' ? 'bg-blue-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${deployment.progress}%` }}
                      />
                    </div>
                    <span className="text-xs text-gray-500">{deployment.progress}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Service Status */}
        <div className="card">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Статус сервисов</h3>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {serviceStatus.map((service) => (
                <div key={service.name} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={`h-3 w-3 rounded-full ${
                      service.status === 'running' ? 'bg-green-500' : 'bg-red-500'
                    }`} />
                    <div>
                      <p className="text-sm font-medium text-gray-900">{service.name}</p>
                      <p className="text-xs text-gray-500 capitalize">{service.status}</p>
                    </div>
                  </div>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getHealthColor(service.health)}`}>
                    {service.health}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Быстрые действия</h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <button className="flex items-center justify-center px-4 py-3 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
              <RocketLaunchIcon className="h-5 w-5 mr-2" />
              Новый деплоймент
            </button>
            <button className="flex items-center justify-center px-4 py-3 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
              <ShoppingBagIcon className="h-5 w-5 mr-2" />
              Просмотр шаблонов
            </button>
            <button className="flex items-center justify-center px-4 py-3 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
              <ChartBarIcon className="h-5 w-5 mr-2" />
              Аналитика
            </button>
            <button className="flex items-center justify-center px-4 py-3 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
              <ServerIcon className="h-5 w-5 mr-2" />
              Управление сервисами
            </button>
          </div>
        </div>
      </div>
    </div>
  )
} 