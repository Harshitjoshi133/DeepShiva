import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Home, MessageCircle, Activity, BarChart3, Palette, AlertCircle, Menu, X, Globe } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { useLanguage } from '../contexts/LanguageContext'

export default function Layout({ children }) {
  const location = useLocation()
  const { language, changeLanguage, t } = useLanguage()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const navItems = [
    { path: '/', icon: Home, label: t('nav.home', 'Home') },
    { path: '/chat', icon: MessageCircle, label: t('nav.chat', 'Chat') },
    { path: '/yoga-sentinel', icon: Activity, label: t('nav.yoga', 'Yoga') },
    { path: '/dashboard', icon: BarChart3, label: t('nav.dashboard', 'Dashboard') },
    { path: '/culture', icon: Palette, label: t('nav.culture', 'Culture') },
    { path: '/emergency', icon: AlertCircle, label: t('nav.emergency', 'SOS') },
  ]

  const languages = {
    en: 'English',
    hi: 'हिंदी',
    ga: 'गढ़वळी'
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-white to-green-50 relative">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute top-0 left-0 w-96 h-96 bg-saffron rounded-full mix-blend-multiply filter blur-xl animate-pulse"></div>
        <div className="absolute top-0 right-0 w-96 h-96 bg-forest rounded-full mix-blend-multiply filter blur-xl animate-pulse" style={{animationDelay: '2s'}}></div>
        <div className="absolute bottom-0 left-1/2 w-96 h-96 bg-orange-300 rounded-full mix-blend-multiply filter blur-xl animate-pulse" style={{animationDelay: '4s'}}></div>
      </div>
      
      <div className="relative z-10">
      {/* Header */}
      <header className="glass-nav shadow-lg sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-3 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button 
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden p-2 hover:bg-white/20 rounded-lg transition-colors duration-200"
            >
              {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
            <div className="flex items-center gap-2">
              <img src="/images/branding/logo.svg" alt="Deep-Shiva" className="h-5 w-5" />
              <h1 className="text-lg font-bold gradient-text">Deep-Shiva</h1>
            </div>
          </div>
          
          <div className="flex items-center gap-1">
            <Globe size={16} className="text-forest" />
            <select 
              value={language}
              onChange={(e) => changeLanguage(e.target.value)}
              className="bg-white/20 backdrop-blur-sm border border-forest/30 rounded-md px-2 py-1 text-sm font-semibold text-forest focus:outline-none focus:ring-1 focus:ring-forest/50 focus:bg-white/30 transition-all duration-200"
            >
              {Object.entries(languages).map(([code, name]) => (
                <option key={code} value={code}>{name}</option>
              ))}
            </select>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Desktop Sidebar */}
        <aside className="hidden lg:block w-52 glass-sidebar shadow-xl min-h-[calc(100vh-61px)] sticky top-[61px]">
          <nav className="p-3 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.path
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center gap-2 px-3 py-2 rounded-md transition-all duration-300 ${
                    isActive 
                      ? 'bg-gradient-to-r from-saffron to-orange-500 text-white shadow-md glow-effect' 
                      : 'hover:bg-white/30 text-gray-700 hover:shadow-sm'
                  }`}
                >
                  <Icon size={16} />
                  <span className="font-medium text-sm">{item.label}</span>
                </Link>
              )
            })}
          </nav>
        </aside>

        {/* Mobile Sidebar */}
        <AnimatePresence>
          {sidebarOpen && (
            <motion.aside
              initial={{ x: -300 }}
              animate={{ x: 0 }}
              exit={{ x: -300 }}
              className="lg:hidden fixed inset-y-0 left-0 w-52 bg-white shadow-2xl z-50 top-[61px]"
            >
              <nav className="p-3 space-y-1">
                {navItems.map((item) => {
                  const Icon = item.icon
                  const isActive = location.pathname === item.path
                  return (
                    <Link
                      key={item.path}
                      to={item.path}
                      onClick={() => setSidebarOpen(false)}
                      className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                        isActive 
                          ? 'bg-saffron text-white' 
                          : 'hover:bg-gray-100 text-gray-700'
                      }`}
                    >
                      <Icon size={20} />
                      <span className="font-medium">{item.label}</span>
                    </Link>
                  )
                })}
              </nav>
            </motion.aside>
          )}
        </AnimatePresence>

        {/* Main Content */}
        <main className="flex-1 p-2 lg:p-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            {children}
          </motion.div>
        </main>
      </div>
      </div>

      {/* Mobile Bottom Navigation */}
      <nav className="lg:hidden fixed bottom-0 left-0 right-0 glass-nav border-t border-white/20 z-40">
        <div className="flex justify-around items-center py-2">
          {navItems.slice(0, 5).map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex flex-col items-center gap-1 px-3 py-2 rounded-lg transition-all duration-300 ${
                  isActive ? 'text-saffron scale-110' : 'text-gray-600 hover:text-saffron hover:scale-105'
                }`}
              >
                <Icon size={24} />
                <span className="text-xs font-medium">{item.label}</span>
              </Link>
            )
          })}
        </div>
      </nav>
    </div>
  )
}
