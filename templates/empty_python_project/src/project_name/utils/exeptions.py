# Import Exception from the built-in module
from builtins import Exception

from project_name.utils.logger import get_logger


class ProjectNameException(Exception):
    def __init__(self, message):
        self.message = message
        self.logger = get_logger(__name__, loglevel="error")
        self.logger.error(self.message)

    def __str__(self):
        return self.message
