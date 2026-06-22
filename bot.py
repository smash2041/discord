import discord
from discord.ext import commands, tasks
import requests
import socket
import os

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
        # Dummy connect to get local IP
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
            await ctx.send(f"Result: {data}")
        else:
            await ctx.send("Failed to get data from external API.")
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

# Keep-alive task
@tasks.loop(minutes=5)
async def keep_alive():
    try:
        response = requests.get(KEEP_ALIVE_URL)
        print("Keep-alive ping sent to:", KEEP_ALIVE_URL)
    except Exception as e:
        print(f"Error in keep-alive: {str(e)}")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    keep_alive.start()

# Run bot
bot.run(TOKEN)
