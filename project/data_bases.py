import sqlite3
from config import BASE_NAME


def execute_quere(sql_quere, data = None, db_name=f'{BASE_NAME}'):
    con = sqlite3.connect(db_name)
    cursor = con.cursor()
    if data:
        cursor.execute(sql_quere,data)
    else:
        cursor.execute(sql_quere)
    con.commit()
    con.close()

def execute_selection_quere(sql_quere, data = None, db_name=f'{BASE_NAME}'):
    con = sqlite3.connect(db_name)
    cursor = con.cursor()
    if data:
        cursor.execute(sql_quere,data)
    else:
        cursor.execute(sql_quere)
    rows = cursor.fetchall()
    con.close()
    return rows

def create_table(table_name):
    sql_quere = f''' CREATE TABLE IF NOT EXISTS {table_name}(
    id INTEGER PRIMARY KEY,
    user_id TEXT,
    role TEXT,
    content TEXT,
    date DATETIME,
    session INTEGER,
    tokens INTEGER);
    '''
    execute_quere(sql_quere)

def insert_session(values):
    sql_quere = '''
    INSERT INTO Promts (session) VALUES(?)
    '''
    execute_quere(sql_quere,values)

def get_session(user_id):
    sql_quere = f'''SELECT session from Promts WHERE user_id="{user_id}"
                '''
    return execute_selection_quere(sql_quere)

def insert_user_id(value):
    sql_quere = '''
    INSERT INTO Promts(user_id) VALUES(?)
    '''
    execute_quere(sql_quere,value)



def get_token_by_user_id(user_id,session):
    sql_quere = f'''
    SELECT tokens FROM Promts WHERE user_id = "{user_id}" AND session={session}
    '''
    execute_selection_quere(sql_quere)

def insert_tokens(value):
    sql_quere = '''
    INSERT INTO Promts (tokens) VALUES(?)
    '''
    execute_quere(sql_quere,value)


def insert_date(value):
    sql_quere = '''
    INSERT INTO Promts (date) VALUES(?)
    '''
    execute_quere(sql_quere,value)

def insert_info(value):
    sql_quere = '''INSERT INTO Promts (user_id, role, content, date, tokens, session) VALUES(?,?,?,?,?,?)'''
    execute_quere(sql_quere,value)

def check_users(MAX_USERS=3):
    sql_quere = '''SELECT DISTINCT user_id from Promts'''
    execute_selection_quere(sql_quere)
