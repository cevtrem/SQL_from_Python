import psycopg2

with psycopg2.connect(database="clients_db", user="postgres", password="password") as conn:
    with conn.cursor() as cursor:

        # Функция для создания таблиц
        def create_db():
            cursor.execute("CREATE TABLE IF NOT EXISTS clients (id SERIAL PRIMARY KEY, first_name VARCHAR(50), last_name VARCHAR(50), email VARCHAR(100), phone VARCHAR(50))")
            cursor.execute("CREATE TABLE IF NOT EXISTS client_phones (client_id INTEGER, phone VARCHAR(50))")

        # Функция для добавления нового клиента
        def add_client(first_name, last_name, email, phones):
            cursor.execute("INSERT INTO clients (first_name, last_name, email) VALUES (%s, %s, %s) RETURNING id", (first_name, last_name, email))
            client_id = cursor.fetchone()[0]
            if phones:
                cursor.executemany("INSERT INTO client_phones (client_id, phone) VALUES (%s, %s)", [(client_id, phone) for phone in phones])
            return client_id

        # Функция для добавления телефона для существующего клиента
        def add_phone(client_id, phone):
            cursor.execute("INSERT INTO client_phones (client_id, phone) VALUES (%s, %s)", (client_id, phone))

        # Функция для изменения данных о клиенте
        def change_client(client_id, first_name=None, last_name=None, email=None, phone=None):
            if first_name:
                cursor.execute("UPDATE clients SET first_name=%s WHERE id=%s", (first_name, client_id))
            if last_name:
                cursor.execute("UPDATE clients SET last_name=%s WHERE id=%s", (last_name, client_id))
            if email:
                cursor.execute("UPDATE clients SET email=%s WHERE id=%s", (email, client_id))
            if phone:
                cursor.execute("DELETE FROM client_phones WHERE client_id=%s", (client_id,))
                cursor.execute("INSERT INTO client_phones (client_id, phone) VALUES (%s, %s)", (client_id, phone))
            else:
                cursor.execute("SELECT * FROM clients")
            return

        # Функция для удаления телефона у существующего клиента
        def delete_phone(client_id, phone):
            cursor.execute("DELETE FROM client_phones WHERE client_id=%s AND phone=%s", (client_id, phone))

        # Функция для удаления существующего клиента
        def delete_client(client_id):
            cursor.execute("DELETE FROM client_phones WHERE client_id=%s", (client_id,))
            cursor.execute("DELETE FROM clients WHERE id=%s", (client_id, ))

        # Функция для поиска клиента по его данным (имени, фамилии, email или телефону)
        def find_client(first_name=None, last_name=None, email=None, phone=None):
            if first_name:
                cursor.execute("SELECT * FROM clients WHERE first_name=%s", (first_name,))
            elif last_name:
                cursor.execute("SELECT * FROM clients WHERE last_name=%s", (last_name,))
            elif email:
                cursor.execute("SELECT * FROM clients WHERE email=%s", (email, ))
            elif phone:
                cursor.execute("SELECT * FROM clients WHERE EXISTS (SELECT 1 FROM client_phones WHERE client_id = clients.id AND phone = %s)", (phone, ))
            else:
                cursor.execute("SELECT * FROM clients")
            clients = cursor.fetchall()
            return clients

        # Функция для получения всех номеров телефонов клиента
        def get_client_phones(client_id):
            cursor.execute("SELECT phone FROM client_phones WHERE client_id=%s", (client_id, ))
            phones = cursor.fetchall()
            return ([phone[0] for phone in phones if phone])

        # Функция для вывода всех существующих клиентов
        def list_clients():
            cursor.execute("SELECT * FROM clients")
            clients = cursor.fetchall()
            for client in clients:
                print(f"ID: {client[0]}\nИмя: {client[1]}\nФамилия: {client[2]}\nEmail: {client[3]}\nТелефоны: {get_client_phones(client[0])}\n")

        # Функция для удаления всех клиентов и всех номеров телефонов
        def clear_database():
            cursor.execute("DELETE FROM clients")
            cursor.execute("DELETE FROM client_phones")


# Основная функция для демонстрации работы всех функций
        def main():

            # Добавление нового клиента
            add_client("Вася", "Васечкин", "vasya@example.com", ['222222222'])
            add_client("Иван", "Иванов", "ivan@example.com", ['3333333333'])
            client_id = add_client("Anton", "Mlad", "anton@example.com", ["111111"])

            # Добавление телефона для существующего клиента
            add_phone(client_id, "111122")

            # Поиск клиента по его данным
            # print(find_client(first_name="Anton", last_name="Mlad"))
            # print(find_client(phone='222222222'))


            # Изменение данных о клиенте
            change_client(client_id, first_name="Tony")
            change_client(client_id, last_name="Stark", email="stark@example.com")

            # Вывести всех клиентов существующих в базе
            list_clients()

            # Удаление телефона у существующего клиента
            delete_phone(client_id, "111122")

            # Удаление существующего клиента
            # delete_client(client_id)

        # Запуск демострации
        main()

        # Удаление всех данных из таблиц клиенты и телефоны
        # clear_database()

# Закрытие соединения с базой данных
conn.close()

