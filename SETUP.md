# 🚀 Deep-Shiva Setup Guide

## Step-by-Step Installation

### 1️⃣ Backend Setup (5 minutes)

Open a terminal and run:

```bash
# Navigate to server directory
cd server

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the backend server
python run.py
```

✅ Backend should now be running at `http://localhost:8000`
✅ Visit `http://localhost:8000/docs` to see API documentation

### 2️⃣ Frontend Setup (5 minutes)

Open a NEW terminal and run:

```bash
# Navigate to client directory
cd client

# Install dependencies
npm install

# Start the development server
npm run dev
```

✅ Frontend should now be running at `http://localhost:5173`
✅ Open your browser and visit `http://localhost:5173`

## 🧪 Testing the Application

### Test Chat Interface
1. Navigate to Chat page
2. Type: "Tell me about Kedarnath"
3. You should see a mock response from Deep-Shiva

### Test Yoga Sentinel
1. Navigate to Yoga Sentinel page
2. Allow camera access when prompted
3. Click "Analyze Pose"
4. You should see mock feedback

### Test Dashboard
1. Navigate to Dashboard
2. View crowd status chart
3. Enter distance (e.g., 100) and select vehicle type
4. Click "Calculate" to see carbon footprint

### Test Culture Hub
1. Navigate to Culture page
2. Browse artisan products
3. Click heart icon to favorite items

### Test Emergency SOS
1. Navigate to Emergency page
2. View emergency contact numbers
3. Expand first aid accordion items

## 🔧 Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
# Windows: Find and kill process
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or change port in server/run.py
```

**Module not found:**
```bash
# Ensure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend Issues

**Port 5173 already in use:**
```bash
# Kill the process or change port in vite.config.js
```

**Dependencies not installing:**
```bash
# Clear npm cache
npm cache clean --force
# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**CORS errors:**
- Ensure backend is running on port 8000
- Check CORS settings in `server/app/main.py`

## 📝 Next Steps: Integration

### Connect Ollama LLM
Edit `server/app/routers/chat.py`:
```python
# Add Ollama client
import ollama

@router.post("/query")
async def chat_query(request: ChatRequest):
    response = ollama.chat(
        model='llama2',
        messages=[{'role': 'user', 'content': request.message}]
    )
    return ChatResponse(
        response=response['message']['content'],
        user_id=request.user_id
    )
```

### Add Computer Vision
Edit `server/app/routers/vision.py`:
```python
import cv2
import mediapipe as mp

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Add pose detection logic
```

## 🎯 Production Deployment

### Backend (FastAPI)
- Deploy to Railway, Render, or AWS Lambda
- Set environment variables
- Use production ASGI server (Gunicorn + Uvicorn)

### Frontend (React)
- Build: `npm run build`
- Deploy to Vercel, Netlify, or Cloudflare Pages
- Update API endpoint in production

## 📞 Support

If you encounter issues:
1. Check console logs (F12 in browser)
2. Check terminal output for errors
3. Verify all dependencies are installed
4. Ensure both servers are running

---

**Happy Coding! 🏔️**