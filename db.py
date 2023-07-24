import sqlite3


def connect_bd():
    con = sqlite3.connect('captcha_bd.db')
    cur = con.cursor()
    return con, cur


def insert_table():
    con, cur = connect_bd()
    cur.execute(f"""CREATE TABLE articles(
        user_id integer,
        nickname text,
        pop integer,
        time_out integer,
        captcha text,
        PRIMARY KEY(user_id)
        )""")
    con.commit()
    con.close()


def insert_user(info, captcha):
    con, cur = connect_bd()
    cur.execute(f"""INSERT OR IGNORE INTO articles
            (user_id, nickname, pop, time_out, captcha)
            VALUES
            ({info.from_user.id},
            '{info.from_user.username}',
            {3},
            '{0}',
            '{captcha}');""")
    con.commit()


def update_db_user_pop(user_id, pop):
    con, cur = connect_bd()
    cur.execute(
        f"""UPDATE articles SET pop='{pop}' WHERE user_id='{user_id}'""")
    con.commit()
    con.close()


def update_db_user_timeout(user_id, timeout):
    con, cur = connect_bd()
    cur.execute(
        f"""UPDATE articles SET time_out='{timeout}' WHERE user_id='{user_id}'""")
    con.commit()
    con.close()


def update_db_user_captcha(user_id, captcha):
    con, cur = connect_bd()
    cur.execute(
        f"""UPDATE articles SET captcha='{captcha}' WHERE user_id='{user_id}'""")
    con.commit()
    con.close()


def gate_timeout(user_id):
    con, cur = connect_bd()
    tim = cur.execute(
        f"""SELECT time_out FROM articles WHERE user_id='{user_id}'""").fetchone()
    con.commit()
    con.close()
    if tim == None:
        return None
    return tim[0]


def gate_pop(user_id):
    con, cur = connect_bd()
    pop = cur.execute(
        f"""SELECT pop FROM articles WHERE user_id='{user_id}'""").fetchone()
    con.commit()
    con.close()
    return pop[0]


def gate_captcha(user_id):
    con, cur = connect_bd()
    capt = cur.execute(
        f"""SELECT captcha FROM articles WHERE user_id='{user_id}'""").fetchone()
    con.commit()
    con.close()
    return capt[0]


def gate_user(user_id):
    con, cur = connect_bd()
    sql_find = cur.execute(f"SELECT * FROM articles WHERE user_id = {user_id}").fetchall()
    con.commit()
    con.close()
    return bool(len(sql_find))


def delete_user(user_id):
    con, cur = connect_bd()
    sql_delete = cur.execute(f'DELETE from articles where user_id="{user_id}"')
    con.commit()
    con.close()
    print(f'Пользователь {user_id} удален из БД')

