import hmac
import hashlib
import os
import threading
import time
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from fastapi import Request, status
import subprocess

load_dotenv('.env', override=True)
# Your secret (set the same as in GitHub webhook settings)
SECRET = os.getenv('GITHUB_WEBHOOK_SECRET').encode('utf-8')

# Specify the branch you want to listen for
TARGET_BRANCH = 'alpha'  # Change this to your target branch
DELAY_BEFORE_UPDATE = 0.8 # Delay in seconds

from fastapi import APIRouter

routes = APIRouter()

def verify_signature(request, payload):
    signature = request.headers.get('X-Hub-Signature')
    if not signature:
        return False
    # Calculate the HMAC
    hash_name, signature = signature.split('=')
    if hash_name != 'sha1':
        return False
    hash = hmac.new(SECRET, payload, hashlib.sha1)
    return hmac.compare_digest(signature, hash.hexdigest())

@routes.post('/push')
async def webhook(request: Request):
    payload = await request.body()

    # Verify the signature
    if not verify_signature(request, payload):
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content="")  # Forbidden

    data = await request.json()

    # Check if the push is on the desired branch
    if 'ref' in data and data['ref'] == f'refs/heads/{TARGET_BRANCH}':
        print("[SecRag] Updated detected. Begin update...")
        thread = threading.Thread(target=delayed_update)
        thread.start()
        return JSONResponse(status_code=status.HTTP_200_OK, content="")
    else:
        # If it's not the target branch, return 404
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content="")

def delayed_update():
    """Function to delay execution and run the shell script."""
    time.sleep(DELAY_BEFORE_UPDATE)

    result = subprocess.run(['sudo', 'systemctl', 'start', 'secrag-autoupdate'], check=True, text=True)