import eventlet
eventlet.monkey_patch(socket=True, select=True)

from server.general.utils import send_autoupdate_log
from logtail import LogtailHandler
from server import create_app, handler

import logging


mode = 'prod' # Controls whether the server will use built client static files or not (prod or dev)
app, socketio = create_app(mode)
app.logger.setLevel(logging.DEBUG)
app.logger.addHandler(handler)
app.logger.addHandler(LogtailHandler(source_token='r7bKwtvkMf9iBBqAsYXmJyFS'))



@app.before_request
def init_send_logs():
    # prevent spamming
    if not app.config['INIT_LOGS_SENT']:
        send_autoupdate_log()
        app.config['INIT_LOGS_SENT'] = True


# Handle stop signal. Could not seem to make it work inside routes or init.
from flask import request
from server.dashboard.globals import stop_signals
@socketio.on('stop_llm_stream')
def handle_stop_signal():
    client_id = request.sid
    stop_signals[client_id] = True

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug = True)
