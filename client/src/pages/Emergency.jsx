import { Phone, Ambulance, Shield, ChevronDown, ChevronUp, AlertTriangle, Lightbulb } from 'lucide-react'
import { useState } from 'react'
import { motion } from 'framer-motion'
import { useLanguage } from '../contexts/LanguageContext'

const getEmergencyContacts = (t) => [
  { name: t('emergency.police', 'Police'), number: '100', icon: Shield, color: 'bg-blue-600' },
  { name: t('emergency.ambulance', 'Ambulance'), number: '108', icon: Ambulance, color: 'bg-red-600' },
  { name: t('emergency.disaster', 'Disaster Management'), number: '1070', icon: Phone, color: 'bg-orange-600' },
]

const firstAidTips = [
  {
    title: 'Altitude Sickness',
    symptoms: 'Headache, nausea, dizziness, fatigue',
    treatment: [
      'Descend to lower altitude immediately',
      'Rest and avoid physical exertion',
      'Drink plenty of water',
      'Take pain relievers for headache',
      'Seek medical help if symptoms worsen'
    ]
  },
  {
    title: 'Hypothermia',
    symptoms: 'Shivering, confusion, slurred speech, drowsiness',
    treatment: [
      'Move to warm shelter immediately',
      'Remove wet clothing',
      'Wrap in warm blankets',
      'Give warm (not hot) beverages',
      'Call emergency services'
    ]
  },
  {
    title: 'Dehydration',
    symptoms: 'Extreme thirst, dark urine, dizziness, fatigue',
    treatment: [
      'Drink water slowly and steadily',
      'Rest in shade',
      'Use oral rehydration solution if available',
      'Avoid caffeine and alcohol',
      'Seek medical help if severe'
    ]
  },
  {
    title: 'Snake Bite',
    symptoms: 'Puncture marks, pain, swelling, nausea',
    treatment: [
      'Keep calm and still',
      'Remove jewelry and tight clothing',
      'Keep bitten area below heart level',
      'DO NOT apply tourniquet or ice',
      'Get to hospital immediately'
    ]
  }
]

export default function Emergency() {
  const { t } = useLanguage()
  const [expandedTip, setExpandedTip] = useState(null)
  
  const emergencyContacts = getEmergencyContacts(t)

  return (
    <div className="max-w-4xl mx-auto space-y-4">
      <div className="glass-card bg-red-50/80 border-2 border-red-500/30 shadow-2xl">
        <div className="flex items-center gap-2 mb-2">
          <AlertTriangle size={20} className="text-red-600" />
          <h2 className="text-xl font-bold text-red-700">{t('emergency.title', 'Emergency SOS')}</h2>
        </div>
        <p className="text-gray-700 mb-3 text-sm">
          {t('emergency.description', 'In case of emergency, contact these services immediately. Your location will be shared automatically.')}
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
          {emergencyContacts.map((contact) => {
            const Icon = contact.icon
            return (
              <motion.button
                key={contact.name}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className={`${contact.color} text-white p-3 rounded-xl shadow-lg hover:shadow-2xl transition-all`}
              >
                <Icon size={28} className="mx-auto mb-2" />
                <h3 className="text-base font-bold mb-1">{contact.name}</h3>
                <p className="text-xl font-bold">{contact.number}</p>
              </motion.button>
            )
          })}
        </div>
      </div>

      {/* First Aid Tips */}
      <div className="glass-card shadow-2xl">
        <div className="flex items-center gap-2 mb-2">
          <Lightbulb size={20} className="text-saffron" />
          <h3 className="text-lg font-bold gradient-text">{t('emergency.firstAidTitle', 'Offline First Aid Guide')}</h3>
        </div>
        <p className="text-gray-600 mb-3 text-sm">
          {t('emergency.firstAidDesc', 'Essential first aid information for common mountain emergencies')}
        </p>

        <div className="space-y-2">
          {firstAidTips.map((tip, index) => (
            <div key={index} className="border-2 border-gray-200 rounded-lg overflow-hidden">
              <button
                onClick={() => setExpandedTip(expandedTip === index ? null : index)}
                className="w-full px-4 py-3 flex items-center justify-between bg-gray-50 hover:bg-gray-100 transition-colors"
              >
                <div className="text-left">
                  <h4 className="text-base font-bold text-gray-800">{tip.title}</h4>
                  <p className="text-xs text-gray-600">{tip.symptoms}</p>
                </div>
                {expandedTip === index ? (
                  <ChevronUp size={20} className="text-gray-600" />
                ) : (
                  <ChevronDown size={20} className="text-gray-600" />
                )}
              </button>

              {expandedTip === index && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  className="px-4 py-3 bg-white"
                >
                  <h5 className="font-semibold text-gray-800 mb-2 text-sm">Treatment Steps:</h5>
                  <ol className="list-decimal list-inside space-y-1">
                    {tip.treatment.map((step, stepIndex) => (
                      <li key={stepIndex} className="text-gray-700 text-xs">{step}</li>
                    ))}
                  </ol>
                </motion.div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Important Note */}
      <div className="glass-card bg-yellow-50/80 border-2 border-yellow-500/30">
        <div className="flex items-center gap-2 mb-1">
          <AlertTriangle size={16} className="text-yellow-600" />
          <h4 className="font-bold text-gray-800 text-sm">{t('emergency.important', 'Important')}</h4>
        </div>
        <p className="text-gray-700 text-xs">
          {t('emergency.importantNote', 'This guide is for informational purposes only. Always seek professional medical help in emergencies. Keep emergency numbers saved offline in your phone.')}
        </p>
      </div>
    </div>
  )
}
