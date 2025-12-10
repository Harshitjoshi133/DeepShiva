import { Link } from 'react-router-dom'
import { Users, Activity, AlertCircle, Mountain, Sparkles, Heart, Palette, Leaf, Globe } from 'lucide-react'
import { motion } from 'framer-motion'

export default function Home() {
  const quickActions = [
    { icon: Users, label: 'Check Crowd Status', path: '/dashboard', color: 'bg-blue-500' },
    { icon: Activity, label: 'Yoga Mode', path: '/yoga-sentinel', color: 'bg-green-500' },
    { icon: AlertCircle, label: 'Emergency Help', path: '/emergency', color: 'bg-red-500' },
  ]

  return (
    <div className="max-w-5xl mx-auto relative">
      {/* Hero Background */}
      <div className="absolute inset-0 -z-10 rounded-2xl overflow-hidden">
        <img 
          src="/images/hero/hero-bg.png" 
          alt="Uttarakhand Mountains" 
          className="w-full h-full object-cover opacity-15"
        />
      </div>
      
      {/* Hero Section */}
      <motion.div 
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-8 relative z-10"
      >
        <div className="flex justify-center mb-4">
          <div className="floating-animation">
            <img 
              src="/images/hero/moutain-icon.svg" 
              alt="Mountain" 
              className="h-16 w-16 text-saffron pulse-glow"
            />
          </div>
        </div>
        <h1 className="text-3xl lg:text-5xl font-bold text-gray-800 mb-3">
          Plan Your Yatra to <span className="gradient-text">Uttarakhand</span>
        </h1>
        <p className="text-lg text-gray-600 mb-6">
          Your AI-powered spiritual guide for eco-tourism, yoga, and sacred journeys
        </p>
        <Link to="/chat" className="btn-primary inline-flex items-center gap-2 pulse-glow">
          <Sparkles size={20} />
          Start Your Journey
        </Link>
      </motion.div>

      {/* Quick Actions */}
      <div className="mb-8">
        <h2 className="text-xl font-bold text-gray-800 mb-4 text-center">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {quickActions.map((action, index) => {
            const Icon = action.icon
            return (
              <motion.div
                key={action.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Link to={action.path} className="glass-card hover:scale-105 transition-all duration-300 group">
                  <div className={`${action.color} w-12 h-12 rounded-full flex items-center justify-center mb-3 mx-auto shadow-lg group-hover:shadow-xl transition-shadow duration-300`}>
                    <Icon size={24} className="text-white" />
                  </div>
                  <h3 className="text-lg font-semibold text-center text-gray-800">{action.label}</h3>
                </Link>
              </motion.div>
            )
          })}
        </div>
      </div>

      {/* Features */}
      <div className="glass-card gradient-bg text-white shadow-2xl">
        <h2 className="text-2xl font-bold mb-4">Why Deep-Shiva?</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="flex items-start gap-3"
          >
            <Heart size={20} className="text-white mt-1 flex-shrink-0" />
            <div>
              <h3 className="text-lg font-semibold mb-1">Spiritual Guidance</h3>
              <p>Get personalized yatra recommendations and spiritual insights</p>
            </div>
          </motion.div>
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="flex items-start gap-3"
          >
            <Activity size={20} className="text-white mt-1 flex-shrink-0" />
            <div>
              <h3 className="text-lg font-semibold mb-1">Yoga Correction</h3>
              <p>Real-time posture analysis using AI vision technology</p>
            </div>
          </motion.div>
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="flex items-start gap-3"
          >
            <Leaf size={20} className="text-white mt-1 flex-shrink-0" />
            <div>
              <h3 className="text-lg font-semibold mb-1">Eco-Tourism</h3>
              <p>Calculate your carbon footprint and travel sustainably</p>
            </div>
          </motion.div>
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
            className="flex items-start gap-3"
          >
            <Palette size={20} className="text-white mt-1 flex-shrink-0" />
            <div>
              <h3 className="text-lg font-semibold mb-1">Local Culture</h3>
              <p>Discover and support local artisans and traditions</p>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  )
}
