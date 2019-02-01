import rethinkdb as r
from tools.pairs import triangular_pair_list
from influxdb import InfluxDBClient

_conn = None
_influxconn = None


def get_connection():
    """
    Return a database connection
    :return:
    """
    global _conn
    if not _conn:
        _conn = r.connect("localhost", 28015, db='arbitrage')

    return _conn

def get_influx_connection():
    global _influxconn
    if not _influxconn:
        _influxconn = InfluxDBClient('localhost', 8086, 'root', 'root', 'arbitrage')

    return _influxconn

def create_database(name):
    """
    Delete the old database and create a new empty one
    :param name: name of database to be created
    """
    conn = get_connection()
    try:
        print('Deleting old database...')
        r.db_drop(name).run(conn)
    except r.ReqlOpFailedError:
        pass

    print('Creating new database...')

    try:
        r.db_create(name).run(conn)
    except r.ReqlOpFailedError as e:
        print(e)

    print('Creating new tables and indexes...')

    for item in triangular_pair_list():
        new_table = "{}_{}_{}".format(item[0], item[1], item[2])
        r.db(name).table_create(new_table).run(conn)
        r.table(new_table).index_create('timestamp').run(conn)

    r.db(name).wait()
    print('Tables created!')
