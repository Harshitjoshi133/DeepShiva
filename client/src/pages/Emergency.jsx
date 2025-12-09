import { Phone, Ambulance, Shield, ChevronDown, ChevronUp } from 'lucide-react'
import { useState } from 'react'
import { motion } from 'framer-motion'

const emergencyContacts = [
  { name: 'Police', number: '100', icon: Shield, color: 'bg-blue-600' },
  { name: 'Ambulance', number: '108', icon: Ambulance, color: 'bg-red-600' },
  { name: 'Disaster Management', number: '1070', icon: Phone, color: 'bg-orange-600' },
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
  const [expandedTip, setExpandedTip] = useState(null)

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="card bg-red-50 border-2 border-red-500">
        <h2 className="text-3xl font-bold text-red-700 mb-4">Emergency SOS</h2>
        <p className="text-gray-700 mb-6">
          In case of emergency, contact these services immediately. Your location will be shared automatically.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {emergencyContacts.map((contact) => {
            const Icon = contact.icon
            return (
              <motion.button
                key={contact.name}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className={`${contact.color} text-white p-6 rounded-xl shadow-lg hover:shadow-2xl transition-all`}
              >
                <Icon size={48} className="mx-auto mb-3" />
                <h3 className="text-xl font-bold mb-2">{contact.name}</h3>
                <p className="text-3xl font-bold">{contact.number}</p>
              </motion.button>
            )
          })}
        </div>
      </div>

      {/* First Aid Tips */}
      <div className="card">
        <h3 className="text-2xl font-bold text-gray-800 mb-4">Offline First Aid Guide</h3>
        <p className="text-gray-600 mb-6">
          Essential first aid information for common mountain emergencies
        </p>

        <div className="space-y-3">
          {firstAidTips.map((tip, index) => (
            <div key={index} className="border-2 border-gray-200 rounded-lg overflow-hidden">
              <button
                onClick={() => setExpandedTip(expandedTip === index ? null : index)}
                className="w-full px-6 py-4 flex items-center justify-between bg-gray-50 hover:bg-gray-100 transition-colors"
              >
                <div className="text-left">
                  <h4 className="text-lg font-bold text-gray-800">{tip.title}</h4>
                  <p className="text-sm text-gray-600">{tip.symptoms}</p>
                </div>
                {expandedTip === index ? (
                  <ChevronUp size={24} className="text-gray-600" />
                ) : (
                  <ChevronDown size={24} className="text-gray-600" />
                )}
              </button>

              {expandedTip === index && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  className="px-6 py-4 bg-white"
                >
                  <h5 className="font-semibold text-gray-800 mb-3">Treatment Steps:</h5>
                  <ol className="list-decimal list-inside space-y-2">
                    {tip.treatment.map((step, stepIndex) => (
                      <li key={stepIndex} className="text-gray-700">{step}</li>
                    ))}
                  </ol>
                </motion.div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Important Note */}
      <div className="card bg-yellow-50 border-2 border-yellow-500">
        <h4 className="font-bold text-gray-800 mb-2">⚠️ Important</h4>
        <p className="text-gray-700">
          This guide is for informational purposes only. Always seek professional medical help in emergencies. 
          Keep emergency numbers saved offline in your phone.
        </p>
      </div>
    </div>
  )
}
