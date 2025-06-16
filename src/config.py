from pathlib import Path
from dotenv import load_dotenv
from os import environ


load_dotenv()
BASE_DIR = Path(__file__).parent.parent
message = 'define me!'

# DATABASE
DB_HOST: str = environ.get("DB_HOST", message)
DB_PORT: str = environ.get("DB_PORT", message)
DB_NAME: str = environ.get("DB_NAME", message)
DB_USER: str = environ.get("DB_USER", message)
DB_PASS: str = environ.get("DB_PASS", message)

# REDIS
REDIS_HOST: str = environ.get("REDIS_HOST", message)
REDIS_PORT: int = environ.get("REDIS_PORT", message)

# RabbitMQ
RabbitMQ_USERNAME: str = environ.get("RabbitMQ_USERNAME")
RabbitMQ_PASSWORD: str = environ.get("RabbitMQ_PASSWORD")
RabbitMQ_HOST: str = environ.get("RabbitMQ_HOST", message)
RabbitMQ_PORT: int = environ.get("RabbitMQ_PORT", message)
RabbitMQ_VHOST: str = environ.get("RabbitMQ_VHOST", message)

# TELEGRAM
TOKEN_BOT: str = environ.get("TOKEN_BOT", message)
TELEGRAM_BOT_HOST: str = environ.get("TELEGRAM_BOT_HOST", message)
TELEGRAM_BOT_PORT: int = int(environ.get("TELEGRAM_BOT_PORT", message))
WEBHOOK_PATH: str = environ.get("WEBHOOK_PATH", message)
NGROK_API_KEY: str = environ.get("NGROK_API_KEY", message)
TELEGRAM_ADMIN_IDS = list(map(int, environ.get("ADMIN_IDS", message).split(",")))

LOG_DIRECTORY: str = "logs/"
