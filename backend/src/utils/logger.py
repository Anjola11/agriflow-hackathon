import logging
import sys

from logtail import LogtailHandler
from src.config import Config

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers: #prevent duplicate
    stream_handler = logging.StreamHandler(sys.stdout)
    better_stack_handler = LogtailHandler(source_token=Config.BETTER_STACK_SOURCE_TOKEN, host=Config.BETTER_STACK_INGESTING_HOST)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    stream_handler.setFormatter(formatter)
    

    logger.handlers = [stream_handler, better_stack_handler]
