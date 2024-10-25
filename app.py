import eventlet
eventlet.monkey_patch(socket=True, select=True)

from logtail import LogtailHandler
from server import create_app, handler

import logging

mode = 'dev' # Controls whether the server will use built client static files or not (prod or dev)
app, socketio = create_app(mode)
app.logger.setLevel(logging.DEBUG)
app.logger.addHandler(handler)
app.logger.addHandler(LogtailHandler(source_token='r7bKwtvkMf9iBBqAsYXmJyFS'))

# Handle stop signal. Could not seem to make it work inside routes or init.
from flask import request
from server.dashboard.globals import stop_signals
@socketio.on('stop_llm_stream')
def handle_stop_signal():
    client_id = request.sid
    stop_signals[client_id] = True

if __name__ == '__main__':
    socketio.run(app, debug = True)
