import os

import psycopg2


def db_open():
    # Connect to the database
    conn = psycopg2.connect(database=os.getenv('POSTGRES_DB_NAME'), user=os.getenv('POSTGRES_DB_USER'), password=os.getenv('POSTGRES_DB_PASS'), host=os.getenv('POSTGRES_DB_HOST'), port=os.getenv('POSTGRES_DB_PORT'))
    # create a cursor
    cur = conn.cursor()
    return conn, cur


def db_close(conn, cur):
    cur.close()
    conn.close()


def insert_user(data):
    username = data['username']
    password = data['password']
    uuid = data['uuid']

    query = "INSERT INTO users (username, password, uuid) VALUES (%s, %s, %s)"

    conn, cur = db_open()
    result = cur.execute(query, (username, password, uuid))
    conn.commit()
    db_close(conn, cur)

    return result


def get_user(data):
    username = data['username']
    password = data['password']

    query = "SELECT * FROM users WHERE username = %s and password = %s"

    conn, cur = db_open()
    cur.execute(query, (username, password))
    # Fetch the data
    result = cur.fetchall()
    db_close(conn, cur)

    return result


def get_user_apps(data):
    uuid = data['uuid']
    query = "SELECT * FROM apps WHERE user_uuid = '"+uuid+"'"
    conn, cur = db_open()
    cur.execute(query)
    # Fetch the data
    result = cur.fetchall()
    db_close(conn, cur)
    return result


def insert_app(data):
    title = data['title']
    description = data['description']
    uuid = data['uuid']
    app_id = data['app_id']

    query = "INSERT INTO apps (title, description, user_uuid, app_id) VALUES (%s, %s, %s, %s)"

    conn, cur = db_open()
    result = cur.execute(query, (title, description, uuid, app_id))
    conn.commit()
    db_close(conn, cur)

    return result


def get_app(data):
    app_id = data['app_id']
    query = "SELECT * FROM apps WHERE app_id = '" + app_id + "'"
    conn, cur = db_open()
    cur.execute(query)
    # Fetch the data
    result = cur.fetchall()
    db_close(conn, cur)
    return result
