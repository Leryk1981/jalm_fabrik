import { MagnifyingGlassIcon, FunnelIcon } from '@heroicons/react/24/outline'

const templates = [
  {
    id: 1,
    name: 'Booking Light',
    description: 'Легкая система бронирования для малого бизнеса',
    category: 'Booking',
    price: 0,
    isFree: true,
    rating: 4.8,
    downloads: 1250,
    tags: ['booking', 'light', 'small-business'],
    features: ['Online booking', 'Calendar integration', 'Email notifications']
  },
  {
    id: 2,
    name: 'E-commerce Pro',
    description: 'Полнофункциональная платформа электронной коммерции',
    category: 'E-commerce',
    price: 99,
    isFree: false,
    rating: 4.9,
    downloads: 890,
    tags: ['ecommerce', 'pro', 'full-featured'],
    features: ['Product catalog', 'Payment processing', 'Inventory management']
  },
  {
    id: 3,
    name: 'Analytics Dashboard',
    description: 'Панель аналитики с интерактивными графиками',
    category: 'Analytics',
    price: 49,
    isFree: false,
    rating: 4.7,
    downloads: 567,
    tags: ['analytics', 'dashboard', 'charts'],
    features: ['Real-time data', 'Interactive charts', 'Export reports']
  }
]

const functions = [
  {
    id: 1,
    name: 'Slot Validator',
    description: 'Валидация временных слотов для бронирования',
    category: 'Validation',
    price: 0,
    isFree: true,
    rating: 4.6,
    usage: 2340,
    tags: ['validation', 'booking', 'slots']
  },
  {
    id: 2,
    name: 'Notify System',
    description: 'Система уведомлений с поддержкой email и SMS',
    category: 'Notifications',
    price: 29,
    isFree: false,
    rating: 4.8,
    usage: 1567,
    tags: ['notifications', 'email', 'sms']
  },
  {
    id: 3,
    name: 'Booking Widget',
    description: 'Встраиваемый виджет для бронирования',
    category: 'Widgets',
    price: 19,
    isFree: false,
    rating: 4.5,
    usage: 892,
    tags: ['widget', 'booking', 'embed']
  }
]

export function Marketplace() {
  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Marketplace</h2>
        <p className="text-gray-600">Каталог готовых решений и компонентов</p>
      </div>

      {/* Search and filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Поиск шаблонов и функций..."
            className="input pl-10"
          />
        </div>
        <button className="btn-secondary flex items-center">
          <FunnelIcon className="h-5 w-5 mr-2" />
          Фильтры
        </button>
      </div>

      {/* Templates section */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Шаблоны</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {templates.map((template) => (
            <div key={template.id} className="card hover:shadow-md transition-shadow">
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h4 className="text-lg font-semibold text-gray-900">{template.name}</h4>
                    <p className="text-sm text-gray-500">{template.category}</p>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-gray-900">
                      {template.isFree ? 'Бесплатно' : `$${template.price}`}
                    </div>
                    <div className="flex items-center text-sm text-gray-500">
                      <span>★ {template.rating}</span>
                      <span className="mx-1">•</span>
                      <span>{template.downloads} загрузок</span>
                    </div>
                  </div>
                </div>
                
                <p className="text-gray-600 mb-4">{template.description}</p>
                
                <div className="flex flex-wrap gap-1 mb-4">
                  {template.tags.slice(0, 3).map((tag) => (
                    <span
                      key={tag}
                      className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
                
                <div className="space-y-2 mb-4">
                  {template.features.slice(0, 2).map((feature) => (
                    <div key={feature} className="flex items-center text-sm text-gray-600">
                      <div className="h-1.5 w-1.5 rounded-full bg-green-500 mr-2" />
                      {feature}
                    </div>
                  ))}
                </div>
                
                <button className="w-full btn-primary">
                  {template.isFree ? 'Использовать' : 'Купить'}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Functions section */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Функции</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {functions.map((func) => (
            <div key={func.id} className="card hover:shadow-md transition-shadow">
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h4 className="text-lg font-semibold text-gray-900">{func.name}</h4>
                    <p className="text-sm text-gray-500">{func.category}</p>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-gray-900">
                      {func.isFree ? 'Бесплатно' : `$${func.price}`}
                    </div>
                    <div className="flex items-center text-sm text-gray-500">
                      <span>★ {func.rating}</span>
                      <span className="mx-1">•</span>
                      <span>{func.usage} использований</span>
                    </div>
                  </div>
                </div>
                
                <p className="text-gray-600 mb-4">{func.description}</p>
                
                <div className="flex flex-wrap gap-1 mb-4">
                  {func.tags.map((tag) => (
                    <span
                      key={tag}
                      className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
                
                <button className="w-full btn-primary">
                  {func.isFree ? 'Добавить' : 'Купить'}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
} 