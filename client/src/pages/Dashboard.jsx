import { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { TrendingUp, Leaf, Car } from 'lucide-react'
import { motion } from 'framer-motion'

export default function Dashboard() {
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
    <div className="max-w-6xl mx-auto space-y-6">
      <h2 className="text-3xl font-bold text-gray-800">Yatra Dashboard</h2>

      {/* Crowd Meter */}
      <div className="card">
        <div className="flex items-center gap-3 mb-6">
          <TrendingUp size={32} className="text-saffron" />
          <h3 className="text-2xl font-bold text-gray-800">Live Crowd Status</h3>
        </div>
        
        <ResponsiveContainer width="100%" height={300}>
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

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          {crowdData.map((shrine) => (
            <div key={shrine.shrine} className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="font-semibold text-gray-800">{shrine.shrine}</p>
              <p className={`text-sm font-bold ${
                shrine.status === 'Light' ? 'text-green-600' :
                shrine.status === 'Moderate' ? 'text-orange-600' :
                'text-red-600'
              }`}>
                {shrine.status}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Carbon Calculator */}
      <div className="card">
        <div className="flex items-center gap-3 mb-6">
          <Leaf size={32} className="text-forest" />
          <h3 className="text-2xl font-bold text-gray-800">Carbon Footprint Calculator</h3>
        </div>

        <form onSubmit={handleCarbonSubmit} className="grid md:grid-cols-3 gap-4 mb-6">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Distance (km)
            </label>
            <input
              type="number"
              value={carbonForm.distance}
              onChange={(e) => setCarbonForm({...carbonForm, distance: e.target.value})}
              className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-forest"
              placeholder="Enter distance"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Vehicle Type
            </label>
            <select
              value={carbonForm.vehicle}
              onChange={(e) => setCarbonForm({...carbonForm, vehicle: e.target.value})}
              className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-forest"
            >
              <option value="car">Car</option>
              <option value="bike">Bike</option>
              <option value="bus">Bus</option>
              <option value="ev">Electric Vehicle</option>
            </select>
          </div>

          <div className="flex items-end">
            <button type="submit" className="w-full btn-secondary flex items-center justify-center gap-2">
              <Car size={20} />
              Calculate
            </button>
          </div>
        </form>

        {carbonResult && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-gradient-to-r from-green-100 to-blue-100 p-6 rounded-lg border-2 border-green-500"
          >
            <h4 className="text-xl font-bold text-gray-800 mb-4">Your Carbon Impact</h4>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="bg-white p-4 rounded-lg">
                <p className="text-sm text-gray-600 mb-1">CO₂ Emissions</p>
                <p className="text-3xl font-bold text-gray-800">{carbonResult.co2_kg.toFixed(2)} kg</p>
              </div>
              <div className="bg-white p-4 rounded-lg">
                <p className="text-sm text-gray-600 mb-1">vs. Standard SUV</p>
                <p className="text-3xl font-bold text-green-600">
                  {carbonResult.saved_vs_suv > 0 ? '-' : '+'}{Math.abs(carbonResult.saved_vs_suv).toFixed(2)} kg
                </p>
              </div>
            </div>
            <p className="mt-4 text-sm text-gray-700">
              💡 Tip: Consider carpooling or using public transport to reduce your carbon footprint!
            </p>
          </motion.div>
        )}
      </div>
    </div>
  )
}
