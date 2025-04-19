import time

def set_auth_time(backend, details, response, *args, **kwargs):
    return {
        'extra_data': {
            'auth_time': int(time.time())
        }
    }
