import os
import asyncio
from aiohttp import web
from bot.bot import ProfessorOak
from config.config import config

# Create an aiohttp application
app = web.Application()

async def handle(request):
    return web.Response(text="Web service is running alongside the bot!")

# Add the route to the aiohttp app
app.add_routes([web.get('/', handle)])

async def run_bot(token: str, base_path: str):
    bot = ProfessorOak(base_path)
    # Use bot.start() instead of bot.run() so it works with the current event loop
    await bot.start(token)

async def start_server():
    # Start aiohttp server in an asyncio event loop
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)  # You can change the port here
    await site.start()
    print("Web service is running at http://localhost:8080")

async def main():
    # Run both the bot and the web service concurrently
    loop = asyncio.get_event_loop()
    
    # Start the aiohttp server
    server_task = loop.create_task(start_server())
    
    # Start the bot
    bot_task = loop.create_task(run_bot(config.DISCORD_TOKEN, os.path.dirname(os.path.abspath(__file__))))
    
    # Wait for both tasks to finish
    await asyncio.gather(server_task, bot_task)

if __name__ == "__main__":    
    if config.DISCORD_TOKEN is not None:
        print("Starting both web server and bot...")
        # Run everything in asyncio
        asyncio.run(main())
    else:
        print("Environment Variable that holds 'Discord Token' not found!")
