import logging

from servoskull import settings

_formatter = logging.Formatter('%(name)s %(asctime)s %(levelname)s: %(message)s')

_handler = logging.StreamHandler()
_handler.setFormatter(_formatter)

logger = logging.getLogger(__name__)
logger.addHandler(_handler)
logger.setLevel(getattr(logging, settings.LOGGING_LEVEL.upper()))
