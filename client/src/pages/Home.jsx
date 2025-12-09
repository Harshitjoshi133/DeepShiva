import { Link } from 'react-router-dom'
import { Users, Activity, AlertCircle, Mountain, Sparkles } from 'lucide-react'
import { motion } from 'framer-motion'

export default function Home() {
  const quickActions = [
    { icon: Users, label: 'Check Crowd Status', path: '/dashboard', color: 'bg-blue-500' },
    { icon: Activity, label: 'Yoga Mode', path: '/yoga-sentinel', color: 'bg-green-500' },
    { icon: AlertCircle, label: 'Emergency Help', path: '/emergency', color: 'bg-red-500' },
  ]

  return (
    <div className="max-w-6xl mx-auto">
      {/* Hero Section */}
      <motion.div 
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-12"
      >
        <div className="flex justify-center mb-6">
          <Mountain size={80} className="text-saffron" />
        </div>
        <h1 className="text-4xl lg:text-6xl font-bold text-gray-800 mb-4">
          Plan Your Yatra to <span className="text-saffron">Uttarakhand</span>
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Your AI-powered spiritual guide for eco-tourism, yoga, and sacred journeys
        </p>
        <Link to="/chat" className="btn-primary inline-flex items-center gap-2 text-lg">
          <Sparkles size={24} />
          Start Your Journey
        </Link>
      </motion.div>

      {/* Quick Actions */}
      <div className="mb-12">
        <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {quickActions.map((action, index) => {
            const Icon = action.icon
            return (
              <motion.div
                key={action.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Link to={action.path} className="card hover:scale-105 transition-transform">
                  <div className={`${action.color} w-16 h-16 rounded-full flex items-center justify-center mb-4 mx-auto`}>
                    <Icon size={32} className="text-white" />
                  </div>
                  <h3 className="text-xl font-semibold text-center text-gray-800">{action.label}</h3>
                </Link>
              </motion.div>
            )
          })}
        </div>
      </div>

      {/* Features */}
      <div className="card bg-gradient-to-r from-saffron to-orange-400 text-white">
        <h2 className="text-3xl font-bold mb-6">Why Deep-Shiva?</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-xl font-semibold mb-2">🙏 Spiritual Guidance</h3>
            <p>Get personalized yatra recommendations and spiritual insights</p>
          </div>
          <div>
            <h3 className="text-xl font-semibold mb-2">🧘 Yoga Correction</h3>
            <p>Real-time posture analysis using AI vision technology</p>
          </div>
          <div>
            <h3 className="text-xl font-semibold mb-2">🌱 Eco-Tourism</h3>
            <p>Calculate your carbon footprint and travel sustainably</p>
          </div>
          <div>
            <h3 className="text-xl font-semibold mb-2">🎨 Local Culture</h3>
            <p>Discover and support local artisans and traditions</p>
          </div>
        </div>
      </div>
    </div>
  )
}
