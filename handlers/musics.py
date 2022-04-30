from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile, InputMediaAudio, InputMediaPhoto
from aiogram.dispatcher.filters import Text
import config
from data_base import musics_db
from utils import vk_music
import os


async def start_info(message: types.Message):
    instructions_img = [InputMediaPhoto(media=x) for x in vk_music.get_instructions()]
    await message.answer_media_group(instructions_img)
    await message.answer('Привет, это небольшая информация о том как надо делать,'
                         '1: Жмем по кнопке OAuth и переходим на страничку авторизации вк,'
                         ' просить у тебя должны только информацию страницы и аудиозаписи, все,'
                         ' если вдруг что то кого-то просят еще, ни за что не разрешай\n'
                         '2: После того как разрешили доступ, переходим на страничку где нам выдали токен, '
                         'он находится в самом адресе этой странички, нужно получить его, жмем на кнопку поделиться\n '
                         '3: Ну, копируем\n'
                         '4: Отправляем боту, этот токен нужен что бы делать запросы в вк и получать список твоей музыки,'
                         'приятного пользования')
    await musics(message)


async def musics(message: types.Message):
    if vk_music.check_pre_music(message.from_user.id):
        await message.answer('Нужно заного получить токен')
    else:
        await message.answer('Приветствую, я вам помогу получить доступ к вашей музыке вк,'
                              ' внизу будет кнопка-ссылка для получения ключа доступа к вашим аудио-записям,'
                              'пройдя по ней и разрешив доступ откроется следущая страница,'
                              ' скопируйте ее адресс и отправьте мне, не переживайте,'
                              ' эти данные будут использованы один раз для запроса списка вашей музыки '
                              'и нигде не будут храниться')
    await message.answer('Вот', reply_markup=InlineKeyboardMarkup().
                             add(InlineKeyboardButton(text='OAuth', url=config.OAuth_url)))


async def build_musics_list(message: types.Message):
    vk_music.get_musics_list(message)
    await message.answer('Список вашей музыки с вк был добавлен бота,'
                         ' используйте /listen что бы загружать ее сюда и получать от бота')


async def set_access(message: types.Message):
    if not vk_music.check_access(message.from_user.id):
        user_id = message.from_user.id
        vk_id = message.text.split('user_id=')[1]
        vk_music.set_access(message.text, user_id, vk_id)
        if not vk_music.check_pre_music(user_id):
            await build_musics_list(message)
        else:
            await message.answer('Токен установлен, теперь вы снова можете загружать музыку')
        await message.delete()



async def music_load(message: types.Message):
    print(message.text)
    if not vk_music.check_access(message.from_user.id):
        await musics(message)
    else:
        mus_input = InputFile('static/music.mp3')
        thumb_input = InputFile('static/thumb.jpg')
        msg = await message.answer_audio(audio=mus_input, thumb=thumb_input, performer='GachiSound',
                                   title='three hundred bucks', duration=3)

        finished_counter = 1
        if len(message.text) > 5:
            all_count = message.text.split(' ')[1]
        else:
            all_count = 20
        for item in vk_music.music_loader(message.from_user.id, all_count):
            audio = InputMediaAudio(media=item['audio'], performer=item['artist'],
                                    title=item['title'], duration=item['duration'],
                                    thumb=item['thumb'], caption=f'{finished_counter} из {all_count} готов')
            msg = await msg.edit_media(media=audio)
            item['audio'] = msg.audio.file_id
            item['thumb'] = msg.audio.thumb.file_id
            item['user_id'] = message.from_user.id
            await musics_db.added_musics(item)
            finished_counter += 1

        await message.answer(text='Ну вот и все готово')


async def play_music(message: types.Message):
    playlist = vk_music.get_music_for_play(message)
    if playlist:
        music_list = [InputMediaAudio(media=x[0], thumb=x[1], performer=x[2], title=x[3],  duration=x[4])
                      for x in playlist]
        await message.answer_media_group(media=music_list)
    else:
        message.text = '/load'
        await message.answer('Музыка кончилась блять, качаем еще')
        await music_load(message)


async def play_all_music(message: types.Message):
    playlist = vk_music.get_all_music_for_play(message)
    for i in range(0, len(playlist), 10):
        music_list = [InputMediaAudio(media=x[0], performer=x[1], title=x[2], thumb=x[3], duration=x[4])
                      for x in playlist[i:i + 10]]
        await message.answer_media_group(media=music_list)


async def update_music(message):
    if not vk_music.check_access(message.from_user.id):
        await musics(message)
    else:
        count_new_music = vk_music.get_update_music_list(message)
        message.text = f'/load {count_new_music}'
        await music_load(message)



def register_handlers_musics(dp: Dispatcher):
    dp.register_message_handler(start_info, commands=['start', 'info'])
    dp.register_message_handler(musics, commands=['music_start'])
    dp.register_message_handler(set_access, Text(startswith='https://oauth.vk.com/blank.html#access_token'))
    dp.register_message_handler(play_music, commands=['listen'])
    dp.register_message_handler(music_load, commands=['load'])
    dp.register_message_handler(play_all_music, commands=['all_music'])
    dp.register_message_handler(update_music, commands=['update'])

