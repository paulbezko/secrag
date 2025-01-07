from dotenv import load_dotenv
from server import create_app
import uvicorn

load_dotenv('.env', override=True)

# Mode is specified by the environmental variable 'APP_MODE' now. (dev or prod)
app, socketio = create_app()


# Handle stop signal. Could not seem to make it work inside routes or init.
from server.globals import stop_signals
@socketio.on('stop_llm_stream')
async def handle_stop_signal(sid):
    stop_signals[sid] = True


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=5000)
