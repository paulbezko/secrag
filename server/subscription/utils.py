from ..general.utils import reconnect_to_db, log
from psycopg2 import OperationalError, InterfaceError
from flask import current_app
import time

def get_user_data_stripe(stripe_user_id, retries=3):

    attempt = 0
    while attempt < retries:
        try:
            connection = current_app.config['DB_CONNECTION']
            with connection.cursor() as cursor:
                query = f"SELECT * FROM users_{current_app.config['MODE']} WHERE stripe_user_id = %s"
                cursor.execute(query, (stripe_user_id,))
                return cursor.fetchone()
        
        except (OperationalError, InterfaceError) as conn_error:
            log('warning', f'Connection error [Attempt {attempt + 1}/{retries}]: {conn_error}')
            attempt += 1
            reconnect_to_db()
            time.sleep(2)  # Optional delay before retrying
        
        except Exception as error:
            log('error', f'Error [Get User Data]: {error}')
            break
    
    log('fatal', 'Failed to retrieve user data after multiple attempts.')
    return None