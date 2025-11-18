# How to Start the Backend Server

## Quick Start

**Option 1: Double-click the batch file**
- Double-click `start_server.bat` in this directory

**Option 2: Command line**
```bash
cd "C:\Bershaw Recruitment\recruit-assist-api"
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## What You Should See

When the server starts successfully, you'll see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## Test the Server

Once running, open these URLs in your browser:

1. **Health Check**: http://localhost:8000/healthz
   - Should return: `{"ok": true}`

2. **API Documentation**: http://localhost:8000/docs
   - Interactive API documentation

3. **Alternative Docs**: http://localhost:8000/redoc
   - Alternative API documentation

## Troubleshooting

### Port 8000 Already in Use
If you get an error about port 8000 being in use:
- Change the port: `--port 8001`
- Update `API_BASE_URL` in `recruit-assist-web/dashboard.js` to match

### Module Not Found
If you see `ModuleNotFoundError`:
```bash
pip install --user fastapi uvicorn[standard] pydantic pydantic-settings python-multipart openai python-dotenv
```

### Python Not Found
Make sure Python 3.10+ is installed and in your PATH.

## Keep This Window Open

**Important**: Keep the terminal window open while the server is running. Closing it will stop the server.

To stop the server, press `Ctrl+C` in the terminal window.

