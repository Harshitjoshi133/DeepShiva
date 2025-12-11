import { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { TrendingUp, Leaf, Car, Lightbulb } from 'lucide-react'
import { motion } from 'framer-motion'
import { useLanguage } from '../contexts/LanguageContext'

export default function Dashboard() {
  const { t } = useLanguage()
  const [crowdData, setCrowdData] = useState([])
  const [carbonForm, setCarbonForm] = useState({ distance: '', vehicle: 'car' })
  const [carbonResult, setCarbonResult] = useState(null)

  useEffect(() => {
    fetch('/api/v1/tourism/crowd-status')
      .then(res => res.json())
      .then(data => setCrowdData(data))
      .catch(err => console.error(err))
  }, [])

  const handleCarbonSubmit = async (e) => {
    e.preventDefault()
    try {
      const response = await fetch('/api/v1/tourism/calculate-carbon', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          distance: parseFloat(carbonForm.distance),
          vehicle_type: carbonForm.vehicle
        })
      })
      const data = await response.json()
      setCarbonResult(data)
    } catch (error) {
      console.error('Carbon calculation failed:', error)
    }
  }

  const getBarColor = (level) => {
    if (level < 40) return '#228B22'
    if (level < 70) return '#FFA500'
    return '#FF4444'
  }

  return (
    <div className="max-w-5xl mx-auto space-y-3">
      <h2 className="text-xl font-bold text-gray-800">{t('dashboard.title', 'Yatra Dashboard')}</h2>

      {/* Crowd Meter */}
      <div className="glass-card shadow-2xl">
        <div className="flex items-center gap-2 mb-3">
          <TrendingUp size={20} className="text-saffron" />
          <h3 className="text-lg font-bold gradient-text">{t('dashboard.crowdStatus', 'Live Crowd Status')}</h3>
        </div>
        
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={crowdData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="shrine" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="crowd_level" radius={[8, 8, 0, 0]}>
              {crowdData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={getBarColor(entry.crowd_level)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mt-3">
          {crowdData.map((shrine) => {
            const shrineImages = {
              'Kedarnath': '/images/shrines/kedarnath.png',
              'Badrinath': '/images/shrines/badrinath.png', 
              'Gangotri': '/images/shrines/gangotri.png',
              'Yamunotri': '/images/shrines/yamontri.png'
            }
            return (
              <div key={shrine.shrine} className="relative text-center p-2 bg-gray-50 rounded-lg overflow-hidden">
                <img 
                  src={shrineImages[shrine.shrine]}
                  alt={shrine.shrine}
                  className="absolute inset-0 w-full h-full object-cover opacity-20"
                />
                <div className="relative z-10">
                  <p className="font-semibold text-gray-800 text-xs">{shrine.shrine}</p>
                  <p className={`text-xs font-bold ${
                    shrine.status === 'Light' ? 'text-green-600' :
                    shrine.status === 'Moderate' ? 'text-orange-600' :
                    'text-red-600'
                  }`}>
                    {shrine.status}
                  </p>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Carbon Calculator */}
      <div className="glass-card shadow-2xl">
        <div className="flex items-center gap-2 mb-3">
          <Leaf size={20} className="text-forest" />
          <h3 className="text-lg font-bold gradient-text">{t('dashboard.carbonCalculator', 'Carbon Footprint Calculator')}</h3>
        </div>

        <form onSubmit={handleCarbonSubmit} className="grid md:grid-cols-3 gap-2 mb-3">
          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">
              {t('dashboard.distance', 'Distance (km)')}
            </label>
            <input
              type="number"
              value={carbonForm.distance}
              onChange={(e) => setCarbonForm({...carbonForm, distance: e.target.value})}
              className="w-full px-3 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-forest text-sm"
              placeholder={t('dashboard.distance', 'Enter distance')}
              required
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">
              {t('dashboard.vehicleType', 'Vehicle Type')}
            </label>
            <select
              value={carbonForm.vehicle}
              onChange={(e) => setCarbonForm({...carbonForm, vehicle: e.target.value})}
              className="w-full px-3 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-forest text-sm"
            >
              <option value="car">{t('dashboard.vehicles.car', 'Car')}</option>
              <option value="bike">{t('dashboard.vehicles.bike', 'Bike')}</option>
              <option value="bus">{t('dashboard.vehicles.bus', 'Bus')}</option>
              <option value="ev">{t('dashboard.vehicles.ev', 'Electric Vehicle')}</option>
            </select>
          </div>

          <div className="flex items-end">
            <button type="submit" className="w-full btn-secondary flex items-center justify-center gap-2 text-sm">
              <Car size={16} />
              {t('dashboard.calculate', 'Calculate')}
            </button>
          </div>
        </form>

        {carbonResult && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-card bg-gradient-to-r from-green-100/80 to-blue-100/80 border-2 border-green-500/30 shadow-xl"
          >
            <h4 className="text-base font-bold text-gray-800 mb-2">{t('dashboard.carbonImpact', 'Your Carbon Impact')}</h4>
            <div className="grid md:grid-cols-2 gap-2">
              <div className="bg-white p-3 rounded-lg">
                <p className="text-xs text-gray-600 mb-1">{t('dashboard.emissions', 'CO₂ Emissions')}</p>
                <p className="text-2xl font-bold text-gray-800">{carbonResult.co2_kg.toFixed(2)} kg</p>
              </div>
              <div className="bg-white p-3 rounded-lg">
                <p className="text-xs text-gray-600 mb-1">{t('dashboard.vsSuv', 'vs. Standard SUV')}</p>
                <p className="text-2xl font-bold text-green-600">
                  {carbonResult.saved_vs_suv > 0 ? '-' : '+'}{Math.abs(carbonResult.saved_vs_suv).toFixed(2)} kg
                </p>
              </div>
            </div>
            <p className="mt-3 text-xs text-gray-700">
              <Lightbulb size={14} className="inline mr-1" /> {t('dashboard.tip', 'Tip: Consider carpooling or using public transport to reduce your carbon footprint!')}
            </p>
          </motion.div>
        )}
      </div>
    </div>
  )
}
