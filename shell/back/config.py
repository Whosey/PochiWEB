# back/config.py
from pathlib import Path
import os

from dotenv import load_dotenv

# .env 放在 PochiWEB/shell/.env
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_PATH)


class Settings:
    # --- SiliconFlow / Qwen3-VL ---
    SILICONFLOW_API_KEY: str = os.getenv("SILICONFLOW_API_KEY", "")
    IMAGE2TEXT_API_URL: str = os.getenv("IMAGE2TEXT_API_URL", "")
    IMG2TEXT_MODEL: str = os.getenv("IMG2TEXT_MODEL", "")

    # --- GLM4V（目前没用到，但先保留） ---
    GLM_API_KEY: str = os.getenv("GLM_API_KEY", "")
    GLM_API_URL: str = os.getenv("GLM_API_URL", "")
    GLM_MODEL: str = os.getenv("GLM_MODEL", "")

    # --- Stability SD3.5 文生图 ---
    STABILITY_API_KEY: str = os.getenv("STABILITY_API_KEY", "")
    STABILITY_API_URL: str = os.getenv("STABILITY_API_URL", "")
    STABILITY_MODEL: str = os.getenv("STABILITY_MODEL", "")

    # --- 佳博打印机（如果 .env 里没写，就先是空字符串） ---
    POS_API_KEY: str = os.getenv("POS_API_KEY", "")
    POS_MEMBER_CODE: str = os.getenv("POS_MEMBER_CODE", "")
    POS_DEVICE_ID: str = os.getenv("POS_DEVICE_ID", "")


settings = Settings()
