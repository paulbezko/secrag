import hmac
import hashlib
import os
from dotenv import load_dotenv
from flask import Flask, request, abort
import subprocess

app = Flask(__name__)
load_dotenv('.env', override=True)
# Your secret (set the same as in GitHub webhook settings)
SECRET = os.getenv('GITHUB_WEBHOOK_SECRET').encode('utf-8')

PATH_TO_THE_REPO = '/path/to/your/repo'
# Specify the branch you want to listen for
TARGET_BRANCH = 'test_webhook'  # Change this to your target branch

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

@app.route('/push', methods=['POST'])
def webhook():
    payload = request.get_data()

    # Verify the signature
    if not verify_signature(payload):
        abort(403)  # Forbidden

    data = request.json

    # Check if the push is on the desired branch
    if 'ref' in data and data['ref'] == f'refs/heads/{TARGET_BRANCH}':
        os.chdir(PATH_TO_THE_REPO) 
        subprocess.run(['git', 'pull', 'origin', TARGET_BRANCH])
        # Restart the Gunicorn service
        subprocess.run(['systemctl', 'restart', 'secrag.service'])
        return '', 200
    else:
        # If it's not the target branch, return 404
        abort(404)