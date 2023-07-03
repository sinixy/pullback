from aiologger import Logger
from aiologger.levels import LogLevel
from aiologger.handlers.files import AsyncFileHandler
from aiologger.formatters.base import Formatter

import logging


logger = Logger(name='PULLBACK', level=LogLevel.INFO)
handler = AsyncFileHandler(filename='logs.txt')
handler.formatter = Formatter('[%(levelname)s] [%(name)s] %(asctime)s :: %(message)s', '%Y-%m-%d_%H:%M:%S')
logger.add_handler(handler)

logging.basicConfig(
    filename='logs.txt',
    level=logging.INFO,
    format='[%(levelname)s] [%(name)s] %(asctime)s :: %(message)s',
    datefmt='%Y-%m-%d_%H:%M:%S'
)
applogger = logging.getLogger('APPLICATION')