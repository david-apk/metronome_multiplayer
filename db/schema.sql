DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    name_login TEXT NOT NULL,
    password_login TEXT NOT NULL,
    last_address TEXT NOT NULL
);

DROP TABLE IF EXISTS rooms;

CREATE TABLE rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    administrator_name_login TEXT NOT NULL,
    private_state TEXT NOT NULL,
    activation_state TEXT NOT NULL,
    room_name TEXT NOT NULL
);

DROP TABLE IF EXISTS routing_users_to_rooms;

CREATE TABLE routing_users_to_rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    users_names INTEGER NOT NULL,
    rooms_names INTEGER NOT NULL,
    time_of_last_change TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_role_now TEXT NOT NULL,
    last_presence TEXT NOT NULL,
    max_delay TEXT NOT NULL,
    last_delay TEXT NOT NULL

);

DROP TABLE IF EXISTS sessions_web;

CREATE TABLE sessions_web (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    users_name_login TEXT NOT NULL,
    session_key TEXT NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


DROP TABLE IF EXISTS calibrations;

CREATE TABLE calibrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_listener_name TEXT NOT NULL,
    user_admin_name TEXT NOT NULL,
    calibration_list TEXT NOT NULL
);
