import psycopg2
from config import load_config

def delete_user(name=None, phone=None):
    config = load_config()
    if not name and not phone:
        print("No name or phone provided for deletion")
        return
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                if name and phone:
                    cur.execute("DELETE FROM phonebook WHERE name = %s AND phone = %s", (name, phone))
                elif name:
                    cur.execute("DELETE FROM phonebook WHERE name = %s", (name,))
                elif phone:
                    cur.execute("DELETE FROM phonebook WHERE phone = %s", (phone,))
                conn.commit()
                print(f"Deleted {cur.rowcount} row(s)")
    except Exception as e:
        print(e)

if __name__ == '__main__':
    name = input("Enter name to delete: ").strip()
    phone = input("Enter phone to delete: ").strip()
    delete_user(name if name else None, phone if phone else None)
