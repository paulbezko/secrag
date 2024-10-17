from server import create_app, handler
import logging

mode = 'prod' # Controls whether the server will use built client static files or not (prod or dev)
app = create_app(mode)
app.logger.setLevel(logging.DEBUG)
app.logger.addHandler(handler)

if __name__ == '__main__':
    app.run(debug = False)