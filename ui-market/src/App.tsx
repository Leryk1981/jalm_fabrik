import { Routes, Route } from 'react-router-dom'
import { Sidebar } from '@/components/common/Sidebar'
import { Header } from '@/components/common/Header'
import { Dashboard } from '@/pages/Dashboard'
import { Marketplace } from '@/pages/Marketplace'
import { ResearchAnalytics } from '@/pages/ResearchAnalytics'
import { ServiceManagement } from '@/pages/ServiceManagement'
import { Deployment } from '@/pages/Deployment'
import { useSidebarStore } from '@/stores/sidebarStore'

function App() {
  const { isOpen } = useSidebarStore()

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />
      <div className={`main-content ${isOpen ? 'main-content-sidebar-open' : ''}`}>
        <Header />
        <main className="p-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/marketplace" element={<Marketplace />} />
            <Route path="/research" element={<ResearchAnalytics />} />
            <Route path="/services" element={<ServiceManagement />} />
            <Route path="/deployment" element={<Deployment />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}

export default App 