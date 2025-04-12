import psycopg2
from config import load_config

def update_phonebook(name, new_name=None, new_phone=None):
    set_clause = []
    values = []
    
    if new_name:
        set_clause.append("name = %s")
        values.append(new_name)
    if new_phone:
        set_clause.append("phone = %s")
        values.append(new_phone)
    
    if not set_clause:
        print("No changes provided to update.")
        return
    
    set_clause_str = ", ".join(set_clause)
    values.append(name)
    
    command = f"""
        UPDATE phonebook
        SET {set_clause_str}
        WHERE name = %s;
    """
    
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(command, tuple(values))
                conn.commit()
                
                if cur.rowcount > 0:
                    print(f"Updated {name} to {new_name if new_name else name} with phone {new_phone if new_phone else 'unchanged'}")
                else:
                    print(f"No user found with name {name}")
    except Exception as e:
        print(e)

if __name__ == '__main__':
    name_to_update = input("Enter the name of the user you want to update: ")
    new_name = input("Enter new name ")
    new_phone = input("Enter new phone ")
    
    update_phonebook(name_to_update, new_name, new_phone)
