import os
import sys
import signal
import asyncio
from typing import Optional

from aiohttp import web

from bot.bot import ProfessorOakBot
from config.config import config
from bot.utils.logger import get_logger, configure_logger


class BotApplication:
    """
    Manages the complete application lifecycle,
    including Discord bot and web server with graceful shutdown.
    """

    def __init__(self, discord_token: str, base_path: str, web_port: int = 8080):
        """
        Initialize the bot application.

        Args:
            discord_token (str): Discord bot token
            base_path (str): Base path for bot resources
            web_port (int, optional): Port for web server. Defaults to 8080.
        """
        self.logger = get_logger(__name__)

        # Application components
        self.discord_token = discord_token
        self.base_path = base_path
        self.web_port = web_port

        # Asyncio components
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.bot: Optional[ProfessorOakBot] = None
        self.web_app: Optional[web.Application] = None
        self.web_runner: Optional[web.AppRunner] = None

        # Shutdown management
        self.shutdown_event = asyncio.Event()

    def _setup_signal_handlers(self):
        """
        Set up signal handlers for graceful shutdown.
        """
        try:
            # Unix-like systems
            self.loop.add_signal_handler(signal.SIGINT, self._request_shutdown)
            self.loop.add_signal_handler(signal.SIGTERM, self._request_shutdown)
        except NotImplementedError:
            # Windows fallback
            for sig in (signal.SIGINT, signal.SIGTERM):
                self.loop.add_signal_handler(sig, self._request_shutdown)

    def _request_shutdown(self):
        """
        Request graceful shutdown of the application.
        """
        self.logger.info("Shutdown signal received. Initiating graceful shutdown...")
        self.shutdown_event.set()

    async def _create_web_server(self):
        """
        Create a web server for health checks and monitoring.

        Returns:
            web.AppRunner: Configured web application runner
        """
        self.web_app = web.Application()

        # Health check endpoint for Render
        async def health_check(request):
            return web.Response(text="OK", status=200, content_type="text/plain")

        self.web_app.add_routes(
            [web.get("/", health_check), web.get("/health", health_check)]
        )

        runner = web.AppRunner(self.web_app)
        await runner.setup()

        site = web.TCPSite(
            runner, "0.0.0.0", int(os.environ.get("PORT", self.web_port))
        )
        await site.start()

        self.logger.info(f"Web server started on port {site._port}")
        return runner

    async def _start_bot(self):
        """
        Initialize and start the Discord bot.
        """
        self.bot = ProfessorOakBot(self.base_path)
        await self.bot.start(self.discord_token)

    async def run(self):
        """
        Run the complete application with graceful shutdown support.
        """
        try:
            # Configure event loop
            self.loop = asyncio.get_running_loop()
            self._setup_signal_handlers()

            # Start web server for health checks
            self.web_runner = await self._create_web_server()

            # Start Discord bot in the background
            bot_task = asyncio.create_task(self._start_bot())

            # Wait for shutdown signal
            await self.shutdown_event.wait()

        except Exception as e:
            self.logger.error(f"Application startup error: {e}")
            sys.exit(1)

        finally:
            # Graceful shutdown sequence
            await self._shutdown()

    async def _shutdown(self):
        """
        Perform a coordinated shutdown of all application components.
        """
        self.logger.info("Performing graceful shutdown...")

        # Close web server
        if self.web_runner:
            await self.web_runner.cleanup()
            self.logger.info("Web server shut down.")

        # Close Discord bot
        if self.bot and not self.bot.is_closed():
            await self.bot.close()
            self.logger.info("Discord bot connection closed.")

        # Cancel any remaining tasks
        for task in asyncio.all_tasks(self.loop):
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        self.logger.info("Application shutdown complete.")


def main():
    """
    Entry point for the Discord bot application.
    Handles configuration and application startup.
    """
    # Configure logging
    configure_logger()
    logger = get_logger(__name__)

    # Validate Discord token
    discord_token = config.DISCORD_TOKEN
    if not discord_token:
        logger.error("Discord token not found. Cannot start bot.")
        sys.exit(1)

    # Determine base path
    base_path = os.path.dirname(os.path.abspath(__file__))

    # Create and run bot application
    try:
        bot_app = BotApplication(discord_token, base_path)
        asyncio.run(bot_app.run())

    except Exception as e:
        logger.critical(f"Fatal application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
