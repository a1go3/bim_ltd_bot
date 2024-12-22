import os

from dotenv import load_dotenv

load_dotenv()


class Config(object):
    """Настройки для flask."""

    SECRET_KEY = os.getenv("SECRET_KEY")
