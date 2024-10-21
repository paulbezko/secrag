import hmac
import hashlib
import os
import threading
import time
from dotenv import load_dotenv
from flask import Blueprint, Flask, request, abort
import subprocess

load_dotenv('.env', override=True)
# Your secret (set the same as in GitHub webhook settings)
SECRET = os.getenv('GITHUB_WEBHOOK_SECRET').encode('utf-8')

# Specify the branch you want to listen for
TARGET_BRANCH = 'prod'  # Change this to your target branch
AUTOUPDATE_SCRIPT = 'autoupdate.sh'
DELAY_BEFORE_UPDATE = 0.8 # Delay in seconds

# Routes initialization
routes = Blueprint('routes', __name__)

def verify_signature(payload):
    signature = request.headers.get('X-Hub-Signature')
    if not signature:
        return False
    # Calculate the HMAC
    hash_name, signature = signature.split('=')
    if hash_name != 'sha1':
        return False
    hash = hmac.new(SECRET, payload, hashlib.sha1)
    return hmac.compare_digest(signature, hash.hexdigest())

@routes.route('/push', methods=['POST'])
def webhook():
    payload = request.get_data()

    # Verify the signature
    if not verify_signature(payload):
        abort(403)  # Forbidden

    data = request.json

    # Check if the push is on the desired branch
    if 'ref' in data and data['ref'] == f'refs/heads/{TARGET_BRANCH}':
        print("[SecRag] Updated detected. Begin update...")
        thread = threading.Thread(target=delayed_update)
        thread.start()
        return '', 200
    else:
        # If it's not the target branch, return 404
        abort(404)

def delayed_update():
    """Function to delay execution and run the shell script."""
    time.sleep(DELAY_BEFORE_UPDATE)

    with open("autoupdate.log", 'a') as log_file:
        process = subprocess.Popen(['bash', AUTOUPDATE_SCRIPT], stdout=log_file, stderr=subprocess.STDOUT)
        process.wait()  # Wait for the process to finish