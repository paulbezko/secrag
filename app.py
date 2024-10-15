import eventlet
eventlet.monkey_patch()

from server import create_app

mode = 'prod' # Controls whether the server will use built client static files or not (prod or dev)
app = create_app(mode)

if __name__ == '__main__':
    app.run(debug = True)
