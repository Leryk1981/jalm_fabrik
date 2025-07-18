import { Link, useLocation } from 'react-router-dom'
import { 
  HomeIcon, 
  ShoppingBagIcon, 
  ChartBarIcon, 
  CogIcon, 
  RocketLaunchIcon,
  XMarkIcon
} from '@heroicons/react/24/outline'
import { useSidebarStore } from '@/stores/sidebarStore'

const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Marketplace', href: '/marketplace', icon: ShoppingBagIcon },
  { name: 'Research Analytics', href: '/research', icon: ChartBarIcon },
  { name: 'Service Management', href: '/services', icon: CogIcon },
  { name: 'Deployment', href: '/deployment', icon: RocketLaunchIcon },
]

export function Sidebar() {
  const { isOpen, close } = useSidebarStore()
  const location = useLocation()

  return (
    <>
      {/* Overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 z-30 bg-gray-600 bg-opacity-75 lg:hidden"
          onClick={close}
        />
      )}
      
      {/* Sidebar */}
      <div className={`sidebar ${isOpen ? 'sidebar-open' : ''} lg:translate-x-0`}>
        <div className="flex h-full flex-col bg-white">
          {/* Header */}
          <div className="flex h-16 items-center justify-between px-6 border-b border-gray-200">
            <div className="flex items-center">
              <div className="h-8 w-8 rounded-lg bg-primary-600 flex items-center justify-center">
                <span className="text-white font-bold text-sm">J</span>
              </div>
              <span className="ml-3 text-lg font-semibold text-gray-900">
                JALM Market
              </span>
            </div>
            <button
              onClick={close}
              className="lg:hidden rounded-md p-1 text-gray-400 hover:text-gray-500 hover:bg-gray-100"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-1 px-3 py-4">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                    isActive
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                  onClick={close}
                >
                  <item.icon
                    className={`mr-3 h-5 w-5 flex-shrink-0 ${
                      isActive ? 'text-primary-500' : 'text-gray-400 group-hover:text-gray-500'
                    }`}
                  />
                  {item.name}
                </Link>
              )
            })}
          </nav>

          {/* Footer */}
          <div className="border-t border-gray-200 p-4">
            <div className="text-xs text-gray-500">
              <p>JALM Full Stack</p>
              <p>v1.0.0</p>
            </div>
          </div>
        </div>
      </div>
    </>
  )
} 