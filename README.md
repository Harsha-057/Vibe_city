# Vibe City

Vibe City is a roleplay server management system designed to streamline the administration of roleplay communities. It integrates various components such as user account management, job assignments, whitelisting, and a Discord bot for enhanced community interaction.

## 🚀 Features

- **User Accounts**: Manage player profiles and authentication.
- **Dashboard**: Administrative interface for overseeing server activities.
- **Job Management**: Assign and manage in-game jobs for players.
- **Discord Bot**: Facilitates communication and moderation within the community.
- **Whitelisting**: Control access to the server by managing a whitelist of approved players.
- **Web Interface**: User-friendly web pages for interaction and management.

## 🛠️ Technologies Used

- **Backend**: Python
- **Frontend**: HTML, CSS, JavaScript
- **Web Server**: Waitress

# Discord Git Commit Webhook

This script creates a webhook endpoint that receives GitHub webhook events and forwards formatted commit messages to a Discord channel.

## Setup Instructions

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a Discord webhook:
   - Go to your Discord server
   - Select a channel
   - Click the gear icon (Edit Channel)
   - Go to Integrations
   - Click "Create Webhook"
   - Copy the webhook URL

3. Update the `DISCORD_WEBHOOK_URL` in `discord_webhook.py` with your Discord webhook URL.

4. Set up the GitHub webhook:
   - Go to your GitHub repository
   - Go to Settings > Webhooks
   - Click "Add webhook"
   - Set the Payload URL to your server's URL (e.g., `http://your-server:5000/webhook`)
   - Set Content type to `application/json`
   - Select "Just the push event"
   - Click "Add webhook"

5. Run the script:
```bash
python discord_webhook.py
```

The script will start a web server on port 5000 that listens for GitHub webhook events. When a push event is received, it will format the commit message and send it to your Discord channel.

## Message Format

The commit messages will be formatted as follows:
```
Author: [Author Name]
Date: [Commit Date]
Message: [Commit Message]
```

## Security Note

For production use, make sure to:
1. Use HTTPS for your webhook endpoint
2. Implement GitHub webhook secret verification
3. Use environment variables for sensitive data
4. Consider using a proper web server (like Gunicorn) instead of Flask's development server
