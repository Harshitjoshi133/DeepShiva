import { createContext, useContext, useState, useEffect } from 'react'

const LanguageContext = createContext()

export const useLanguage = () => {
  const context = useContext(LanguageContext)
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider')
  }
  return context
}

export const LanguageProvider = ({ children }) => {
  const [language, setLanguage] = useState(() => {
    // Get saved language from localStorage or default to English
    return localStorage.getItem('deep-shiva-language') || 'en'
  })

  const changeLanguage = (newLanguage) => {
    setLanguage(newLanguage)
    localStorage.setItem('deep-shiva-language', newLanguage)
  }

  useEffect(() => {
    // Update document language attribute
    document.documentElement.lang = language
  }, [language])

  const value = {
    language,
    changeLanguage,
    t: (key, fallback) => translate(key, language, fallback)
  }

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  )
}

// Translation function
const translate = (key, language, fallback) => {
  const translations = getTranslations()
  
  // Navigate through nested keys (e.g., "home.title")
  const keys = key.split('.')
  let value = translations[language]
  
  for (const k of keys) {
    value = value?.[k]
  }
  
  return value || fallback || key
}

// Translation data
const getTranslations = () => ({
  en: {
    // Navigation
    nav: {
      home: 'Home',
      chat: 'Chat',
      yoga: 'Yoga',
      dashboard: 'Dashboard',
      culture: 'Culture',
      emergency: 'SOS'
    },
    
    // Common
    common: {
      loading: 'Loading...',
      error: 'Error',
      success: 'Success',
      cancel: 'Cancel',
      save: 'Save',
      delete: 'Delete',
      edit: 'Edit',
      view: 'View',
      search: 'Search',
      filter: 'Filter',
      sort: 'Sort',
      back: 'Back',
      next: 'Next',
      previous: 'Previous',
      close: 'Close'
    },
    
    // Home Page
    home: {
      title: 'Plan Your Yatra to Uttarakhand',
      subtitle: 'Your AI-powered spiritual guide for eco-tourism, yoga, and sacred journeys',
      startJourney: 'Start Your Journey',
      quickActions: 'Quick Actions',
      checkCrowd: 'Check Crowd Status',
      yogaMode: 'Yoga Mode',
      emergencyHelp: 'Emergency Help',
      whyDeepShiva: 'Why Deep-Shiva?',
      spiritualGuidance: 'Spiritual Guidance',
      spiritualDesc: 'Get personalized yatra recommendations and spiritual insights',
      yogaCorrection: 'Yoga Correction',
      yogaDesc: 'Real-time posture analysis using AI vision technology',
      ecoTourism: 'Eco-Tourism',
      ecoDesc: 'Calculate your carbon footprint and travel sustainably',
      localCulture: 'Local Culture',
      cultureDesc: 'Discover and support local artisans and traditions'
    },
    
    // Chat Page
    chat: {
      title: 'Chat with Deep-Shiva',
      placeholder: 'Ask about temples, routes, weather...',
      thinking: 'Deep-Shiva is thinking...',
      voiceInput: 'Voice input (coming soon)'
    },
    
    // Yoga Page
    yoga: {
      title: 'Yoga Sentinel',
      description: 'Position yourself in front of the camera and click "Analyze Pose" for real-time feedback on your yoga posture.',
      analyzePose: 'Analyze Pose',
      analyzing: 'Analyzing...',
      cameraRequired: 'Camera Access Required',
      cameraMessage: 'Please allow camera access in your browser settings to use Yoga Sentinel.',
      confidence: 'Confidence',
      tipsTitle: 'Tips for Best Results:',
      tips: {
        lighting: 'Ensure good lighting',
        distance: 'Stand 6-8 feet from camera',
        clothing: 'Wear contrasting clothing',
        frame: 'Keep full body in frame'
      }
    },
    
    // Dashboard Page
    dashboard: {
      title: 'Yatra Dashboard',
      crowdStatus: 'Live Crowd Status',
      carbonCalculator: 'Carbon Footprint Calculator',
      distance: 'Distance (km)',
      vehicleType: 'Vehicle Type',
      calculate: 'Calculate',
      carbonImpact: 'Your Carbon Impact',
      emissions: 'CO₂ Emissions',
      vsSuv: 'vs. Standard SUV',
      tip: 'Tip: Consider carpooling or using public transport to reduce your carbon footprint!',
      vehicles: {
        car: 'Car',
        bike: 'Bike',
        bus: 'Bus',
        ev: 'Electric Vehicle'
      }
    },
    
    // Culture Page
    culture: {
      title: 'Culture & Artisan Hub',
      description: 'Support local artisans and discover authentic Uttarakhand crafts'
    },
    
    // Emergency Page
    emergency: {
      title: 'Emergency SOS',
      description: 'In case of emergency, contact these services immediately. Your location will be shared automatically.',
      police: 'Police',
      ambulance: 'Ambulance',
      disaster: 'Disaster Management',
      firstAidTitle: 'Offline First Aid Guide',
      firstAidDesc: 'Essential first aid information for common mountain emergencies',
      important: 'Important',
      importantNote: 'This guide is for informational purposes only. Always seek professional medical help in emergencies. Keep emergency numbers saved offline in your phone.'
    }
  },
  
  hi: {
    // Navigation
    nav: {
      home: 'होम',
      chat: 'चैट',
      yoga: 'योग',
      dashboard: 'डैशबोर्ड',
      culture: 'संस्कृति',
      emergency: 'आपातकाल'
    },
    
    // Common
    common: {
      loading: 'लोड हो रहा है...',
      error: 'त्रुटि',
      success: 'सफलता',
      cancel: 'रद्द करें',
      save: 'सेव करें',
      delete: 'हटाएं',
      edit: 'संपादित करें',
      view: 'देखें',
      search: 'खोजें',
      filter: 'फिल्टर',
      sort: 'क्रमबद्ध करें',
      back: 'वापस',
      next: 'अगला',
      previous: 'पिछला',
      close: 'बंद करें'
    },
    
    // Home Page
    home: {
      title: 'उत्तराखंड की अपनी यात्रा की योजना बनाएं',
      subtitle: 'पर्यावरण-पर्यटन, योग और पवित्र यात्राओं के लिए आपका AI-संचालित आध्यात्मिक गाइड',
      startJourney: 'अपनी यात्रा शुरू करें',
      quickActions: 'त्वरित कार्य',
      checkCrowd: 'भीड़ की स्थिति देखें',
      yogaMode: 'योग मोड',
      emergencyHelp: 'आपातकालीन सहायता',
      whyDeepShiva: 'दीप-शिव क्यों?',
      spiritualGuidance: 'आध्यात्मिक मार्गदर्शन',
      spiritualDesc: 'व्यक्तिगत यात्रा सिफारिशें और आध्यात्मिक अंतर्दृष्टि प्राप्त करें',
      yogaCorrection: 'योग सुधार',
      yogaDesc: 'AI विज़न तकनीक का उपयोग करके वास्तविक समय मुद्रा विश्लेषण',
      ecoTourism: 'पर्यावरण-पर्यटन',
      ecoDesc: 'अपने कार्बन फुटप्रिंट की गणना करें और टिकाऊ यात्रा करें',
      localCulture: 'स्थानीय संस्कृति',
      cultureDesc: 'स्थानीय कारीगरों और परंपराओं की खोज और समर्थन करें'
    },
    
    // Chat Page
    chat: {
      title: 'दीप-शिव के साथ चैट करें',
      placeholder: 'मंदिरों, मार्गों, मौसम के बारे में पूछें...',
      thinking: 'दीप-शिव सोच रहा है...',
      voiceInput: 'वॉयस इनपुट (जल्द आ रहा है)'
    },
    
    // Yoga Page
    yoga: {
      title: 'योग सेंटिनल',
      description: 'कैमरे के सामने खुद को स्थिति में रखें और अपनी योग मुद्रा पर वास्तविक समय प्रतिक्रिया के लिए "मुद्रा का विश्लेषण करें" पर क्लिक करें।',
      analyzePose: 'मुद्रा का विश्लेषण करें',
      analyzing: 'विश्लेषण कर रहे हैं...',
      cameraRequired: 'कैमरा एक्सेस आवश्यक',
      cameraMessage: 'योग सेंटिनल का उपयोग करने के लिए कृपया अपनी ब्राउज़र सेटिंग्स में कैमरा एक्सेस की अनुमति दें।',
      confidence: 'विश्वास',
      tipsTitle: 'सर्वोत्तम परिणामों के लिए सुझाव:',
      tips: {
        lighting: 'अच्छी रोशनी सुनिश्चित करें',
        distance: 'कैमरे से 6-8 फीट दूर खड़े हों',
        clothing: 'विपरीत रंग के कपड़े पहनें',
        frame: 'पूरे शरीर को फ्रेम में रखें'
      }
    },
    
    // Dashboard Page
    dashboard: {
      title: 'यात्रा डैशबोर्ड',
      crowdStatus: 'लाइव भीड़ स्थिति',
      carbonCalculator: 'कार्बन फुटप्रिंट कैलकुलेटर',
      distance: 'दूरी (किमी)',
      vehicleType: 'वाहन प्रकार',
      calculate: 'गणना करें',
      carbonImpact: 'आपका कार्बन प्रभाव',
      emissions: 'CO₂ उत्सर्जन',
      vsSuv: 'बनाम मानक SUV',
      tip: 'सुझाव: अपने कार्बन फुटप्रिंट को कम करने के लिए कारपूलिंग या सार्वजनिक परिवहन का उपयोग करने पर विचार करें!',
      vehicles: {
        car: 'कार',
        bike: 'बाइक',
        bus: 'बस',
        ev: 'इलेक्ट्रिक वाहन'
      }
    },
    
    // Culture Page
    culture: {
      title: 'संस्कृति और कारीगर हब',
      description: 'स्थानीय कारीगरों का समर्थन करें और प्रामाणिक उत्तराखंड शिल्प की खोज करें'
    },
    
    // Emergency Page
    emergency: {
      title: 'आपातकालीन SOS',
      description: 'आपातकाल की स्थिति में, तुरंत इन सेवाओं से संपर्क करें। आपका स्थान स्वचालित रूप से साझा किया जाएगा।',
      police: 'पुलिस',
      ambulance: 'एम्बुलेंस',
      disaster: 'आपदा प्रबंधन',
      firstAidTitle: 'ऑफलाइन प्राथमिक चिकित्सा गाइड',
      firstAidDesc: 'सामान्य पर्वतीय आपातकाल के लिए आवश्यक प्राथमिक चिकित्सा जानकारी',
      important: 'महत्वपूर्ण',
      importantNote: 'यह गाइड केवल सूचनात्मक उद्देश्यों के लिए है। आपातकाल में हमेशा पेशेवर चिकित्सा सहायता लें। आपातकालीन नंबरों को अपने फोन में ऑफलाइन सेव करके रखें।'
    }
  },
  
  ga: {
    // Navigation (Garhwali)
    nav: {
      home: 'घर',
      chat: 'गल्लबात',
      yoga: 'योग',
      dashboard: 'डैशबोर्ड',
      culture: 'संस्कार',
      emergency: 'मुसीबत'
    },
    
    // Common
    common: {
      loading: 'लोड हुंदा...',
      error: 'गलती',
      success: 'सफलता',
      cancel: 'रद्द करो',
      save: 'बचाओ',
      delete: 'मिटाओ',
      edit: 'सुधारो',
      view: 'देखो',
      search: 'खोजो',
      filter: 'छानो',
      sort: 'क्रम लगाओ',
      back: 'वापस',
      next: 'अगला',
      previous: 'पिछला',
      close: 'बंद करो'
    },
    
    // Home Page
    home: {
      title: 'उत्तराखंड की यात्रा की योजना बनाओ',
      subtitle: 'पर्यावरण-पर्यटन, योग और पवित्र यात्राओं के लिए तुम्हारा AI गाइड',
      startJourney: 'यात्रा शुरू करो',
      quickActions: 'जल्दी काम',
      checkCrowd: 'भीड़ देखो',
      yogaMode: 'योग मोड',
      emergencyHelp: 'मुसीबत में मदद',
      whyDeepShiva: 'दीप-शिव क्यों?',
      spiritualGuidance: 'आध्यात्मिक मार्गदर्शन',
      spiritualDesc: 'व्यक्तिगत यात्रा सलाह और आध्यात्मिक ज्ञान पाओ',
      yogaCorrection: 'योग सुधार',
      yogaDesc: 'AI तकनीक से वास्तविक समय मुद्रा जांच',
      ecoTourism: 'पर्यावरण-पर्यटन',
      ecoDesc: 'अपना कार्बन फुटप्रिंट गिनो और टिकाऊ यात्रा करो',
      localCulture: 'स्थानीय संस्कार',
      cultureDesc: 'स्थानीय कारीगरों और परंपराओं की खोज और समर्थन करो'
    },
    
    // Chat Page
    chat: {
      title: 'दीप-शिव से गल्लबात करो',
      placeholder: 'मंदिर, रास्ता, मौसम के बारे में पूछो...',
      thinking: 'दीप-शिव सोच रहा है...',
      voiceInput: 'आवाज इनपुट (जल्द आएगा)'
    },
    
    // Yoga Page
    yoga: {
      title: 'योग सेंटिनल',
      description: 'कैमरे के सामने खड़े हो जाओ और अपनी योग मुद्रा की जांच के लिए "मुद्रा देखो" पर दबाओ।',
      analyzePose: 'मुद्रा देखो',
      analyzing: 'देख रहे हैं...',
      cameraRequired: 'कैमरा चाहिए',
      cameraMessage: 'योग सेंटिनल इस्तेमाल करने के लिए ब्राउज़र में कैमरा की इजाजत दो।',
      confidence: 'भरोसा',
      tipsTitle: 'अच्छे नतीजे के लिए सुझाव:',
      tips: {
        lighting: 'अच्छी रोशनी रखो',
        distance: 'कैमरे से 6-8 फुट दूर खड़े हो',
        clothing: 'अलग रंग के कपड़े पहनो',
        frame: 'पूरा शरीर फ्रेम में रखो'
      }
    },
    
    // Dashboard Page
    dashboard: {
      title: 'यात्रा डैशबोर्ड',
      crowdStatus: 'लाइव भीड़ स्थिति',
      carbonCalculator: 'कार्बन फुटप्रिंट गिनती',
      distance: 'दूरी (किमी)',
      vehicleType: 'गाड़ी का प्रकार',
      calculate: 'गिनती करो',
      carbonImpact: 'तुम्हारा कार्बन प्रभाव',
      emissions: 'CO₂ निकास',
      vsSuv: 'SUV के मुकाबले',
      tip: 'सुझाव: कार्बन फुटप्रिंट कम करने के लिए साझा गाड़ी या सार्वजनिक परिवहन का इस्तेमाल करो!',
      vehicles: {
        car: 'कार',
        bike: 'बाइक',
        bus: 'बस',
        ev: 'बिजली गाड़ी'
      }
    },
    
    // Culture Page
    culture: {
      title: 'संस्कार और कारीगर केंद्र',
      description: 'स्थानीय कारीगरों का समर्थन करो और असली उत्तराखंड शिल्प की खोज करो'
    },
    
    // Emergency Page
    emergency: {
      title: 'मुसीबत SOS',
      description: 'मुसीबत में तुरंत इन सेवाओं से संपर्क करो। तुम्हारी जगह अपने आप साझा हो जाएगी।',
      police: 'पुलिस',
      ambulance: 'एम्बुलेंस',
      disaster: 'आपदा प्रबंधन',
      firstAidTitle: 'ऑफलाइन प्राथमिक चिकित्सा गाइड',
      firstAidDesc: 'पहाड़ी मुसीबतों के लिए जरूरी प्राथमिक चिकित्सा जानकारी',
      important: 'जरूरी',
      importantNote: 'यह गाइड सिर्फ जानकारी के लिए है। मुसीबत में हमेशा डॉक्टर की मदद लो। मुसीबत के नंबर अपने फोन में ऑफलाइन सेव करके रखो।'
    }
  }
})