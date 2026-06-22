import discord
from discord.ext import commands, tasks
import requests
import socket
import os
import json
from flask import Flask

# Flask app setup
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot server is running!"

# Discord bot token
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# API URL
API_URL = 'http://api.subhxcosmo.in/api'

# Port set karna (default 5000)
PORT = int(os.getenv('PORT', 5000))  # Environment variable se port le, nahi to 5000

# Function to get local IP address
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

# Construct URL
LOCAL_IP = get_local_ip()
KEEP_ALIVE_URL = f'http://{LOCAL_IP}:{PORT}'

# Intents setup
intents = discord.Intents.default()
intents.message_content = True

# Bot initialization
bot = commands.Bot(command_prefix='/', intents=intents)

# /num command
@bot.command(name='num')
async def fetch_api(ctx, *, term):
    await ctx.send(f"Processing request for: {term}")
    try:
        # API request
        params = {
            'key': 'toxic',
            'type': 'mobile',
            'term': term
        }
        response = requests.get(API_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            # Pretty print JSON data
            formatted_data = json.dumps(data, indent=2)
            # Limit message length to avoid exceeding Discord limit
            if len(formatted_data) > 1900:
                await ctx.send("Data too long to display.")
            else:
                await ctx.send(f"Result:\n```json\n{formatted_data}\n```")
        else:
            await ctx.send(f"Failed to get data from API. Status code: {response.status_code}")
    except Exception as e:
        await ctx.send(f"Error occurred: {str(e)}")

# Keep-alive task
@tasks.loop(minutes=5)
async def keep_alive():
    try:
        res = requests.get(KEEP_ALIVE_URL)
        if res.status_code == 200:
            print("Keep-alive ping sent successfully.")
        else:
            print(f"Keep-alive ping failed with status code: {res.status_code}")
    except Exception as e:
        print(f"Error in keep-alive: {str(e)}")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    keep_alive.start()

# Run Flask app in a separate thread
if __name__ == '__main__':
    import threading
    def run_flask():
        app.run(host='0.0.0.0', port=PORT)
    
    threading.Thread(target=run_flask).start()
    # Run bot
    if TOKEN:
        try:
            bot.run(TOKEN)
        except Exception as e:
            print(f"Error starting bot: {str(e)}")
    else:
        print("Error: DISCORD_BOT_TOKEN environment variable not set.")
