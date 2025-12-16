import { useState, useEffect } from 'react'
import { Leaf, Car, Lightbulb } from 'lucide-react'
import { motion } from 'framer-motion'
import { useLanguage } from '../contexts/LanguageContext'
import CharDhamMap from '../components/CharDhamMap'

export default function Dashboard() {
  const { t } = useLanguage()
  const [carbonForm, setCarbonForm] = useState({ distance: '', vehicle: 'car' })
  const [carbonResult, setCarbonResult] = useState(null)

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

  return (
    <div className="max-w-5xl mx-auto space-y-3">
      <h2 className="text-xl font-bold text-gray-800">{t('dashboard.title', 'Yatra Dashboard')}</h2>

      {/* Char Dham Route Map */}
      <CharDhamMap />

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
