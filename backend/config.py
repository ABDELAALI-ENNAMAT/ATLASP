import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'atlas-audit-dev-key-change-this')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

    BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR    = os.path.join(BASE_DIR, 'data', 'demo')
    OUTPUTS_DIR = os.path.join(BASE_DIR, 'outputs')

    os.makedirs(DATA_DIR,    exist_ok=True)
    os.makedirs(OUTPUTS_DIR, exist_ok=True)

    if SECRET_KEY == 'atlas-audit-dev-key-change-this':
        logger.warning(
            "FLASK_SECRET_KEY is not set in environment. "
            "Do not use the default key in production."
        )
