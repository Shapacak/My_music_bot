from aiogram import Bot, Dispatcher
import sys, config


bot_token = config.BOT_TOKEN
if not bot_token:
    sys.exit('Нету токена')

bot = Bot(token=bot_token)
dp = Dispatcher(bot)