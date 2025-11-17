# Quick Start Guide - Web Frontend

## 🚀 Get Started in 30 Seconds

1. **Navigate to the frontend directory:**
   ```bash
   cd recruit-assist-web
   ```

2. **Start a simple server:**
   ```bash
   python -m http.server 8080
   ```
   (Or use any HTTP server - Node.js, PHP, etc.)

3. **Open in browser:**
   ```
   http://localhost:8080
   ```

That's it! You now have a professional landing page and dashboard ready to show clients.

## 📋 What You Get

✅ **Landing Page** - Professional homepage with:
- Hero section with value proposition
- Features showcase
- "How It Works" section
- Call-to-action buttons

✅ **Dashboard** - Full-featured interface with:
- Stats cards (ready for real data)
- Candidate pipeline view
- Analytics section
- Quick tools (CV upload, JD normalize, etc.)

✅ **Modern Design** - Clean, professional UI that matches leading SaaS platforms

## 🔗 Connect to Backend

The dashboard is pre-configured to connect to your FastAPI backend at `http://localhost:8000`.

**To test with backend:**
1. Start your FastAPI server: `uvicorn app.main:app --reload`
2. Open dashboard: `http://localhost:8080/dashboard.html`
3. Try the "Quick Tools" - they'll call your API endpoints

## 🎨 Customize

- **Colors**: Edit CSS variables in `styles.css`
- **Content**: Update text in `index.html` and `dashboard.html`
- **Branding**: Change logo and company name in navigation

## 📱 Demo Tips

- Works great on mobile (responsive design)
- All buttons and forms are functional (connect to backend)
- Professional enough to show clients while backend work continues

## 🐛 Troubleshooting

**CORS errors?** Make sure your FastAPI backend has CORS enabled:
```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["*"])
```

**API not connecting?** Check `API_BASE_URL` in `dashboard.js` matches your backend URL.

---

**Ready to impress!** 🎉

