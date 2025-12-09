# 🌟 Deep-Shiva Features Documentation

## 1. 🏠 Home / Landing Page

**Route:** `/`

**Features:**
- Hero section with mountain icon and tagline
- Quick action cards for:
  - Check Crowd Status
  - Yoga Mode
  - Emergency Help
- Feature showcase grid
- Language toggle (English/Hindi/Garhwali)
- Smooth animations on load

**User Flow:**
1. User lands on homepage
2. Sees quick actions and features
3. Clicks "Start Your Journey" → Goes to Chat
4. Or clicks quick action cards → Goes to specific feature

---

## 2. 💬 Immersive Chat Interface

**Route:** `/chat`

**Features:**
- Real-time chat with Deep-Shiva AI
- Markdown rendering for formatted responses
- Message history display
- Loading state ("Deep-Shiva is thinking...")
- Voice input button (UI ready)
- Auto-scroll to latest message
- User/Assistant message differentiation

**Technical:**
- API: `POST /api/v1/chat/query`
- Request: `{ message, user_id }`
- Response: `{ response, user_id }`

**Mock Behavior:**
Returns: "I am Deep-Shiva. I will soon be connected to Ollama to answer your question about [User Message]..."

**Integration Point:**
Replace mock with Ollama LLM in `server/app/routers/chat.py`

---

## 3. 🧘 Yoga Sentinel

**Route:** `/yoga-sentinel`

**Features:**
- Live webcam feed
- Skeleton overlay guide (SVG)
- "Analyze Pose" button
- Real-time feedback card with:
  - Status (Perfect/Correction Needed)
  - Detailed feedback text
  - Confidence percentage bar
- Camera error handling
- Tips for best results

**Technical:**
- Uses `react-webcam` library
- Captures screenshot as base64
- API: `POST /api/v1/vision/analyze`
- Request: `{ image: base64_string }`
- Response: `{ status, feedback, confidence }`

**Mock Behavior:**
Returns random feedback:
- "Please lift your arms higher for Warrior Pose..."
- "Excellent form! Your Tree Pose is well-balanced..."
- "Bend your knees slightly more in Chair Pose..."

**Integration Point:**
Add MediaPipe/OpenCV in `server/app/routers/vision.py`

---

## 4. 📊 Yatra Dashboard

**Route:** `/dashboard`

**Features:**

### A. Live Crowd Meter
- Bar chart showing crowd levels at 4 shrines:
  - Kedarnath
  - Badrinath
  - Gangotri
  - Yamunotri
- Color-coded status:
  - Green: Light (< 40%)
  - Orange: Moderate (40-70%)
  - Red: Heavy (> 70%)
- Status cards below chart

**Technical:**
- Uses Recharts library
- API: `GET /api/v1/tourism/crowd-status`
- Response: `[{ shrine, crowd_level, status }]`

### B. Carbon Footprint Calculator
- Input fields:
  - Distance (km)
  - Vehicle type (Car/Bike/Bus/EV)
- Calculate button
- Results display:
  - CO₂ emissions in kg
  - Comparison vs. standard SUV
  - Eco-friendly tips

**Technical:**
- API: `POST /api/v1/tourism/calculate-carbon`
- Request: `{ distance, vehicle_type }`
- Response: `{ co2_kg, saved_vs_suv, vehicle_type, distance }`

**Emission Factors:**
- Car: 0.21 kg/km
- Bike: 0.10 kg/km
- Bus: 0.08 kg/km
- EV: 0.05 kg/km
- SUV: 0.30 kg/km (baseline)

---

## 5. 🎨 Culture & Artisan Hub

**Route:** `/culture`

**Features:**
- Grid layout of artisan products
- Each product card shows:
  - Product image (placeholder)
  - Product name
  - Description
  - Price in ₹
  - Artisan name
  - Favorite heart button
  - View button
- Hover effects and animations
- Favorite toggle functionality

**Technical:**
- API: `GET /api/v1/culture/products`
- Response: `[{ id, name, description, price, artisan, image }]`

**Mock Products:**
1. Aipan Art Canvas - ₹1,500
2. Woolen Shawl - ₹2,500
3. Ringal Basket - ₹800
4. Copper Water Bottle - ₹1,200
5. Himalayan Honey - ₹600

**Integration Point:**
Connect to product database and payment gateway

---

## 6. 🚨 Emergency SOS

**Route:** `/emergency`

**Features:**

### A. Emergency Contacts
- Large, touch-friendly buttons for:
  - Police (100)
  - Ambulance (108)
  - Disaster Management (1070)
- Color-coded by service type
- One-tap calling (UI ready)

### B. Offline First Aid Guide
- Accordion-style expandable tips
- Covers 4 common emergencies:
  1. **Altitude Sickness**
     - Symptoms: Headache, nausea, dizziness
     - Treatment: Descend, rest, hydrate
  2. **Hypothermia**
     - Symptoms: Shivering, confusion
     - Treatment: Warm shelter, remove wet clothes
  3. **Dehydration**
     - Symptoms: Extreme thirst, dark urine
     - Treatment: Drink water slowly, rest in shade
  4. **Snake Bite**
     - Symptoms: Puncture marks, swelling
     - Treatment: Stay calm, get to hospital

**Technical:**
- No API calls (offline-first)
- Static content stored in component
- Expandable/collapsible sections

---

## 7. 🎨 Layout & Navigation

**Component:** `Layout.jsx`

**Features:**

### Desktop (≥ 1024px)
- Left sidebar navigation
- Sticky header with logo and language toggle
- Main content area

### Mobile (< 1024px)
- Top header with hamburger menu
- Bottom navigation bar (5 main items)
- Slide-out sidebar on menu click

**Navigation Items:**
- Home
- Chat
- Yoga
- Dashboard
- Culture
- SOS (desktop only, accessible via menu on mobile)

**Language Toggle:**
- Dropdown selector
- Options: English, हिंदी, गढ़वळी
- UI ready (translation logic to be added)

---

## 🎨 Design System

### Colors
```css
--saffron: #FF9933
--forest: #228B22
--snow: #FFFFFF
```

### Button Styles
- `.btn-primary` - Saffron background
- `.btn-secondary` - Forest green background
- `.card` - White background with shadow

### Animations
- Page transitions: Fade + slide up
- Hover effects: Scale 1.05
- Loading states: Spin animation

### Accessibility
- High contrast text
- Large touch targets (44x44px minimum)
- Keyboard navigation
- Screen reader labels
- Error messages

---

## 📱 Responsive Breakpoints

- Mobile: < 768px
- Tablet: 768px - 1023px
- Desktop: ≥ 1024px

---

## 🔌 API Summary

| Endpoint | Method | Purpose | Status |
|----------|--------|---------|--------|
| `/api/v1/chat/query` | POST | Chat with AI | Mock |
| `/api/v1/vision/analyze` | POST | Analyze yoga pose | Mock |
| `/api/v1/tourism/crowd-status` | GET | Get crowd data | Mock |
| `/api/v1/tourism/calculate-carbon` | POST | Calculate CO₂ | Working |
| `/api/v1/culture/products` | GET | Get products | Mock |

---

## ✅ Testing Checklist

- [ ] Home page loads with animations
- [ ] Navigation works on mobile and desktop
- [ ] Chat sends messages and receives responses
- [ ] Webcam activates and captures images
- [ ] Crowd chart renders correctly
- [ ] Carbon calculator computes accurately
- [ ] Products display in grid
- [ ] Emergency accordion expands/collapses
- [ ] Language toggle changes (UI only)
- [ ] All pages are responsive
- [ ] No console errors

---

**All features are functional with mock data and ready for integration!**