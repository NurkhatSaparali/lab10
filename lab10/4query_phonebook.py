import psycopg2
from config import load_config

def query_phonebook(name=None, phone=None):
    config = load_config()
    sql = "SELECT * FROM phonebook WHERE 1=1"
    params = []

    if name:
        sql += " AND name = %s"
        params.append(name)
    
    if phone:
        sql += " AND phone = %s"
        params.append(phone)

    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, tuple(params))
                rows = cur.fetchall()
                if rows:
                    for row in rows:
                        print(row)
                else:
                    print("No records found")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    name = input("Enter name to search: ")
    phone = input("Enter phone to search : ")

    if phone:
        query_phonebook(name=name, phone=phone)
    else:
        query_phonebook(name=name)
