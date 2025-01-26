import psycopg2

# Подключение к базе данных
def connect_to_db():
    conn = psycopg2.connect(database="clients_db", user="postgres", password="postgres", host="localhost")
    return conn

# Функция для создания таблиц
def create_db(conn):
    with conn.cursor() as cursor:
        cursor.execute("CREATE TABLE IF NOT EXISTS clients (id SERIAL PRIMARY KEY, first_name VARCHAR(50), last_name VARCHAR(50), email VARCHAR(100), phone VARCHAR(50))")
        cursor.execute("CREATE TABLE IF NOT EXISTS client_phones (client_id INTEGER, phone VARCHAR(50))")
        conn.commit()

# Функция для добавления нового клиента
def add_client(conn, first_name, last_name, email, phones):
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO clients (first_name, last_name, email) VALUES (%s, %s, %s) RETURNING id", (first_name, last_name, email))
        client_id = cursor.fetchone()[0]
        if phones:
            cursor.executemany("INSERT INTO client_phones (client_id, phone) VALUES (%s, %s)", [(client_id, phone) for phone in phones])
        conn.commit()
        return client_id

# Функция для добавления телефона для существующего клиента
def add_phone(conn, client_id, phone):
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO client_phones (client_id, phone) VALUES (%s, %s)", (client_id, phone))
        conn.commit()

# Функция для изменения данных о клиенте
def change_client(conn, client_id, first_name=None, last_name=None, email=None, phones=None):
    with conn.cursor() as cursor:
        if first_name or last_name or email:
            cursor.execute("UPDATE clients SET first_name=%s, last_name=%s, email=%s WHERE id=%s", (first_name, last_name, email, client_id))
        if phones:
            cursor.executemany("DELETE FROM client_phones WHERE client_id=%s", [(client_id,)])
            cursor.executemany("INSERT INTO client_phones (client_id, phone) VALUES (%s, %s)", [(client_id, phone) for phone in phones])
        conn.commit()

# Функция для удаления телефона у существующего клиента
def delete_phone(conn, client_id, phone):
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM client_phones WHERE client_id=%s AND phone=%s", (client_id, phone))
        conn.commit()

# Функция для удаления существующего клиента
def delete_client(conn, client_id):
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM clients WHERE id=%s", (client_id, ))
        conn.commit()

# Функция для поиска клиента по его данным (имени, фамилии, email или телефону)
def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    with conn.cursor() as cursor:
        if first_name and last_name:
            cursor.execute("SELECT * FROM clients WHERE first_name=%s AND last_name=%s", (first_name, last_name))
        elif email:
            cursor.execute("SELECT * FROM clients WHERE email=%s", (email, ))
        elif phone:
            cursor.execute("SELECT * FROM clients WHERE EXISTS (SELECT 1 FROM client_phones WHERE client_id = clients.id AND phone = %s)", (phone, ))
        else:
            cursor.execute("SELECT * FROM clients")
        clients = cursor.fetchall()
    return clients



# Функция для получения всех номеров телефонов клиента
def get_client_phones(conn, client_id):
    with conn.cursor() as cursor:
        cursor.execute("SELECT phone FROM client_phones WHERE client_id=%s", (client_id, ))
        phones = cursor.fetchall()
    return [phone[0] for phone in phones if phone]

# Функция для вывода всех существующих клиентов
def list_clients(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM clients")
        clients = cur.fetchall()
        for client in clients:
            print(f"ID: {client[0]}\nИмя: {client[1]}\nФамилия: {client[2]}\nEmail: {client[3]}\nТелефоны: {get_client_phones(conn,client[0])}\n")
    conn.commit()

# Функция для удаления всех клиентов и всех номеров телефонов
def clear_database(conn):
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM clients")
        conn.commit()
        cursor.execute("DELETE FROM client_phones")
        conn.commit()

# Основная функция для демонстрации работы всех функций
def main():
    conn = connect_to_db()
    create_db(conn)

    # Добавление нового клиента
    client_id = add_client(conn, "Anton", "Mlad", "anton@example.com", ["1234567890", "9876543210"])

    # Добавление телефона для существующего клиента
    add_phone(conn, client_id, "1234567890")

    # Изменение данных о клиенте
    change_client(conn, client_id, first_name="Tony", last_name="Stark", email="stark@example.com")

    # Добавление второго телефона для существующего клиента
    add_phone(conn, client_id, "0987654321")

    # Поиск клиента по его данным
    clients = find_client(conn, first_name="Anton", last_name="Mlad", email="anton@example.com")
    for client in clients:
        print(client)

    # Вывести всех клиентов существующих в базе
    list_clients(connect_to_db())

    # Удаление телефона у существующего клиента
    delete_phone(conn, client_id, "1234567890")

    # Удаление существующего клиента
    delete_client(conn, client_id)

    # Закрытие соединения с базой данных
    conn.close()

main()
#
clear_database(connect_to_db())
