from datetime import datetime
from flask import Flask, request, render_template, redirect, send_from_directory, make_response, Response, json
from flask import  jsonify
import sqlite3
import hashlib
import math
from time import gmtime, strftime

from db_init import db_init

db_init()

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('db/database.db')
    conn.row_factory = sqlite3.Row
    return conn

# легаси пример
@app.route("/login=<string:number>", methods=["GET", "POST"])
def index2(number):
    if request.method == "POST":
        print("\n"+number)
        info ={"1":"hello"}
        return jsonify(info) 
    
# ревращаем строку в число
def time_to_int(time_str):
    #print(time_str)
    answer_int=""
    splited_time = time_str.split("_")
    for time_part_num in range(0,len(splited_time)):
        make_splited_time=splited_time[time_part_num]
        if time_part_num == 6:
            while len(list(make_splited_time)) < 3:
                make_splited_time+="0"
        answer_int+=make_splited_time
        #print(answer_int)
    return int(answer_int)



# посчитать разницу между временами
def getDifference(cl_time,sv_time,format_answer):
    first_less_then_second = "-"
    diff_is = ""
    splited_cl_time = cl_time.split("_")
    splited_sv_time = sv_time.split("_")
    for time_part_num in range(0,len(splited_sv_time)):
        if int(splited_sv_time[time_part_num]) > int(splited_cl_time[time_part_num]):
            diff_is+= str(int(splited_sv_time[time_part_num]) - int(splited_cl_time[time_part_num]))+"_"
            if first_less_then_second == "-":
                first_less_then_second="True"
        else:
            diff_is+="0_"
            if first_less_then_second == "-":
                first_less_then_second="False"
    # print(splited_cl_time, splited_sv_time)
    answer = first_less_then_second
    if format_answer == "nums":
        answer = diff_is[:-1]
    return answer

def get_time_at_server():
    time_from_server = str(datetime.utcnow().year)+"_"+str(datetime.utcnow().month)+"_"+str(datetime.utcnow().day)+"_"
    time_from_server += str(datetime.utcnow().hour)+"_"+str(datetime.utcnow().minute)+"_"+str(datetime.utcnow().second)+"_"+str(datetime.utcnow().microsecond)[:3]
    return time_from_server





# пользователь выходит из аккаунта
@app.route("/exit/<string:user_name>", methods=["GET", "POST"])
def exit(user_name):
    # спрашиваем у браузера куки с определенным именем
    session_key = request.cookies.get('metronome_session_key_' + user_name)
    conn = get_db_connection()
    # удаляем ключ сесии из базы данных
    sql = 'DELETE FROM sessions_web WHERE session_key=?'
    cur = conn.cursor()
    cur.execute(sql, (session_key,))
    conn.commit()
    # удаляем куки в браузере пользователя
    response = make_response( redirect("/")) # рисуем сраничку в браузере
    response.delete_cookie('metronome_session_key_' + user_name)
    return response
    
    
# загружаем файлы в метроном
@app.route("/room/<string:room_name>/assets/audio/<path:filename>", methods=["GET"])
def metron1(filename,room_name):
    print(" - - ",filename)
    return send_from_directory("static/assets/audio/", filename, as_attachment=True)


# открываем метроном
@app.route("/metron/", methods=["GET", "POST"])
def metron():
    return render_template("metron.html")
    

    
    
    
    
    
# страница входа
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form["name"]
        password = request.form["password"]
        print(name, password)
        if name!="" and password!="":
            conn = get_db_connection()
            # получаем список всех пользоваетелей, которые удовлетворяют введенным значениям
            getLoginList = conn.execute('SELECT * FROM users WHERE name_login = ? AND password_login = ?',(name,password)).fetchall()
            conn.close()
            
            # если найден пльзователь с таким именем и паролем
            if len(getLoginList) == 1:
                
                # создаем куки-сессионый ключ
                time_now = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                dk = hashlib.pbkdf2_hmac('sha256', bytes(time_now+"m0nd4y", 'utf-8'), b'salt', 100000)
                key_s = dk.hex()
                cooky_max_age = 60*60*16  # 60*60*24*365*1 на один год хранения куки
                
                # сохраняем ключ в базе
                connection = sqlite3.connect('db/database.db')
                cur = connection.cursor()
                cur.execute("INSERT INTO sessions_web (session_key, users_name_login) VALUES (?, ?)",(key_s, name,))
                connection.commit()
                connection.close()
                
                # отправляем ответ клиенту
                response = make_response( redirect("/home/"+name)) # рисуем сраничку в браузере
                response.set_cookie('metronome_session_key_'+name,  key_s, cooky_max_age) # отрпавляем куки браузеру
                return response
            else:
                return render_template("login.html", error_message="Неправильный логин или пароль!")
    
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    sqlite_select_query = """SELECT * from users"""
    cursor.execute(sqlite_select_query)
    records = cursor.fetchall()
    cursor.close()
    return render_template("login.html",error_message="",users_list =records )







# страница регистрации
@app.route("/registration/", methods=["GET", "POST"])
def registration():
    if request.method == "POST":
        name_reg = request.form["name_reg"]
        password_reg = request.form["password_reg"]
        conn = get_db_connection()
        getLoginList = conn.execute('SELECT * FROM users WHERE name_login = ?',
                        (name_reg,)).fetchall()
        conn.close()
        # если пользователь ввел уникальную комбинацию
        if len(getLoginList) == 0:
            
            # если пользователь что-то ввел
            if len(name_reg) > 0 and len(password_reg) > 0:
                if  len(name_reg) < 21:
                
                    # сохраняем пользователя в базе
                    connection = sqlite3.connect('db/database.db')
                    cur = connection.cursor()
                    cur.execute("INSERT INTO users (name_login, password_login, last_address) VALUES (?, ?, ?)",(name_reg, password_reg, "login"))
                    connection.commit()
                    connection.close()
                    
                    return redirect("/")
                else:
                    return render_template("registration.html", error_message="Максимально 20 символов!",succes_message="")
            else:
                return render_template("registration.html", error_message="Слишком короткое имя или пароль!",succes_message="")
        else:
            return render_template("registration.html", error_message="Пользователь с таким именем уже существует!",succes_message="")
    return render_template("registration.html",succes_message="")







# страница меню
@app.route("/home/<string:home_address>", methods=["GET", "POST"])
def home(home_address):
    # спрашиваем у браузера куки с определенным именем
    session_key = request.cookies.get('metronome_session_key_'+home_address)
    conn = get_db_connection()
    # получаем сессионный ключ
    getLoginList = conn.execute('SELECT * FROM sessions_web WHERE session_key = ? AND users_name_login = ?',(session_key,home_address,) ).fetchall() # WHERE session_key = ? ',(session_key,)
    conn.close()
    if len(getLoginList) == 1:
        conn = sqlite3.connect('db/database.db')
        cursor = conn.cursor()
        sqlite_select_query = """SELECT * from routing_users_to_rooms WHERE users_names = ?"""
        cursor.execute(sqlite_select_query, (home_address,))
        records = cursor.fetchall() # посмотреть комнаты в бд
        
        # меняем текущий адрес у пользователя
        sql_update_query = """Update users set last_address = ? where name_login = ?"""
        data = ("/home/"+home_address, home_address)
        cursor.execute(sql_update_query, data)
        conn.commit()
        cursor.close()
        
        return render_template("home.html", name=home_address,  rooms=records)
    return redirect("/")






# страница комнаты
@app.route("/room/<string:room_name>/<string:user_name>", methods=["GET", "POST"])
def room(room_name, user_name):
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    
    # меняем текущий адрес у пользователя
    sql_update_query = """Update users set last_address = ? where name_login = ?"""
    data = ("/room/"+room_name, user_name)
    cursor.execute(sql_update_query, data)
    conn.commit()
    
    # проверяем роль пользователя в данной комнате
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    sqlite_select_query = """SELECT * from routing_users_to_rooms WHERE rooms_names = ? AND users_names = ?"""
    cursor.execute(sqlite_select_query, (room_name,user_name))
    users_this_room = cursor.fetchall() 
    
    # достаем админа
    sqlite_select_query = """SELECT * from routing_users_to_rooms WHERE rooms_names = ? AND user_role_now = ?"""
    cursor.execute(sqlite_select_query, (room_name, "admin"))
    admin_is = cursor.fetchall() 
    
    start_word = "Ready"
    stop_word = "Waiting for"
    if users_this_room[0][4] == "admin":
        start_word = "Start"
        stop_word = "Stop"
        
    cursor.close()
        
    return render_template("room.html", room_name=room_name,  opener=user_name, opener_role=users_this_room[0][4], start_word = start_word, stop_word = stop_word, administrator_name = admin_is[0][1])








# обновляем информацию о пользователях в комнате онлайн
@app.route("/room/<string:room_name>/<string:user_name>/<string:presence_state>/time/<string:time_from_client>", methods=["GET", "POST"])
def get_musicians_list(room_name, user_name, presence_state, time_from_client):
    now_delay = getDifference(time_from_client,get_time_at_server(),"nums")
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    
    if presence_state != "get_musicians_list":
        # меняем текущий адрес у пользователя - если пользователь не просит список музыкантов, значит он не смотрит на страницу в открытом браузере
        sql_update_query = """Update users set last_address = ? where name_login = ?"""
        data = ("/room/not_here//", user_name)
        cursor.execute(sql_update_query, data)
        conn.commit()
        
    else:
        # меняем текущий адрес у пользователя
        sql_update_query = """Update users set last_address = ? where name_login = ?"""
        data = ("/room/"+room_name, user_name)
        cursor.execute(sql_update_query, data)
        conn.commit()
        
        # отмечаем время посещение
        sql_update_query = """Update routing_users_to_rooms set last_presence = ? where users_names = ? and rooms_names = ?"""
        data = (time_from_client, user_name, room_name)
        cursor.execute(sql_update_query, data)
        conn.commit()
        
        # записываем задержку между временем у клиента и временем на сервре включая время на доставку сообщения
        sql_update_query = """Update routing_users_to_rooms set last_delay = ? where users_names = ? and rooms_names = ?"""
        data = (now_delay, user_name, room_name)
        cursor.execute(sql_update_query, data)
        conn.commit()
    cursor.close()
    
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()
    sqlite_select_query = """SELECT * from routing_users_to_rooms WHERE rooms_names = ?"""
    cursor.execute(sqlite_select_query, (room_name,))
    records = cursor.fetchall() # посмотреть комнаты в бд это для создания списка участников данной комнаты
    online_dict ={}
    for one_partner in records:
        # проверяем, открыта ли у данного участника сейчас эта комната
        sqlite_select_query = """SELECT * from users WHERE name_login = ?"""
        cursor.execute(sqlite_select_query, (one_partner[1],))
        partners_datas = cursor.fetchall()
        
        for partner_data in partners_datas:
            if partner_data[4] == "/room/"+room_name:
                # print("  User", partner_data[2], "in this room") 
                online_dict[partner_data[2]]="in this room now"
            else:
                online_dict[partner_data[2]]="anywhere"
    cursor.close()
    musicians_list = []
    
    # перечисляем пользователей данной комнаты
    for i in records:
        
        # если мы взяли информацию про пользователя, кторому сейчас пойдет этот ответ от сервера
        if i[1] == user_name:
            if i[6] == "-":
                conn = sqlite3.connect('db/database.db')
                cursor = conn.cursor()
                # записываем задержку между временем у клиента и временем на сервре включая время на доставку сообщения как максимальную
                sql_update_query = """Update routing_users_to_rooms set max_delay = ? where users_names = ? and rooms_names = ?"""
                data = (now_delay, user_name, room_name)
                cursor.execute(sql_update_query, data)
                conn.commit()
                cursor.close()
            elif i[7] != "-" and  i[6] != "-" and time_to_int(i[6]) < time_to_int(i[7]):
                conn = sqlite3.connect('db/database.db')
                cursor = conn.cursor()
                # записываем задержку между временем у клиента и временем на сервре включая время на доставку сообщения как максимальную
                sql_update_query = """Update routing_users_to_rooms set max_delay = ? where users_names = ? and rooms_names = ?"""
                data = (now_delay, user_name, room_name)
                cursor.execute(sql_update_query, data)
                conn.commit()
                cursor.close()

            # print(i[6],now_delay)

        
        # по умолчанию оставляем статус присутствия таким, каким мы егосделали проверяя открытость вкладки браузера. но ниже мы проверим давтость сообщений, и возмжно изменим статус присутствия
        presence_real_state = online_dict[i[1]]
        if i[5] != "-":
            # максимально допустимая задержка неотправки сообщения на сервер у обычного слушателя в комнате - 2 сек
            if getDifference(i[5],get_time_at_server(),"nums")[:11]!="0_0_0_0_0_0" and getDifference(i[5],get_time_at_server(),"nums")[:12]!="0_0_0_0_0_1_" and getDifference(i[5],get_time_at_server(),"nums")[:12]!="0_0_0_0_0_2_":
                # пользователь посещал комнату более 2х секунд назад и сейчас у него либо пропал интернет либо он закрыл браузер
                presence_real_state="anywhere"
                
                conn = sqlite3.connect('db/database.db')
                cursor = conn.cursor()
                
                # обнуляем задержку между временем у клиента и временем на сервре включая время на доставку сообщения - чтобы не учитывать этого пользователя при созданиии временеи старта
                sql_update_query = """Update routing_users_to_rooms set last_delay = ? where users_names = ? and rooms_names = ?"""
                data = ("-", i[1], room_name)
                cursor.execute(sql_update_query, data)
                conn.commit()
                
                # обнуляем максимальную задержку между временем у клиента и временем на сервре включая время на доставку сообщения - чтобы не учитывать этого пользователя при созданиии временеи старта
                sql_update_query = """Update routing_users_to_rooms set max_delay = ? where users_names = ? and rooms_names = ?"""
                data = ("-", i[1], room_name)
                cursor.execute(sql_update_query, data)
                conn.commit()
                
        else:
            # видимо пользователь стал участником комнаты но ниразу ее еще не посетил
            presence_real_state="anywhere"
            
        # соотношение текущей задержки к максимальной у этого пользователя в этой комнате в это посещение
        state_delay =""
        if i[7] != "-" and  i[6] != "-":
            if time_to_int(i[7])/time_to_int(i[6])>0.95:
                state_delay ="red"
            print("  ",i[1],"- ",time_to_int(i[7])," ",time_to_int(i[6]))
            
        # созаем список кортежей для отбражения участников комнаты сейчас
        new_row =(i[1],i[4],presence_real_state, state_delay)
        
        musicians_list.append(new_row)
        
    return json.dumps({"musicians_list":musicians_list})   











# обработка команд одной комнаты
@app.route("/room/<string:room_name>/<string:user_name>/player/<string:command>/<string:time_from_client>", methods=["GET", "POST"])
def start(room_name, user_name, command, time_from_client):
    
    # если кто-то включает метроном
    if command == "Start":
        # идем берем список всех участников комнаты
        conn = sqlite3.connect('db/database.db')
        cursor = conn.cursor()
        sqlite_select_query = """SELECT * from routing_users_to_rooms WHERE rooms_names = ?"""
        cursor.execute(sqlite_select_query, (room_name,))
        partners_this_room = cursor.fetchall()
        
        max_delay_of_users_in_this_room = 0
        for one_partner in partners_this_room:
            # проверяем, открыта ли у данного участника сейчас эта комната
            if one_partner[6]!="-" and one_partner[7]!="-":
                print("  User", one_partner[1], "in this room")
                # значит его можно учитывать при создании времени общего старта
                if time_to_int(one_partner[6]) > max_delay_of_users_in_this_room:
                    max_delay_of_users_in_this_room = time_to_int(one_partner[6])
        print("  Max delay in room '"+room_name+"' now - ", max_delay_of_users_in_this_room, "milliseconds")
        time_next_sound_from_server = math.ceil(((max_delay_of_users_in_this_room*4)/1000)) # делаем отступ в два разапревышающий максимальную задержку, чтобы все пользователи точь успели получить время насала игры до амого времени
        tm_sv = get_time_at_server().split("_")
        tm_sv[5]=str(int(tm_sv[5]) + time_next_sound_from_server) # добавляем к текущему времени на сервере время отступа, перед началом игры
        if int(tm_sv[5]) > 59: # корректируем время если оно превышает лимиты
            tm_sv[5] = str(int(tm_sv[5]) - 60)
            tm_sv[4] = str(int(tm_sv[4]) + 1)
            if int(tm_sv[4]) > 59:
                tm_sv[4] = str(int(tm_sv[4]) - 60)
                tm_sv[3] = str(int(tm_sv[3]) + 1)
                if int(tm_sv[3]) > 23:
                    tm_sv[3] = str(int(tm_sv[3]) - 24)
                    tm_sv[2] = str(int(tm_sv[2]) + 1)
        tm_sv_str=""
        for num_tm_sv in tm_sv[:-1]:
            tm_sv_str+=num_tm_sv+"_"
        time_next_sound_from_server_str = tm_sv_str
        
        # меняем текущий статус активации в комнате
        sql_update_query = """Update rooms set activation_state = ? where room_name = ?"""
        data = (tm_sv_str,room_name)
        cursor.execute(sql_update_query, data)
        conn.commit()
    
        cursor.close()
        
        return json.dumps({'bpm_from_server': get_time_at_server(),'time_next_sound_from_server': time_next_sound_from_server_str,'time_next_sound_from_server_hour': tm_sv[3], 'time_next_sound_from_server_minute': tm_sv[4], 'time_next_sound_from_server_second': tm_sv[5]})
        
    
    if command == "Ready":
        # проверяем активна ли данная комната
        conn = sqlite3.connect('db/database.db')
        cursor = conn.cursor()
        sqlite_select_query = """SELECT * from rooms WHERE room_name = ? """
        cursor.execute(sqlite_select_query, (room_name,))
        room_data = cursor.fetchall() 
        
        # достаем админа
        sqlite_select_query = """SELECT * from routing_users_to_rooms WHERE rooms_names = ? AND user_role_now = ?"""
        cursor.execute(sqlite_select_query, (room_name, "admin"))
        admin_is = cursor.fetchall() 
        
        room_activation_state = room_data[0][4]
        tm_sv=["-","-","-","-","-","-"]
        if len(room_activation_state)>3:
            tm_sv=room_activation_state.split("_")
            print("\ntm_sv -  ",tm_sv,"\n")
        
        return json.dumps({'bpm_from_server': get_time_at_server(),'time_next_sound_from_server': room_activation_state,'time_next_sound_from_server_hour': tm_sv[3], 'time_next_sound_from_server_minute': tm_sv[4], 'time_next_sound_from_server_second': tm_sv[5], 'administrator_name': admin_is[0][1]})
        
    print(room_name, user_name, " - ", command)
    return ('', 204)






app.run(debug=True)
