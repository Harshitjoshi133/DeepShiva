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
      emergency: 'SOS',
      meditation: 'Meditation'
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
      meditationMode: 'Meditation',
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
      voiceInput: 'Voice input (coming soon)',
      startVoice: 'Start voice input',
      stopVoice: 'Stop voice input',
      send: 'Send message',
      listening: 'Listening...',
      listeningPlaceholder: 'Speak now...',
      hideSidebar: 'Hide Sidebar',
      showSidebar: 'Show Sidebar',
      backToMenu: 'Back to Menu',
      activeChat: 'Active Chat',
      closeSidebar: 'Close Sidebar',
      initializing: 'Initializing your spiritual guide...',
      creating: 'Creating...',
      history: 'Chat History',
      newChat: 'New Chat',
      delete: 'Delete chat',
      chats: 'Chats',
      about: 'About',
      recentChats: 'Recent Chats',
      noHistory: 'No chat history yet',
      startChatting: 'Start a conversation to see your chats here',
      aboutDescription: 'Your AI-powered spiritual guide to Uttarakhand. I can help you plan pilgrimages, find temples, check weather, and discover the rich culture of the Himalayas.',
      features: 'Features',
      feature1: 'Temple & Pilgrimage Information',
      feature2: 'Real-time Weather Updates',
      feature3: 'Route Planning & Navigation',
      feature4: 'Cultural Insights & Traditions',
      feature5: 'Voice Input Support',
      feature6: 'Multi-language Support',
      stats: 'Statistics',
      totalChats: 'Total Chats',
      currentMessages: 'Current Messages',
      lastResponseTime: 'Last Response Time',
      you: 'You',
      responseTime: 'Response time',
      error: 'Error',
      suggestion1: 'Tell me about Kedarnath temple',
      suggestion2: 'Best time to visit Char Dham',
      suggestion3: 'Weather in Rishikesh today',
      suggestion4: 'Plan a 7-day spiritual journey'
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
    },

    // Meditation Page
    meditation: {
      title: 'AI-Guided Meditation',
      subtitle: 'Find inner peace with personalized meditation guidance',
      selectType: 'Choose Your Meditation Type',
      selectDuration: 'Choose Duration',
      settings: 'Settings',
      breathingPattern: 'Breathing Pattern',
      voiceGuidance: 'Voice Guidance',
      voiceSpeed: 'Voice Speed',
      voiceSelection: 'Voice Selection',
      voiceServiceError: 'Voice Service Unavailable',
      voiceErrorHelp: 'To use voice-guided meditation:',
      retryVoice: 'Retry Voice Service',
      useTextOnly: 'Use Text Only',
      cannotStartVoiceError: 'Cannot start voice-guided meditation. Please fix voice service issues or disable voice guidance.',
      voiceNotReady: 'Please wait for voice generation to complete before starting meditation.',
      voiceReady: 'Voice Guidance Ready!',
      voiceReadyDesc: 'Your personalized meditation guidance has been generated and is ready to play.',
      generateVoice: 'Generate Voice Guidance',
      waitingForVoice: 'Waiting for Voice...',
      startMeditation: 'Start Meditation',
      aiGuidance: 'AI Guidance',
      completed: 'Meditation Complete!',
      newSession: 'New Session',
      repeatSession: 'Repeat Session',
      types: {
        mindfulness: 'Mindfulness',
        mindfulnessDesc: 'Focus on present moment awareness',
        lovingKindness: 'Loving Kindness',
        lovingKindnessDesc: 'Cultivate compassion and love',
        nature: 'Nature Connection',
        natureDesc: 'Connect with natural elements',
        sleep: 'Sleep Preparation',
        sleepDesc: 'Prepare for restful sleep',
        energy: 'Energy Boost',
        energyDesc: 'Increase vitality and focus'
      }
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
      emergency: 'आपातकाल',
      meditation: 'ध्यान'
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
      meditationMode: 'ध्यान',
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
      voiceInput: 'वॉयस इनपुट (जल्द आ रहा है)',
      startVoice: 'वॉयस इनपुट शुरू करें',
      stopVoice: 'वॉयस इनपुट बंद करें',
      send: 'संदेश भेजें',
      listening: 'सुन रहा हूं...',
      listeningPlaceholder: 'अब बोलें...',
      hideSidebar: 'साइडबार छुपाएं',
      showSidebar: 'साइडबार दिखाएं',
      backToMenu: 'मेनू पर वापस जाएं',
      activeChat: 'सक्रिय चैट',
      closeSidebar: 'साइडबार बंद करें',
      initializing: 'आपके आध्यात्मिक गाइड को तैयार कर रहे हैं...',
      creating: 'बना रहे हैं...',
      history: 'चैट इतिहास',
      newChat: 'नई चैट',
      delete: 'चैट हटाएं',
      chats: 'चैट्स',
      about: 'के बारे में',
      recentChats: 'हाल की चैट्स',
      noHistory: 'अभी तक कोई चैट इतिहास नहीं',
      startChatting: 'अपनी चैट्स यहां देखने के लिए बातचीत शुरू करें',
      aboutDescription: 'उत्तराखंड के लिए आपका AI-संचालित आध्यात्मिक गाइड। मैं तीर्थयात्राओं की योजना बनाने, मंदिर खोजने, मौसम जांचने और हिमालय की समृद्ध संस्कृति खोजने में मदद कर सकता हूं।',
      features: 'विशेषताएं',
      feature1: 'मंदिर और तीर्थयात्रा की जानकारी',
      feature2: 'वास्तविक समय मौसम अपडेट',
      feature3: 'मार्ग योजना और नेविगेशन',
      feature4: 'सांस्कृतिक अंतर्दृष्टि और परंपराएं',
      feature5: 'वॉयस इनपुट समर्थन',
      feature6: 'बहु-भाषा समर्थन',
      stats: 'आंकड़े',
      totalChats: 'कुल चैट्स',
      currentMessages: 'वर्तमान संदेश',
      lastResponseTime: 'अंतिम प्रतिक्रिया समय',
      you: 'आप',
      responseTime: 'प्रतिक्रिया समय',
      error: 'त्रुटि',
      suggestion1: 'केदारनाथ मंदिर के बारे में बताएं',
      suggestion2: 'चार धाम जाने का सबसे अच्छा समय',
      suggestion3: 'आज ऋषिकेश में मौसम कैसा है',
      suggestion4: '7 दिन की आध्यात्मिक यात्रा की योजना बनाएं'
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
    },

    // Meditation Page
    meditation: {
      title: 'AI-निर्देशित ध्यान',
      subtitle: 'व्यक्तिगत ध्यान मार्गदर्शन के साथ आंतरिक शांति पाएं',
      selectType: 'अपना ध्यान प्रकार चुनें',
      selectDuration: 'अवधि चुनें',
      settings: 'सेटिंग्स',
      breathingPattern: 'सांस लेने का पैटर्न',
      voiceGuidance: 'आवाज़ मार्गदर्शन',
      voiceSpeed: 'आवाज़ की गति',
      voiceSelection: 'आवाज़ चुनें',
      voiceServiceError: 'आवाज़ सेवा उपलब्ध नहीं',
      voiceErrorHelp: 'आवाज़-निर्देशित ध्यान के लिए:',
      retryVoice: 'आवाज़ सेवा पुनः प्रयास करें',
      useTextOnly: 'केवल टेक्स्ट का उपयोग करें',
      cannotStartVoiceError: 'आवाज़-निर्देशित ध्यान शुरू नहीं कर सकते। कृपया आवाज़ सेवा की समस्याओं को ठीक करें या आवाज़ मार्गदर्शन को अक्षम करें।',
      voiceNotReady: 'ध्यान शुरू करने से पहले आवाज़ जेनरेशन पूरा होने का इंतज़ार करें।',
      voiceReady: 'आवाज़ मार्गदर्शन तैयार!',
      voiceReadyDesc: 'आपका व्यक्तिगत ध्यान मार्गदर्शन तैयार हो गया है और चलाने के लिए तैयार है।',
      generateVoice: 'आवाज़ मार्गदर्शन जेनरेट करें',
      waitingForVoice: 'आवाज़ का इंतज़ार...',
      startMeditation: 'ध्यान शुरू करें',
      aiGuidance: 'AI मार्गदर्शन',
      completed: 'ध्यान पूर्ण!',
      newSession: 'नया सत्र',
      repeatSession: 'सत्र दोहराएं',
      types: {
        mindfulness: 'सचेतता',
        mindfulnessDesc: 'वर्तमान क्षण की जागरूकता पर ध्यान दें',
        lovingKindness: 'प्रेम-दया',
        lovingKindnessDesc: 'करुणा और प्रेम विकसित करें',
        nature: 'प्रकृति संबंध',
        natureDesc: 'प्राकृतिक तत्वों से जुड़ें',
        sleep: 'नींद की तैयारी',
        sleepDesc: 'आरामदायक नींद के लिए तैयार हों',
        energy: 'ऊर्जा बूस्ट',
        energyDesc: 'जीवन शक्ति और फोकस बढ़ाएं'
      }
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
      emergency: 'मुसीबत',
      meditation: 'ध्यान'
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
      meditationMode: 'ध्यान',
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
      voiceInput: 'आवाज इनपुट (जल्द आएगा)',
      startVoice: 'आवाज इनपुट शुरू करो',
      stopVoice: 'आवाज इनपुट बंद करो',
      send: 'संदेश भेजो',
      listening: 'सुन रहा हूं...',
      listeningPlaceholder: 'अब बोलो...',
      hideSidebar: 'साइडबार छुपाओ',
      showSidebar: 'साइडबार दिखाओ',
      backToMenu: 'मेनू पर वापस जाओ',
      activeChat: 'सक्रिय चैट',
      closeSidebar: 'साइडबार बंद करो',
      initializing: 'तुम्हारे आध्यात्मिक गाइड को तैयार कर रहे हैं...',
      creating: 'बना रहे हैं...',
      history: 'चैट इतिहास',
      newChat: 'नई चैट',
      delete: 'चैट हटाओ',
      chats: 'चैट्स',
      about: 'के बारे में',
      recentChats: 'हाल की चैट्स',
      noHistory: 'अभी तक कोई चैट इतिहास नहीं',
      startChatting: 'अपनी चैट्स यहां देखने के लिए बातचीत शुरू करो',
      aboutDescription: 'उत्तराखंड के लिए तुम्हारा AI-संचालित आध्यात्मिक गाइड। मैं तीर्थयात्राओं की योजना बनाने, मंदिर खोजने, मौसम जांचने और हिमालय की समृद्ध संस्कृति खोजने में मदद कर सकता हूं।',
      features: 'विशेषताएं',
      feature1: 'मंदिर और तीर्थयात्रा की जानकारी',
      feature2: 'वास्तविक समय मौसम अपडेट',
      feature3: 'मार्ग योजना और नेविगेशन',
      feature4: 'सांस्कृतिक अंतर्दृष्टि और परंपराएं',
      feature5: 'आवाज इनपुट समर्थन',
      feature6: 'बहु-भाषा समर्थन',
      stats: 'आंकड़े',
      totalChats: 'कुल चैट्स',
      currentMessages: 'वर्तमान संदेश',
      lastResponseTime: 'अंतिम प्रतिक्रिया समय',
      you: 'तुम',
      responseTime: 'प्रतिक्रिया समय',
      error: 'त्रुटि',
      suggestion1: 'केदारनाथ मंदिर के बारे में बताओ',
      suggestion2: 'चार धाम जाने का सबसे बढ़िया समय',
      suggestion3: 'आज ऋषिकेश में मौसम कैसा है',
      suggestion4: '7 दिन की आध्यात्मिक यात्रा की योजना बनाओ'
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
    },

    // Meditation Page
    meditation: {
      title: 'AI-निर्देशित ध्यान',
      subtitle: 'व्यक्तिगत ध्यान मार्गदर्शन के साथ मन की शांति पाओ',
      selectType: 'अपना ध्यान प्रकार चुनो',
      selectDuration: 'समय चुनो',
      settings: 'सेटिंग्स',
      breathingPattern: 'सांस का तरीका',
      voiceGuidance: 'आवाज़ मार्गदर्शन',
      voiceSpeed: 'आवाज़ की गति',
      voiceSelection: 'आवाज़ चुनो',
      voiceServiceError: 'आवाज़ सेवा उपलब्ध नहीं',
      voiceErrorHelp: 'आवाज़-निर्देशित ध्यान के लिए:',
      retryVoice: 'आवाज़ सेवा दोबारा कोशिश करो',
      useTextOnly: 'सिर्फ टेक्स्ट इस्तेमाल करो',
      cannotStartVoiceError: 'आवाज़-निर्देशित ध्यान शुरू नहीं कर सकते। आवाज़ सेवा की समस्याओं को ठीक करो या आवाज़ मार्गदर्शन बंद करो।',
      voiceNotReady: 'ध्यान शुरू करने से पहले आवाज़ जेनरेशन पूरा होने का इंतज़ार करो।',
      voiceReady: 'आवाज़ मार्गदर्शन तैयार!',
      voiceReadyDesc: 'तुम्हारा व्यक्तिगत ध्यान मार्गदर्शन तैयार हो गया है और चलाने के लिए तैयार है।',
      generateVoice: 'आवाज़ मार्गदर्शन बनाओ',
      waitingForVoice: 'आवाज़ का इंतज़ार...',
      startMeditation: 'ध्यान शुरू करो',
      aiGuidance: 'AI मार्गदर्शन',
      completed: 'ध्यान पूरा!',
      newSession: 'नया सत्र',
      repeatSession: 'सत्र दोहराओ',
      types: {
        mindfulness: 'सचेतता',
        mindfulnessDesc: 'वर्तमान क्षण की जागरूकता पर ध्यान दो',
        lovingKindness: 'प्रेम-दया',
        lovingKindnessDesc: 'करुणा और प्रेम बढ़ाओ',
        nature: 'प्रकृति संबंध',
        natureDesc: 'प्राकृतिक तत्वों से जुड़ो',
        sleep: 'नींद की तैयारी',
        sleepDesc: 'आरामदायक नींद के लिए तैयार हो',
        energy: 'ऊर्जा बूस्ट',
        energyDesc: 'जीवन शक्ति और फोकस बढ़ाओ'
      }
    }
  }
})