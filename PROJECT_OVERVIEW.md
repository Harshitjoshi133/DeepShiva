# 📋 Deep-Shiva Project Overview

## 🎯 Project Goal
Create a competition-winning, production-ready tourism chatbot for Uttarakhand that combines:
- Spiritual guidance and yatra planning
- Real-time yoga posture correction
- Eco-tourism features (carbon calculator)
- Local artisan marketplace
- Emergency services integration

## 🏗️ Architecture

### Frontend (React + Vite)
**Location:** `/client`

**Key Technologies:**
- React 18 with Vite for fast development
- Tailwind CSS for styling (Spiritual Modern theme)
- Framer Motion for smooth animations
- React Router for navigation
- React Webcam for camera access
- Recharts for data visualization

**Pages:**
1. **Home** (`/`) - Landing page with hero section and quick actions
2. **Chat** (`/chat`) - Conversational AI interface with markdown support
3. **Yoga Sentinel** (`/yoga-sentinel`) - Webcam-based pose analysis
4. **Dashboard** (`/dashboard`) - Crowd monitoring + carbon calculator
5. **Culture** (`/culture`) - Artisan product marketplace
6. **Emergency** (`/emergency`) - SOS contacts + first aid guide

**Components:**
- `Layout.jsx` - Main layout with responsive navigation (sidebar + bottom nav)

### Backend (FastAPI)
**Location:** `/server`

**Key Technologies:**
- FastAPI for high-performance API
- Pydantic for data validation
- Uvicorn as ASGI server
- CORS middleware for frontend communication

**API Routes:**

1. **Chat Router** (`/api/v1/chat`)
   - `POST /query` - Chat with AI assistant
   - TODO: Integrate Ollama LLM

2. **Vision Router** (`/api/v1/vision`)
   - `POST /analyze` - Analyze yoga pose from image
   - TODO: Integrate MediaPipe/OpenCV

3. **Tourism Router** (`/api/v1/tourism`)
   - `GET /crowd-status` - Live crowd data at shrines
   - `POST /calculate-carbon` - Carbon footprint calculator
   - TODO: Connect real-time crowd monitoring

4. **Culture Router** (`/api/v1/culture`)
   - `GET /products` - List artisan products
   - TODO: Connect to product database

## 🎨 Design System

### Color Palette (Spiritual Modern)
- **Saffron:** `#FF9933` - Primary actions, highlights
- **Forest Green:** `#228B22` - Secondary actions, nature theme
- **Snow White:** `#FFFFFF` - Backgrounds, text on dark

### Typography
- Clean, accessible fonts
- High contrast for readability
- Large text sizes for mobile

### Accessibility
- WCAG 2.1 AA compliant
- Touch targets minimum 44x44px
- Keyboard navigation support
- Screen reader friendly
- Camera permission error handling

## 📱 Responsive Design

### Mobile (< 768px)
- Bottom navigation bar
- Single column layouts
- Touch-optimized buttons
- Collapsible sidebar

### Desktop (≥ 768px)
- Left sidebar navigation
- Multi-column layouts
- Hover effects
- Larger content areas

## 🔌 Integration Points

### 1. Ollama LLM (Priority: HIGH)
**File:** `server/app/routers/chat.py`

Current: Mock responses
Needed: 
```python
import ollama
# Add conversation context
# Implement RAG with VectorDB
```

### 2. VectorDB for RAG (Priority: HIGH)
**File:** `server/app/routers/chat.py`

Needed:
- ChromaDB or Pinecone integration
- Tourism knowledge base embeddings
- Semantic search for temple info

### 3. Computer Vision (Priority: MEDIUM)
**File:** `server/app/routers/vision.py`

Current: Random mock responses
Needed:
```python
import mediapipe as mp
import cv2
# Pose detection
# Asana classification
```

### 4. Real-time Crowd Data (Priority: MEDIUM)
**File:** `server/app/routers/tourism.py`

Current: Static mock data
Needed:
- Live API integration
- Historical data analysis
- Prediction models

### 5. Product Database (Priority: LOW)
**File:** `server/app/routers/culture.py`

Current: Mock products
Needed:
- Database connection (PostgreSQL/MongoDB)
- Image storage (S3/Cloudinary)
- Payment integration

## 🚀 Deployment Strategy

### Development
- Frontend: `npm run dev` (Vite dev server)
- Backend: `python run.py` (Uvicorn with reload)

### Production

**Backend:**
- Platform: Railway, Render, or AWS Lambda
- Server: Gunicorn + Uvicorn workers
- Environment variables for secrets
- Database: PostgreSQL on Supabase/Railway

**Frontend:**
- Platform: Vercel, Netlify, or Cloudflare Pages
- Build: `npm run build`
- Environment: Update API endpoint
- CDN: Automatic with hosting platform

## 📊 Performance Targets

- First Contentful Paint: < 1.5s
- Time to Interactive: < 3.5s
- Lighthouse Score: > 90
- API Response Time: < 200ms
- Webcam Frame Rate: 30 FPS

## 🔒 Security Considerations

### Current
- CORS configured for localhost
- Input validation with Pydantic
- Error handling without exposing internals

### Production Needed
- Rate limiting
- API authentication (JWT)
- HTTPS only
- Environment variable management
- Input sanitization
- SQL injection prevention

## 📈 Future Enhancements

1. **Voice Input** - Speech-to-text for chat
2. **Offline Mode** - PWA with service workers
3. **Push Notifications** - Weather alerts, crowd updates
4. **Social Features** - Share itineraries, reviews
5. **AR Features** - Temple information overlay
6. **Multi-modal AI** - Image + text queries

## 🧪 Testing Strategy

### Manual Testing Checklist
- [ ] All pages load without errors
- [ ] Navigation works (mobile + desktop)
- [ ] Chat sends and receives messages
- [ ] Webcam access and capture works
- [ ] Charts render correctly
- [ ] Forms validate and submit
- [ ] Responsive on mobile devices
- [ ] Accessibility with screen reader

### Automated Testing (Future)
- Unit tests: Jest + React Testing Library
- API tests: Pytest
- E2E tests: Playwright
- Performance: Lighthouse CI

## 📚 Documentation

- `README.md` - Project overview and features
- `SETUP.md` - Installation and troubleshooting
- `PROJECT_OVERVIEW.md` - This file (architecture)
- API Docs - Auto-generated at `/docs` (FastAPI)

## 🏆 Competition Criteria Alignment

✅ **Innovation** - Unique combination of spiritual + tech
✅ **User Experience** - Intuitive, accessible design
✅ **Technical Excellence** - Modern stack, clean code
✅ **Social Impact** - Supports local artisans, eco-tourism
✅ **Scalability** - Production-ready architecture
✅ **Completeness** - All features functional (with mocks)

## 📞 Quick Commands

```bash
# Start backend
cd server && python run.py

# Start frontend
cd client && npm run dev

# Install backend deps
cd server && pip install -r requirements.txt

# Install frontend deps
cd client && npm install

# Build for production
cd client && npm run build
```

---

**Status:** ✅ Ready for Development & Testing
**Next Step:** Run setup and test all features
**Integration:** Ready for Ollama and VectorDB connection