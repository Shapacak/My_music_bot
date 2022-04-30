import time
import requests
from io import BytesIO
from data_base import musics_db
from aiogram.types import InputFile
import os



# Проверка наличия токена в сообщении и сохранение его в окружении по id пользователя
def set_access(text, user_id, vk_id):
    if 'access_token' in text:
        os.environ[str(user_id)] = text.split('access_token=')[1].split('&', 1)[0]
        musics_db.register_music_user(user_id, vk_id)
        return True
    else:
        return False

# Проверка на наличие токена в окружении
def check_access(user_id):
    if os.getenv(str(user_id)):
        return True
    else:
        return False


def get_instructions():
    path = 'static/music_instruction/'
    for file in os.listdir(path):
        yield InputFile(path+file)



# Получаем список всей музыки пользователя
def get_musics_list(message):
    user_id = message.from_user.id
    if check_pre_music(user_id):
        return True
    vk_id = musics_db.get_vk_id_music_user(user_id)[0]

    get_count_musics = 'https://api.vk.com/method/audio.getCount'
    params = {'access_token':os.getenv(str(user_id)),
              'owner_id':vk_id,
              'v':'5.131'}

    count = requests.get(get_count_musics, params=params).json()['response']



    step = 200

    musics_items_list = []

    for i in range(0, count, step):
        response = requests.get(f'https://api.vk.com/method/audio.get?access_token={os.getenv(str(user_id))}'
                                f'&owner_id={vk_id}&count={step}&offset={i}&v=5.131').json()

        musics_items_list.extend((x['ads']['content_id'] if 'ads' in x else f'{x["owner_id"]}_{x["id"]}',
                            x['album']['thumb']['photo_300'] if 'album' in x and 'thumb' in x['album']
                                                                else 'static/thumb.jpg',
                          x['artist'], x['title'], x['date'], x['duration'], user_id, vk_id) for x
                                 in response['response']['items'] if 'error' not in x)
        time.sleep(0.5)

    musics_db.pre_music_making(musics_items_list)


# Проверим наличие предметов в списке заготовленной для скачивания музыки
def check_pre_music(user_id):
    if musics_db.check_pre_music(user_id)[0] > 0:
        return True


# Грузим музыку, отправляем генератором ее в бота
def music_loader(user_id, count):
    music_rows = musics_db.cut_out_pre_music(user_id, count)
    audios = ','.join(x[0] for x in music_rows)

    query = f'https://api.vk.com/method/audio.getById'
    params = {'access_token': os.getenv(str(user_id)),
              'audios': audios,
              'v': '5.131'}

    music_urls_response = requests.get(query, params=params).json()
    # На этом моменте мне начинает казаться что лучше сделать полноценный аудио-класс и вертеть его туда сюда
    try:
        for i in range(len(music_rows)):
            audio = BytesIO(requests.get(music_urls_response['response'][i]['url']).content)
            if music_rows[i][1].startswith('static'):
                thumb = open('static/thumb.jpg', 'rb')
            else:
                thumb = BytesIO(requests.get(music_rows[i][1]).content)

            audio_dict = {'audio': audio, 'thumb': thumb,
                          'artist': music_rows[i][2], 'title': music_rows[i][3],
                          'date_added': music_rows[i][4], 'duration': music_rows[i][5]}
            yield audio_dict
            time.sleep(0.5)
    except IndexError:
        print(IndexError)
        print('Ну я не знаю, что то сломалось походу, мой бот меня кибербулит блять')


# Получаем по 10 песенок
def get_music_for_play(message):
    user_id = message.from_user.id
    offset = musics_db.get_music_offset(user_id)[0]
    limit = 10
    playlist = musics_db.get_musics(user_id, limit, offset)
    if playlist:
        musics_db.set_music_offset(user_id)
    return playlist


# Получаем все песни
def get_all_music_for_play(message):
    user_id = message.from_user.id
    offset = 0
    limit = musics_db.get_count_music(user_id)[0]
    playlist = musics_db.get_musics(user_id,limit,offset)
    return playlist


# Повторение кода, мне не нравится очень, но я хлебушек
def get_update_music_list(message):
    user_id = message.from_user.id
    vk_id = musics_db.get_vk_id_music_user(user_id)[0]
    last_date = musics_db.get_last_music_date(user_id)[0]
    response = requests.get(f'https://api.vk.com/method/audio.get?access_token={os.getenv(str(user_id))}'
                           f'&owner_id={vk_id}&v=5.131').json()
    musics_items_list = []
    musics_items_list.extend((x['ads']['content_id'] if 'ads' in x else f'{x["owner_id"]}_{x["id"]}',
                              x['album']['thumb']['photo_300'] if 'album' in x and 'thumb' in x['album']
                              else 'static/thumb.jpg',
                              x['artist'], x['title'], x['date'], x['duration'], user_id, vk_id) for x
                             in response['response']['items'] if 'error' not in x and x['date'] > last_date)
    print(tuple(musics_items_list))
    musics_db.pre_music_making(musics_items_list)
    musics_db.reset_music_offset(user_id)
    return len(tuple(musics_items_list))