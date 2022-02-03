import sqlite3

def db_init():
    connection = sqlite3.connect('db/database.db')


    with open('db/schema.sql') as f:
        connection.executescript(f.read())

    cur = connection.cursor()

    cur.execute("INSERT INTO users (name_login, password_login, last_address) VALUES (?, ?, ?)",
                ('David', '123', "login")
                )
    
    cur.execute("INSERT INTO users (name_login, password_login, last_address) VALUES (?, ?, ?)",
                ('Nik', '123', "login")
                )
    
    cur.execute("INSERT INTO rooms (administrator_name_login, room_name, private_state, activation_state) VALUES (?, ?, ?, ?)",
                ('David', 'first_room', 'private', '-')
                )
    
    cur.execute("INSERT INTO rooms (administrator_name_login, room_name, private_state, activation_state) VALUES (?, ?, ?, ?)",
                ('Nik', 'second_room', 'free', '-')
                )
    
    cur.execute("INSERT INTO routing_users_to_rooms (users_names, rooms_names, user_role_now, last_presence, max_delay, last_delay) VALUES (?, ?, ?, ?, ?, ?)",
                ('David', 'first_room', "admin", "-","-","-")
                )
    
    cur.execute("INSERT INTO routing_users_to_rooms (users_names, rooms_names, user_role_now, last_presence, max_delay, last_delay) VALUES (?, ?, ?, ?, ?, ?)",
                ('Nik', 'first_room', "listener", "-","-","-")
                )
    
    cur.execute("INSERT INTO routing_users_to_rooms (users_names, rooms_names, user_role_now, last_presence, max_delay, last_delay) VALUES (?, ?, ?, ?, ?, ?)",
                ('David', 'second_room', "listener", "-","-","-")
                )

    cur.execute("INSERT INTO routing_users_to_rooms (users_names, rooms_names, user_role_now, last_presence, max_delay, last_delay) VALUES (?, ?, ?, ?, ?, ?)",
                ('David', 'third_room', "listener", "-","-","-")
                )
    
    cur.execute("INSERT INTO routing_users_to_rooms (users_names, rooms_names, user_role_now, last_presence, max_delay, last_delay) VALUES (?, ?, ?, ?, ?, ?)",
                ('Nik', 'second_room', "admin", "-","-","-")
                )


    connection.commit()
    connection.close()