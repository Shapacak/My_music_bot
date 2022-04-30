from aiogram import executor
from create_bot import dp
from data_base import musics_db


async def on_startup(_):
    print('Бот в сети')
    musics_db.sql_connect_musics_db()


from handlers import musics


musics.register_handlers_musics(dp)


executor.start_polling(dp, skip_updates=True, on_startup=on_startup)