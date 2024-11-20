import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from server import create_app
from server.globals import config as global_config
import uvicorn

load_dotenv('.env', override=True)

mode = 'prod' # Controls whether the server will use built client static files or not (prod or dev)
app, socketio, config = create_app(mode)

global_config.set(config)

@app.get("/style.css")
async def serve_css():
    return FileResponse(css_file_path)

# Handle stop signal. Could not seem to make it work inside routes or init.
from server.globals import stop_signals
@socketio.on('stop_llm_stream')
async def handle_stop_signal(sid, data):
    stop_signals[sid] = True


if __name__ == '__main__':
    uvicorn.run(app, port=5000)
