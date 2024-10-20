import eventlet
eventlet.monkey_patch()

from logtail import LogtailHandler
from server import create_app, handler
import logging

mode = 'dev' # Controls whether the server will use built client static files or not (prod or dev)
app, socketio = create_app(mode)
app.logger.setLevel(logging.DEBUG)
app.logger.addHandler(handler)
app.logger.addHandler(LogtailHandler(source_token='r7bKwtvkMf9iBBqAsYXmJyFS'))

if __name__ == '__main__':
    socketio.run(app, debug = True)
