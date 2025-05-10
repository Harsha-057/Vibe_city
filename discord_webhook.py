import json
import requests
from flask import Flask, request, jsonify
import os
from datetime import datetime
import hmac
import hashlib

app = Flask(__name__)

# Discord webhook URL - Replace with your actual webhook URL
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1369247208829882409/rAV8sOYjIPsEkvr0_dqafYOeQoWdu2T28puXOf_fm_HjGEVK97S6gYTIExbFcnV4bWjO"
# GitHub webhook secret - Replace with your actual secret
GITHUB_WEBHOOK_SECRET = "vibecity2.0"

def verify_github_signature(payload_body, signature_header):
    """Verify that the webhook request came from GitHub"""
    if not signature_header:
        return False
    
    expected_signature = hmac.new(
        GITHUB_WEBHOOK_SECRET.encode('utf-8'),
        payload_body,
        hashlib.sha1
    ).hexdigest()
    
    return hmac.compare_digest(f"sha1={expected_signature}", signature_header)

def build_discord_embed(payload, commit):
    repo = payload['repository']
    author = commit['author']['name']
    project = repo['name']
    # Extract branch from ref (refs/heads/branchname)
    branch = payload['ref'].split('/')[-1]
    show_branch = branch != 'main'
    commit_id = commit['id'][:6]
    commit_url = commit['url']
    message_lines = [line for line in commit['message'].split('\n') if line.strip()]
    merged_time = commit['timestamp']  # ISO format
    merged_dt = datetime.fromisoformat(merged_time.replace('Z', '+00:00'))
    merged_time_str = merged_dt.strftime('%I:%M %p IST').lstrip('0')
    footer_time = merged_dt.strftime('%b %d, %Y at %I:%M %p')

    # Base fields that are always shown
    fields = [
        {
            "name": "📁 Project",
            "value": f"`{project}`",
            "inline": True
        }
    ]

    # Add branch field only if it's not main
    if show_branch:
        fields.append({
            "name": "🌿 Branch Flow",
            "value": f"`{branch}` → `main`",
            "inline": True
        })

    # Add remaining fields
    fields.extend([
        {
            "name": "🔗 Commit",
            "value": f"[`{commit_id}`]({commit_url})",
            "inline": True
        },
        {
            "name": "📝 Details",
            "value": '\n'.join([f"- {line}" for line in message_lines]),
            "inline": False
        },
        {
            "name": f"**Merged at {merged_time_str}**",
            "value": "\u200b",
            "inline": False
        }
    ])

    embed = {
        "author": {
            "name": author
        },
        "title": "<:new:112233445566778899> New Changes",  # Replace with your custom emoji if needed
        "description": "Successfully merged into main",
        "color": 0x2ecc71,  # Green
        "fields": fields,
        "footer": {
            "text": f"Vibe City 2.0 • {footer_time}"
        },
        "timestamp": merged_time
    }
    return embed

@app.route('/webhook', methods=['POST'])
def webhook():
    print("Webhook endpoint hit!")  # Debug
    if request.method == 'POST':
        payload_body = request.get_data()
        signature_header = request.headers.get('X-Hub-Signature')
        print("Signature header:", signature_header)  # Debug

        if not verify_github_signature(payload_body, signature_header):
            print("Signature verification failed!")  # Debug
            return jsonify({"status": "error", "message": "Invalid signature"}), 401

        payload = request.json
        print("Payload received:", payload)  # Debug

        if 'commits' in payload and payload['commits']:
            embeds = [build_discord_embed(payload, commit) for commit in payload['commits']]
            discord_payload = {
                "username": "Vibe City Commits",
                "embeds": embeds
            }
            print("Sending to Discord:", discord_payload)  # Debug
            response = requests.post(
                DISCORD_WEBHOOK_URL,
                json=discord_payload
            )
            print("Discord response:", response.status_code, response.text)  # Debug
            if response.status_code in (200, 204):
                return jsonify({"status": "success"}), 200
            else:
                return jsonify({"status": "error", "message": "Failed to send to Discord"}), 500
        print("No commits in payload or not a push event")  # Debug
        return jsonify({"status": "ignored", "message": "Not a push event"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 