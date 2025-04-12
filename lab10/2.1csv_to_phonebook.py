import psycopg2
import csv
from config import load_config

def load_csv_to_phonebook(csv_file):
    command = """
        INSERT INTO phonebook (name, phone)
        VALUES (%s, %s);
    """
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                with open(csv_file, 'r') as file:
                    csv_reader = csv.DictReader(file)
                    for row in csv_reader:
                        cur.execute(command, (row['username'], row['phone']))
                conn.commit()
    except Exception as e:
        print(e)

if __name__ == '__main__':
    load_csv_to_phonebook('data.csv')
