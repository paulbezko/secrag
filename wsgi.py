import eventlet
eventlet.monkey_patch()

from app import app

if __name__ == '__main__':
    app.run(debug=False)