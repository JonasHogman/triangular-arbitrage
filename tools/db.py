import rethinkdb as r

conn = None


def get_connection():
    global conn
    if not conn:
        conn = r.connect("localhost", 28015, db='arbitrage')

    return conn
