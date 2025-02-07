import os, threading
from watchdog.events import FileSystemEventHandler

from classes.config_manager import ConfigManager
from classes.logger import Logger

# Initialize the logger for consistent logging
logger = Logger.get_logger()

class ConfigFileChangeHandler(FileSystemEventHandler):
    """
    A file system event handler for monitoring changes to the configuration file.
    Automatically updates the bot's configuration when the configuration file is modified.
    """
    def __init__(self, bot, debounce_interval=1.0):
        """
        Initializes the file change handler with a reference to the bot instance.

        :param bot: The bot instance to be updated when the configuration file changes.
        :type bot: Bot
        :param debounce_interval: The interval to debounce the file change events, defaults to 1.0 seconds.
        :type debounce_interval: float
        """
        self.bot = bot
        self.debounce_interval = debounce_interval
        self.debounce_timer = None
        self.debounce_interval = debounce_interval
        self.debounce_timer = None

    def on_modified(self, event):
        """
        Called when a file or directory is modified.
        """
        if os.path.exists(event.src_path) and os.path.exists(ConfigManager.CONFIG_FILE) and os.path.samefile(event.src_path, ConfigManager.CONFIG_FILE):
            if self.debounce_timer is not None:
                self.debounce_timer.cancel()
            self.debounce_timer = threading.Timer(self.debounce_interval, self.reload_config, [event.src_path])
            self.debounce_timer.start()

    def reload_config(self, src_path):
        """
        Reloads the configuration file and updates the bot's configuration.
        """
        try:
            # Reload the updated configuration file
            new_config = ConfigManager.load_config()
            # Update the bot's configuration with the new settings
            self.bot.update_config(new_config)
        except Exception as e:
            # Log an error if the configuration update fails
            logger.exception(f"Failed to reload configuration from {src_path}: {e}")