import os
import psycopg2
from ..general.utils import log
from psycopg2.extras import RealDictCursor
from psycopg2 import OperationalError, InterfaceError
import time
from ..globals import config

def get_user_data_stripe(stripe_user_id, retries=3):

    attempt = 0
    while attempt < retries:
        try:
            connection = psycopg2.connect(
                host        = os.getenv('DB_HOST'),
                port        = os.getenv('DB_PORT'),
                database    = os.getenv('DB_NAME'),
                user        = os.getenv('DB_USER'),
                password    = os.getenv('DB_PASS'),
                cursor_factory = RealDictCursor
            )
            with connection.cursor() as cursor:
                query = f"SELECT * FROM users_{config.get('MODE')} WHERE stripe_user_id = %s"
                cursor.execute(query, (stripe_user_id,))
                return cursor.fetchone()
        
        except (OperationalError, InterfaceError) as conn_error:
            log('warning', f'Connection error [Attempt {attempt + 1}/{retries}]: {conn_error}')
            attempt += 1
            time.sleep(2)  # Optional delay before retrying
        
        except Exception as error:
            log('error', f'Error [Get User Data]: {error}')
            break

        finally:
            connection.close()
    
    log('fatal', 'Failed to retrieve user data after multiple attempts.')
    return None