from environs import Env

env = Env()
env.read_env()

TG_BOT_TOKEN = env.str("TG_BOT_TOKEN")
YOOKASSA_SHOP_ID = env.str("YOOKASSA_SHOP_ID", "")
YOOKASSA_SECRET_KEY = env.str("YOOKASSA_SECRET_KEY", "")
