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
    sql_quere = f'''
    CREATE TABLE IF NOT EXISTS {table_name}(
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    role TEXT,
    content TEXT,
    date TEXT,
    tokens INTEGER,
    session INTEGER);
    '''
    execute_quere(sql_quere)

def insert_row_user_id_session(user_id, session):
    sql_quere = '''
    INSERT INTO Promts(user_id, session) Values(?,?)
    '''
    execute_quere(sql_quere,user_id,session)

def insert_row_content(values):
    sql_quere = '''
    INSERT INTO Promts(content) Values(?)
    '''
    execute_quere(sql_quere,values)


def get_row_by_user_id(user_id,session):
    sql_quere = f'''
    SELECT tokens FROM Promts WHERE user_id = {user_id} AND session={session}
    '''
    execute_selection_quere(sql_quere)

def get_row_session(user_id):
    sql_quere = f'''
    SELECT session FROM Promts WHERE user_id={user_id}
    '''
    execute_selection_quere(sql_quere)

