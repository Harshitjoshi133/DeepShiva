# ⚡ Quick Start Guide

## Windows Users

### Option 1: Use Batch Scripts (Easiest)

1. **Start Backend** - Double-click `start-backend.bat`
2. **Start Frontend** - Double-click `start-frontend.bat`
3. **Open Browser** - Go to `http://localhost:5173`

### Option 2: Manual Commands

**Terminal 1 (Backend):**
```cmd
cd server
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

**Terminal 2 (Frontend):**
```cmd
cd client
npm install
npm run dev
```

## Linux/Mac Users

**Terminal 1 (Backend):**
```bash
cd server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

**Terminal 2 (Frontend):**
```bash
cd client
npm install
npm run dev
```

## ✅ Verify Installation

1. Backend: Visit `http://localhost:8000/docs`
2. Frontend: Visit `http://localhost:5173`
3. Test chat, yoga, dashboard features

## 🎯 What to Test

### 1. Chat Interface
- Type: "Tell me about Kedarnath"
- Should see mock AI response

### 2. Yoga Sentinel
- Allow camera access
- Click "Analyze Pose"
- See feedback card

### 3. Dashboard
- View crowd chart
- Enter distance: 100, vehicle: car
- Click Calculate

### 4. Culture Hub
- Browse products
- Click heart icons

### 5. Emergency
- View emergency numbers
- Expand first aid tips

## 🔧 Common Issues

**Backend won't start:**
- Check Python version: `python --version` (need 3.9+)
- Try: `python3` instead of `python`

**Frontend won't start:**
- Check Node version: `node --version` (need 18+)
- Delete `node_modules` and run `npm install` again

**Camera not working:**
- Allow camera permissions in browser
- Use HTTPS or localhost only

## 📝 Next Steps

Once everything works:
1. Read `PROJECT_OVERVIEW.md` for architecture
2. Check `TODO` comments in code for integration points
3. Start integrating Ollama LLM
4. Add computer vision model

---

**Need Help?** Check `SETUP.md` for detailed troubleshooting