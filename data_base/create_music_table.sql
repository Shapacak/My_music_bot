CREATE TABLE IF NOT EXISTS music_user(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            vk_id INTEGER UNIQUE,
            current_music INTEGER);

/*
Спустя пару дней я придумал оптимизацию pre_music, здесь хранить только content_id,
а все остальное раскидать по таблицам и связать по айдишникам
*/
CREATE TABLE IF NOT EXISTS pre_music(
            content_id TEXT UNIQUE,
            thumb_url TEXT,
            artist TEXT,
            title TEXT,
            date_added INTEGER,
            duration INTEGER,
            user_id INTEGER,
            vk_id INTEGER);

CREATE TABLE IF NOT EXISTS musics(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id TEXT UNIQUE,
            thumb_id TEXT,
            artist TEXT,
            title TEXT,
            date_added INTEGER,
            duration INTEGER);

CREATE TABLE IF NOT EXISTS user_to_music(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id REFERENCES music_user(id),
            music_id REFERENCES musics(id));