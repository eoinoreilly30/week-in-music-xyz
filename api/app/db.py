import logging
import sqlite3
from sqlite3 import Error

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        logging.error(e)
 
    return conn


def create_table(conn, create_table_sql):
    try:
        cursor = conn.cursor()
        cursor.execute(create_table_sql)
    except Error as e:
        logging.error(e)


def init_database():
    sql_create_projects_table = """ CREATE TABLE IF NOT EXISTS users (
                                        id integer PRIMARY KEY,
                                        name text NOT NULL,
                                        begin_date text,
                                        end_date text
                                    ); """
 
    sql_create_tasks_table = """CREATE TABLE IF NOT EXISTS tasks (
                                    id text PRIMARY KEY,
                                    access_token text NOT NULL,
                                    refresh_token text NOT NULL,
                                    email text NOT NULL,
                                    scheduling_type text NOT NULL,
                                    playing_time_by_day text NOT NULL,
                                    FOREIGN KEY (project_id) REFERENCES projects (id)
                                );"""
 
    # create a database connection
    conn = create_connection(database)
 
    # create tables
    if conn is not None:
        # create projects table
        create_table(conn, sql_create_projects_table)
 
        # create tasks table
        create_table(conn, sql_create_tasks_table)
    else:
        print("Error! cannot create the database connection.")


def add_user(user_id, access_token, refresh_token, email, scheduling_type):
    # TODO: check if user exists

    db_connection = create_connection()

    id = user_id + '-' + email
    doc = {
        'user_id': id,
        'access_token': access_token,
        'refresh_token': refresh_token,
        'email': email,
        'scheduling_type': scheduling_type,
        'playing_time_by_day': {}
    }

    response = es.index(index='users', doc_type="user", id=id, body=doc)

    logging.info('Added user ' + id)

    db_connection.close()
