import sqlite3


def sql_connect_musics_db():
    global base, cur
    base = sqlite3.connect('data_base/musics.db')
    if base:
        print('musics connected')
    cur = base.cursor()
    create_tables()


def create_tables():
    with open('data_base/create_music_table.sql', 'r') as sql_commands:
        sql_script = sql_commands.read()
    base.executescript(sql_script)
    base.commit()
    print('Таблицы музыки созданы')



def register_music_user(user_id, vk_id):
    cur.execute('INSERT OR IGNORE INTO music_user(user_id, vk_id, current_music)'
                ' VALUES (?,?,?)', (user_id, vk_id, 0, ))
    base.commit()


def get_vk_id_music_user(user_id):
    row = cur.execute('SELECT vk_id FROM music_user WHERE user_id == ?', (user_id, )).fetchone()
    return row


def check_music_user(user_id):
    if cur.execute('SELECT * FROM music_user WHERE user_id == ?', (user_id, )).fetchone():
        return True
    else: return False


def pre_music_making(pre_musics_items_list):
    cur.executemany('''INSERT OR IGNORE INTO pre_music VALUES(?,?,?,?,?,?,?,?)''', pre_musics_items_list)
    base.commit()


def check_pre_music(user_id):
    row = cur.execute('SELECT count(content_id) FROM pre_music WHERE user_id==?',(user_id, )).fetchone()
    return row


def cut_out_pre_music(user_id, count):
    rows = cur.execute('SELECT * FROM pre_music WHERE user_id == ? ORDER BY date_added DESC LIMIT ?',
                                        (user_id, count, )).fetchall()
    cur.execute('DELETE FROM pre_music WHERE content_id IN '
                        '(SELECT content_id FROM pre_music'
                                ' WHERE user_id == ? ORDER BY date_added DESC LIMIT ?)', (user_id, count,))
    base.commit()
    return rows

# mil - music_items_list
async def added_musics(mil):
    cur.execute('''INSERT OR IGNORE INTO musics(file_id, thumb_id, artist, title, date_added, duration)
                        VALUES(?,?,?,?,?,?)''', (mil['audio'], mil['thumb'], mil['artist'], mil['title'],
                                                 mil['date_added'], mil['duration'], ))
    cur.execute('''INSERT OR IGNORE INTO user_to_music (user_id, music_id) 
                        VALUES (
                            (SELECT id FROM music_user WHERE user_id == ?),
                            (SELECT id FROM musics WHERE file_id == ?))''', (mil['user_id'], mil['audio'], ))
    base.commit()



def get_musics(user_id, limit, offset):
    rows = cur.execute('''SELECT file_id, thumb_id, artist, title, duration 
                            FROM musics
                            	INNER JOIN user_to_music ON musics.id == user_to_music.music_id
                            	INNER JOIN music_user ON user_to_music.user_id == music_user.id
                            WHERE music_user.user_id == ?
                            ORDER BY musics.date_added DESC
                            LIMIT ? 
                            OFFSET ?''', (user_id, limit, offset, )).fetchall()
    base.commit()
    return rows


def set_music_offset(user_id):
    cur.execute('UPDATE music_user SET current_music ='
                '            (SELECT current_music + 10 FROM music_user WHERE user_id == ?)', (user_id,))


def get_music_offset(user_id):
    offset = cur.execute('SELECT current_music FROM music_user WHERE user_id == ?', (user_id, )).fetchone()
    return offset


def reset_music_offset(user_id):
    cur.execute('UPDATE music_user SET current_music = 0 WHERE user_id == ?)', (user_id,))

def get_count_music(user_id):
    row = cur.execute('''SELECT count(musics.id) FROM musics
                            INNER JOIN user_to_music ON musics.id == user_to_music.music_id
                            INNER JOIN music_user ON user_to_music.user_id == music_user.id
                        WHERE music_user.user_id == ?''', (user_id, )).fetchone()
    return row


def get_last_music_date(user_id):
    row = cur.execute('''SELECT date_added FROM musics
                            INNER JOIN user_to_music ON musics.id == user_to_music.music_id
                            INNER JOIN music_user ON user_to_music.user_id == music_user.id
                            WHERE music_user.user_id == ?
                            ORDER BY date_added DESC
                            LIMIT 1''', (user_id, )).fetchone()
    return row


