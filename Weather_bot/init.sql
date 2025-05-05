-- Убедимся что пользователь создан с правильными правами
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'bot_user') THEN
    CREATE USER bot_user WITH PASSWORD 'bot_password_123';
  END IF;
END $$;

GRANT ALL PRIVILEGES ON DATABASE weather_bot TO bot_user;

-- Создаем таблицу если ее нет
\c weather_bot

CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL,
  lat FLOAT NOT NULL,
  lon FLOAT NOT NULL,
  req_time TIMESTAMPTZ DEFAULT NOW(),
  cityname TEXT NOT NULL
);