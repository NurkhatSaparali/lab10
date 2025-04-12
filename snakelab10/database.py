import psycopg2
from config import load_config

def create_tables():
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id SERIAL PRIMARY KEY,
                        username VARCHAR(100) UNIQUE NOT NULL
                    );
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS user_score (
                        score_id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
                        score INTEGER NOT NULL,
                        level INTEGER NOT NULL
                    );
                """)
                conn.commit()
                print("Tables created successfully.")
    except Exception as e:
        print("Error creating tables:", e)

def get_user_id(username):
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT user_id FROM users WHERE username = %s", (username,))
                result = cur.fetchone()
                return result[0] if result else None
    except Exception as e:
        print("Error retrieving user_id:", e)
        return None

def create_user(username):
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO users (username) VALUES (%s) RETURNING user_id", (username,))
                user_id = cur.fetchone()[0]
                conn.commit()
                return user_id
    except Exception as e:
        print("Error creating user:", e)
        return None

def get_current_level(user_id):
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                # Берем последний зафиксированный уровень для пользователя
                cur.execute("SELECT level FROM user_score WHERE user_id = %s ORDER BY score_id DESC LIMIT 1", (user_id,))
                result = cur.fetchone()
                return result[0] if result else 1
    except Exception as e:
        print("Error retrieving current level:", e)
        return 1

def save_score(user_id, score, level):
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO user_score (user_id, score, level) VALUES (%s, %s, %s)", (user_id, score, level))
                conn.commit()
                print("Score saved successfully.")
    except Exception as e:
        print("Error saving score:", e)

# Для тестового запуска функции создания таблиц:
if __name__ == '__main__':
    create_tables()