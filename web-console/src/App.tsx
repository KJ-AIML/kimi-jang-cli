import { Routes, Route, Link, useLocation } from 'react-router-dom'
import { LayoutDashboard, Users, ClipboardList, BookOpen, Settings } from 'lucide-react'
import Dashboard from './pages/Dashboard'
import Tasks from './pages/Tasks'
import Knowledge from './pages/Knowledge'
import Agents from './pages/Agents'

function App() {
  const location = useLocation()
  
  const navItems = [
    { path: '/', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/tasks', label: 'Tasks', icon: ClipboardList },
    { path: '/knowledge', label: 'Knowledge', icon: BookOpen },
    { path: '/agents', label: 'Agents', icon: Users },
  ]

  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <aside className="w-64 bg-[var(--bg-secondary)] border-r border-[var(--border)] flex flex-col">
        <div className="p-4 border-b border-[var(--border)]">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-violet-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold">K</span>
            </div>
            <div>
              <h1 className="font-bold text-lg">Kimijang</h1>
              <p className="text-xs text-[var(--text-secondary)]">Console</p>
            </div>
          </div>
        </div>
        
        <nav className="flex-1 p-4">
          <ul className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.path
              return (
                <li key={item.path}>
                  <Link
                    to={item.path}
                    className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                      isActive 
                        ? 'bg-violet-500/20 text-violet-400' 
                        : 'text-[var(--text-secondary)] hover:text-white hover:bg-[var(--bg-tertiary)]'
                    }`}
                  >
                    <Icon size={18} />
                    {item.label}
                  </Link>
                </li>
              )
            })}
          </ul>
        </nav>
        
        <div className="p-4 border-t border-[var(--border)]">
          <button className="flex items-center gap-3 px-3 py-2 text-[var(--text-secondary)] hover:text-white transition-colors">
            <Settings size={18} />
            Settings
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/tasks" element={<Tasks />} />
          <Route path="/knowledge" element={<Knowledge />} />
          <Route path="/agents" element={<Agents />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
