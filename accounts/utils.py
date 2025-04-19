import os
import time
import requests


def refresh_discord_token(discord_account):
    refresh_token = discord_account.extra_data.get('refresh_token')
    expires_at = discord_account.extra_data.get('auth_time', 0) + discord_account.extra_data.get('expires_in', 0)

    # If token is still valid, return it
    if time.time() < expires_at:
        return discord_account.extra_data['access_token']

    # Prepare token refresh request
    data = {
        'client_id': os.getenv('DISCORD_CLIENT_ID'),
        'client_secret': os.getenv('DISCORD_CLIENT_SECRET'),
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'redirect_uri': os.getenv('DISCORD_REDIRECT_URI', ''),  # Optional
        'scope': 'identify email'
    }

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post('https://discord.com/api/oauth2/token', data=data, headers=headers)

    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data['access_token']
        expires_in = token_data['expires_in']
        new_refresh_token = token_data.get('refresh_token', refresh_token)

        # Update stored token info
        discord_account.extra_data.update({
            'access_token': access_token,
            'refresh_token': new_refresh_token,
            'expires_in': expires_in,
            'auth_time': int(time.time())
        })
        discord_account.save()

        return access_token
    else:
        raise Exception('Failed to refresh Discord token')
