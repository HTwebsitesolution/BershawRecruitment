# Bershaw Recruitment - Web Frontend

Modern, professional landing page and dashboard for the Bershaw Recruitment platform.

## Features

- **Landing Page**: Beautiful, conversion-focused homepage showcasing platform features
- **Dashboard**: Analytics and pipeline management interface
- **API Integration**: Ready to connect to FastAPI backend
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Modern UI**: Clean, professional design inspired by leading SaaS platforms

## File Structure

```
recruit-assist-web/
├── index.html          # Landing page
├── dashboard.html      # Dashboard interface
├── styles.css          # Main stylesheet
├── dashboard.css       # Dashboard-specific styles
├── script.js           # Landing page JavaScript
├── dashboard.js        # Dashboard functionality
└── README.md           # This file
```

## Setup

### Option 1: Simple HTTP Server (Recommended for Demo)

1. Navigate to the `recruit-assist-web` directory:
   ```bash
   cd recruit-assist-web
   ```

2. Start a simple HTTP server:

   **Python 3:**
   ```bash
   python -m http.server 8080
   ```

   **Node.js (if you have http-server installed):**
   ```bash
   npx http-server -p 8080
   ```

3. Open your browser and navigate to:
   ```
   http://localhost:8080
   ```

### Option 2: Serve with Backend (Production)

If you're running the FastAPI backend, you can serve the frontend files using FastAPI's static file serving:

```python
from fastapi.staticfiles import StaticFiles

app.mount("/", StaticFiles(directory="recruit-assist-web", html=True), name="static")
```

## Backend Integration

The dashboard is configured to connect to the FastAPI backend at `http://localhost:8000`. 

**Important**: Make sure your backend is running and CORS is configured to allow requests from the frontend origin.

To change the API URL, update the `API_BASE_URL` constant in `dashboard.js`:

```javascript
const API_BASE_URL = 'http://localhost:8000'; // Change to your backend URL
```

## Features Overview

### Landing Page (`index.html`)

- Hero section with compelling value proposition
- Features grid showcasing platform capabilities
- "How It Works" step-by-step guide
- Call-to-action sections
- Professional footer

### Dashboard (`dashboard.html`)

- **Stats Cards**: Key metrics at a glance
- **Candidate Pipeline**: View and filter candidates
- **Analytics**: Engagement trends and metrics
- **Quick Tools**: 
  - CV Upload & Parsing
  - JD Normalization
  - Endorsement Generation
  - Tone Profile Settings

## Customization

### Colors

Edit the CSS variables in `styles.css`:

```css
:root {
    --primary: #2563eb;      /* Primary brand color */
    --primary-dark: #1d4ed8; /* Darker shade */
    --accent: #10b981;       /* Accent color */
    --text: #1e293b;         /* Main text color */
    /* ... */
}
```

### Content

- Update text content directly in the HTML files
- Modify feature descriptions in `index.html`
- Customize dashboard sections in `dashboard.html`

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Next Steps

1. **Connect Real Data**: Replace mock data in `dashboard.js` with actual API calls
2. **Add Charts**: Integrate a charting library (Chart.js, D3.js) for analytics visualization
3. **Authentication**: Add login/signup flow
4. **Real-time Updates**: Consider WebSocket integration for live pipeline updates
5. **Progressive Web App**: Add service worker for offline capability

## Notes

- The dashboard currently uses mock data - replace with real API calls as backend endpoints become available
- File upload functionality requires backend support for multipart/form-data
- All API calls include error handling with user-friendly alerts

## License

Part of the Bershaw Recruitment platform.

