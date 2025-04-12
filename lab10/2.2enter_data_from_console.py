import psycopg2
from config import load_config

def insert_into_phonebook(name, phone):
    command = """
        INSERT INTO phonebook (name, phone)
        VALUES (%s, %s);
    """
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(command, (name, phone))
                conn.commit()
    except Exception as e:
        print(e)

if __name__ == '__main__':
    while True:
        name = input("Enter name:")
        if name.lower() == 'exit':
            break
        phone = input("Enter phone: ")
        insert_into_phonebook(name, phone)
        print(f"Added {name} with phone {phone} to the PhoneBook.")
