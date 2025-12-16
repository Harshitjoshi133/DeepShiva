import { useState, useEffect, useRef } from 'react'
import { MapPin, AlertCircle, Loader2, Navigation, Route, Search } from 'lucide-react'
import { motion } from 'framer-motion'
import mapplsService from '../services/mapplsService'
import { useLanguage } from '../contexts/LanguageContext'

// Char Dham coordinates
const CHAR_DHAM_LOCATIONS = [
  {
    name: 'Kedarnath',
    coordinates: [79.0669, 30.7352],
    status: 'Check Official Portal for Status',
    description: 'Sacred Shiva temple in the Himalayas'
  },
  {
    name: 'Badrinath', 
    coordinates: [79.4938, 30.7433],
    status: 'Check Official Portal for Status',
    description: 'Holy Vishnu temple in Chamoli district'
  },
  {
    name: 'Gangotri',
    coordinates: [78.9322, 30.9993],
    status: 'Check Official Portal for Status', 
    description: 'Source of the sacred Ganges river'
  },
  {
    name: 'Yamunotri',
    coordinates: [78.4270, 31.0118],
    status: 'Check Official Portal for Status',
    description: 'Source of the sacred Yamuna river'
  }
];

// Map center (Rudraprayag area)
const MAP_CENTER = [79.0669, 30.7352];
const MAP_ZOOM = 10;

export default function CharDhamMap() {
  const { t } = useLanguage()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [selectedLocation, setSelectedLocation] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [routeInfo, setRouteInfo] = useState(null)
  const [crowdData, setCrowdData] = useState([])
  const [crowdPredictions, setCrowdPredictions] = useState(null)
  const [realTimeAlerts, setRealTimeAlerts] = useState(null)

  useEffect(() => {
    initializeMapData()
  }, [])

  const initializeMapData = async () => {
    try {
      setIsLoading(true)
      setError(null)

      // Load crowd data instead of traffic data (more reliable)
      await loadCrowdData()
      
      setIsLoading(false)

    } catch (err) {
      console.error('Map initialization error:', err)
      setError(err.message)
      setIsLoading(false)
    }
  }

  const loadCrowdData = async () => {
    try {
      // Try enhanced crowd status first, fallback to basic
      let response = await fetch('/api/v1/tourism/enhanced-crowd-status')
      if (!response.ok) {
        console.warn('Enhanced crowd data failed, trying basic endpoint')
        response = await fetch('/api/v1/tourism/crowd-status')
      }
      
      if (!response.ok) {
        throw new Error(`Failed to load crowd data: ${response.status}`)
      }
      
      const data = await response.json()
      setCrowdData(data)
      console.log('Crowd data loaded successfully:', data)
    } catch (err) {
      console.warn('Could not load crowd data:', err)
      // Don't throw error, just log warning
    }
  }

  const loadCrowdPredictions = async (shrine) => {
    try {
      setIsLoading(true)
      const response = await fetch(`/api/v1/tourism/crowd-predictions/${shrine.toLowerCase()}?hours=12`)
      if (!response.ok) {
        throw new Error(`Failed to load predictions: ${response.status}`)
      }
      const data = await response.json()
      setCrowdPredictions(data)
      setIsLoading(false)
    } catch (err) {
      console.error('Could not load crowd predictions:', err)
      setIsLoading(false)
    }
  }

  const loadRealTimeAlerts = async (shrine) => {
    try {
      const response = await fetch(`/api/v1/tourism/real-time-alerts/${shrine.toLowerCase()}`)
      if (!response.ok) {
        throw new Error(`Failed to load alerts: ${response.status}`)
      }
      const data = await response.json()
      setRealTimeAlerts(data)
    } catch (err) {
      console.error('Could not load real-time alerts:', err)
    }
  }

  const handleSearch = async () => {
    if (!searchQuery.trim()) return

    try {
      setIsLoading(true)
      
      // Try Mappls API first, fallback to mock data
      try {
        const results = await mapplsService.autoSuggest(searchQuery, {
          region: 'IND',
          location: `${MAP_CENTER[1]},${MAP_CENTER[0]}` // lat,lng format for bias
        })
        setSearchResults(results.suggestedLocations || [])
      } catch (mapplsErr) {
        console.warn('Mappls search failed, using fallback:', mapplsErr)
        
        // Fallback mock search results
        const mockResults = [
          { placeName: `${searchQuery} Temple`, placeAddress: `Near ${searchQuery}, Uttarakhand` },
          { placeName: `${searchQuery} Market`, placeAddress: `${searchQuery} Bazaar, Uttarakhand` },
          { placeName: `${searchQuery} Guest House`, placeAddress: `${searchQuery} Accommodation, Uttarakhand` }
        ]
        setSearchResults(mockResults)
      }
      
      setIsLoading(false)
    } catch (err) {
      console.error('Search error:', err)
      setError(`Search failed: ${err.message}`)
      setIsLoading(false)
    }
  }

  const getRouteToLocation = async (location) => {
    try {
      setIsLoading(true)
      
      // Always use our internal route data for reliability
      try {
        const response = await fetch(`/api/v1/tourism/route-info/rishikesh/${location.name.toLowerCase()}`)
        if (response.ok) {
          const routeData = await response.json()
          setRouteInfo({
            destination: location.name,
            route: null,
            distance: `${routeData.distance_km} km`,
            duration: `${routeData.estimated_time_hours} hours`,
            fallbackData: routeData
          })
        } else {
          // If our API fails, try Mappls as backup
          const start = `${MAP_CENTER[1]},${MAP_CENTER[0]}` // lat,lng
          const end = `${location.coordinates[1]},${location.coordinates[0]}` // lat,lng
          
          const route = await mapplsService.getRoute(start, end, {
            profile: 'driving',
            steps: true,
            alternatives: false
          })
          
          setRouteInfo({
            destination: location.name,
            route: route,
            distance: route.routes?.[0]?.distance || 'Unknown',
            duration: route.routes?.[0]?.duration || 'Unknown'
          })
        }
      } catch (routeErr) {
        console.warn('Route calculation failed:', routeErr)
        // Provide basic fallback data
        setRouteInfo({
          destination: location.name,
          route: null,
          distance: 'Calculating...',
          duration: 'Calculating...',
          fallbackData: {
            difficulty: 'Moderate',
            estimated_fuel_cost: 1500,
            warnings: ['Check weather conditions before travel']
          }
        })
      }
      
      // Load crowd predictions and real-time alerts for the selected location
      await loadCrowdPredictions(location.name)
      await loadRealTimeAlerts(location.name)
      
      setIsLoading(false)
    } catch (err) {
      console.error('Route error:', err)
      setError(`Route calculation failed: ${err.message}`)
      setIsLoading(false)
    }
  }

  const handleRetry = () => {
    setError(null)
    setCrowdData([])
    setCrowdPredictions(null)
    setRouteInfo(null)
    setRealTimeAlerts(null)
    initializeMapData()
  }

  const getCrowdColor = (level) => {
    if (level < 25) return 'text-green-600 bg-green-100'
    if (level < 60) return 'text-yellow-600 bg-yellow-100'
    if (level < 85) return 'text-orange-600 bg-orange-100'
    return 'text-red-600 bg-red-100'
  }

  const getCrowdStatus = (locationName) => {
    const crowdInfo = crowdData.find(item => item.shrine === locationName)
    return crowdInfo || null
  }

  if (error) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card shadow-2xl"
      >
        <div className="flex items-center gap-2 mb-3">
          <Navigation size={20} className="text-saffron" />
          <h3 className="text-lg font-bold gradient-text">
            {t('dashboard.charDhamMap', 'Char Dham Route Map')}
          </h3>
        </div>
        
        <div className="flex flex-col items-center justify-center h-64 text-center">
          <AlertCircle size={48} className="text-red-500 mb-4" />
          <h4 className="text-lg font-semibold text-gray-800 mb-2">
            {t('dashboard.mapError', 'Map Loading Error')}
          </h4>
          <p className="text-sm text-gray-600 mb-4 max-w-md">
            {error}
          </p>
          <button
            onClick={handleRetry}
            className="btn-secondary flex items-center gap-2"
          >
            <Navigation size={16} />
            {t('dashboard.retryMap', 'Retry Loading Map')}
          </button>
        </div>
      </motion.div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card shadow-2xl"
    >
      <div className="flex items-center gap-2 mb-3">
        <Navigation size={20} className="text-saffron" />
        <h3 className="text-lg font-bold gradient-text">
          {t('dashboard.charDhamMap', 'Char Dham Route Planner')}
        </h3>
        {isLoading && (
          <Loader2 size={16} className="animate-spin text-saffron ml-auto" />
        )}
      </div>

      {/* Search Section */}
      <div className="mb-4">
        <div className="flex gap-2">
          <div className="flex-1">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              placeholder={t('dashboard.searchPlaces', 'Search places near Char Dham...')}
              className="w-full px-3 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-saffron text-sm"
            />
          </div>
          <button
            onClick={handleSearch}
            disabled={!searchQuery.trim() || isLoading}
            className="btn-secondary flex items-center gap-2"
          >
            <Search size={16} />
            {t('dashboard.search', 'Search')}
          </button>
        </div>

        {/* Search Results */}
        {searchResults.length > 0 && (
          <div className="mt-2 bg-white rounded-lg border border-gray-200 max-h-40 overflow-y-auto">
            {searchResults.slice(0, 5).map((result, index) => (
              <div
                key={index}
                className="p-2 hover:bg-gray-50 cursor-pointer border-b border-gray-100 last:border-b-0"
                onClick={() => {
                  setSelectedLocation(result)
                  setSearchResults([])
                  setSearchQuery(result.placeName || result.placeAddress)
                }}
              >
                <p className="text-sm font-semibold text-gray-800">{result.placeName}</p>
                <p className="text-xs text-gray-600">{result.placeAddress}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Char Dham Location Cards with Real Crowd Data */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mb-4">
        {CHAR_DHAM_LOCATIONS.map((location) => {
          const crowdInfo = getCrowdStatus(location.name)
          return (
            <div
              key={location.name}
              className={`bg-gradient-to-br from-saffron/10 to-forest/10 rounded-lg p-2 text-center cursor-pointer hover:shadow-md transition-all ${
                selectedLocation?.name === location.name ? 'ring-2 ring-saffron' : ''
              }`}
              onClick={() => {
                setSelectedLocation(location)
                getRouteToLocation(location)
              }}
            >
              <MapPin size={16} className="text-saffron mx-auto mb-1" />
              <p className="text-xs font-semibold text-gray-800">{location.name}</p>
              <p className="text-xs text-gray-600 truncate">{location.description}</p>
              
              {/* Real Crowd Status */}
              {crowdInfo && (
                <div className={`mt-1 px-2 py-1 rounded text-xs font-semibold ${getCrowdColor(crowdInfo.crowd_level)}`}>
                  {crowdInfo.status} ({crowdInfo.crowd_level}%)
                </div>
              )}
              
              {/* Weather Info */}
              {crowdInfo && (
                <div className="mt-1 text-xs text-gray-600">
                  {crowdInfo.weather} • {crowdInfo.temperature}°C
                </div>
              )}
              
              <div className="mt-1">
                <button className="text-xs bg-saffron/20 text-saffron px-2 py-1 rounded flex items-center gap-1 mx-auto">
                  <Route size={10} />
                  {t('dashboard.getRoute', 'Get Route')}
                </button>
              </div>
            </div>
          )
        })}
      </div>

      {/* Route Information */}
      {routeInfo && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-r from-blue-50 to-green-50 rounded-lg p-3 mb-4 border border-blue-200"
        >
          <h4 className="text-sm font-bold text-gray-800 mb-2 flex items-center gap-2">
            <Route size={16} className="text-blue-600" />
            {t('dashboard.routeTo', 'Route to')} {routeInfo.destination}
          </h4>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-gray-600">{t('dashboard.distance', 'Distance')}</p>
              <p className="text-sm font-semibold text-gray-800">
                {typeof routeInfo.distance === 'number' 
                  ? `${(routeInfo.distance / 1000).toFixed(1)} km`
                  : routeInfo.distance
                }
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-600">{t('dashboard.duration', 'Duration')}</p>
              <p className="text-sm font-semibold text-gray-800">
                {typeof routeInfo.duration === 'number'
                  ? `${Math.round(routeInfo.duration / 60)} min`
                  : routeInfo.duration
                }
              </p>
            </div>
          </div>
          
          {/* Fallback route data */}
          {routeInfo.fallbackData && (
            <div className="mt-2 grid grid-cols-2 gap-2 text-xs">
              <div>
                <span className="text-gray-600">Difficulty: </span>
                <span className="font-semibold">{routeInfo.fallbackData.difficulty}</span>
              </div>
              <div>
                <span className="text-gray-600">Fuel Cost: </span>
                <span className="font-semibold">₹{routeInfo.fallbackData.estimated_fuel_cost}</span>
              </div>
            </div>
          )}
          
          {routeInfo.route?.routes?.[0]?.legs?.[0]?.steps && (
            <div className="mt-2">
              <p className="text-xs text-gray-600 mb-1">{t('dashboard.directions', 'Key Directions')}:</p>
              <div className="text-xs text-gray-700 max-h-20 overflow-y-auto">
                {routeInfo.route.routes[0].legs[0].steps.slice(0, 3).map((step, index) => (
                  <p key={index} className="mb-1">• {step.maneuver?.instruction || step.name}</p>
                ))}
              </div>
            </div>
          )}
        </motion.div>
      )}

      {/* AI Crowd Predictions */}
      {crowdPredictions && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-3 mb-4 border border-purple-200"
        >
          <h4 className="text-sm font-bold text-gray-800 mb-2 flex items-center gap-2">
            <AlertCircle size={16} className="text-purple-600" />
            AI Crowd Predictions - {crowdPredictions.shrine}
          </h4>
          
          <div className="grid grid-cols-3 gap-2 mb-3 text-xs">
            <div className="text-center">
              <p className="text-gray-600">Avg Level</p>
              <p className="font-bold text-purple-800">{crowdPredictions.summary.avg_crowd_level}%</p>
            </div>
            <div className="text-center">
              <p className="text-gray-600">Peak Time</p>
              <p className="font-bold text-purple-800">
                {new Date(crowdPredictions.summary.peak_hour).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
              </p>
            </div>
            <div className="text-center">
              <p className="text-gray-600">Best Visit</p>
              <p className="font-bold text-green-800">
                {crowdPredictions.summary.best_visit_hours.length > 0 
                  ? new Date(crowdPredictions.summary.best_visit_hours[0]).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
                  : 'Early AM'
                }
              </p>
            </div>
          </div>
          
          {/* Next 6 hours prediction */}
          <div className="space-y-1">
            <p className="text-xs font-semibold text-gray-700 mb-1">Next 6 Hours:</p>
            <div className="grid grid-cols-6 gap-1">
              {crowdPredictions.predictions.slice(0, 6).map((pred, index) => (
                <div key={index} className="text-center">
                  <p className="text-xs text-gray-600">{new Date(pred.time).getHours()}:00</p>
                  <div className={`text-xs font-bold px-1 py-1 rounded ${getCrowdColor(pred.crowd_level)}`}>
                    {pred.crowd_level}%
                  </div>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      )}

      {/* Real-Time Alerts */}
      {realTimeAlerts && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-r from-red-50 to-orange-50 rounded-lg p-3 mb-4 border border-red-200"
        >
          <h4 className="text-sm font-bold text-gray-800 mb-2 flex items-center gap-2">
            <AlertCircle size={16} className="text-red-600" />
            Live Alerts - {realTimeAlerts.shrine}
          </h4>
          
          {/* Current Conditions */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mb-3 text-xs">
            <div className="text-center bg-white/50 rounded p-2">
              <p className="text-gray-600">Crowd</p>
              <p className={`font-bold ${getCrowdColor(realTimeAlerts.current_conditions.crowd_level).split(' ')[0]}`}>
                {realTimeAlerts.current_conditions.crowd_level}%
              </p>
            </div>
            <div className="text-center bg-white/50 rounded p-2">
              <p className="text-gray-600">Weather</p>
              <p className="font-bold text-blue-800">{realTimeAlerts.current_conditions.weather}</p>
            </div>
            <div className="text-center bg-white/50 rounded p-2">
              <p className="text-gray-600">Temp</p>
              <p className="font-bold text-purple-800">{realTimeAlerts.current_conditions.temperature}°C</p>
            </div>
            <div className="text-center bg-white/50 rounded p-2">
              <p className="text-gray-600">Access</p>
              <p className="font-bold text-green-800 text-xs">{realTimeAlerts.current_conditions.accessibility}</p>
            </div>
          </div>
          
          {/* Alerts */}
          {realTimeAlerts.alerts.length > 0 && (
            <div className="mb-3">
              <p className="text-xs font-semibold text-gray-700 mb-1">Active Alerts:</p>
              <div className="space-y-1">
                {realTimeAlerts.alerts.map((alert, index) => (
                  <div key={index} className={`text-xs p-2 rounded flex items-start gap-2 ${
                    alert.severity === 'high' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    <span>{alert.icon}</span>
                    <span>{alert.message}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Recommendations */}
          {realTimeAlerts.recommendations.length > 0 && (
            <div className="mb-2">
              <p className="text-xs font-semibold text-gray-700 mb-1">Recommendations:</p>
              <div className="text-xs text-gray-700 space-y-1">
                {realTimeAlerts.recommendations.slice(0, 3).map((rec, index) => (
                  <p key={index} className="flex items-start gap-1">
                    <span className="text-green-600">•</span>
                    <span>{rec}</span>
                  </p>
                ))}
              </div>
            </div>
          )}
          
          <div className="flex justify-between items-center text-xs text-gray-600 mt-2 pt-2 border-t border-gray-200">
            <span>Next update: {realTimeAlerts.next_update}</span>
            <span>Emergency: {realTimeAlerts.emergency_contacts.police}</span>
          </div>
        </motion.div>
      )}

      {/* Overall Crowd Status Summary */}
      {crowdData.length > 0 && (
        <div className="bg-gradient-to-r from-yellow-50 to-red-50 rounded-lg p-3 border border-yellow-200">
          <h4 className="text-sm font-bold text-gray-800 mb-2 flex items-center gap-2">
            <AlertCircle size={16} className="text-yellow-600" />
            {t('dashboard.crowdStatus', 'Live Crowd Status')}
          </h4>
          <div className="grid grid-cols-4 gap-2 text-center">
            {crowdData.map((shrine) => (
              <div key={shrine.shrine} className={`rounded p-2 ${getCrowdColor(shrine.crowd_level)}`}>
                <p className="text-xs font-bold">{shrine.shrine}</p>
                <p className="text-xs">{shrine.crowd_level}%</p>
                <p className="text-xs">{shrine.accessibility}</p>
              </div>
            ))}
          </div>
          <div className="mt-2 flex justify-between items-center text-xs text-gray-600">
            <span>Last updated: {crowdData[0]?.last_updated}</span>
            <span>AI-powered predictions</span>
          </div>
        </div>
      )}
    </motion.div>
  )
}