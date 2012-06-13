import psycopg2
import sys

from dj_database_url import config as get_db_config

# Parse the database configuration into something psycopg2 can handle
raw_dbconfig = get_db_config(default='postgres://hurley@localhost/cacheusage')
dbconfig = {}
if raw_dbconfig['NAME']:
    dbconfig['database'] = raw_dbconfig['NAME']
if raw_dbconfig['USER']:
    dbconfig['user'] = raw_dbconfig['USER']
if raw_dbconfig['PASSWORD']:
    dbconfig['password'] = raw_dbconfig['PASSWORD']
if raw_dbconfig['HOST']:
    dbconfig['host'] = raw_dbconfig['HOST']
if raw_dbconfig['PORT']:
    dbconfig['port'] = raw_dbconfig['port']

def get_conn():
    return psycopg2.connect(**dbconfig)

if __name__ == '__main__':
    conn = get_conn()
    cur = conn.cursor()
    if sys.argv[1] == 'dump':
        cur.execute('SELECT * FROM reports')
        res = cur.fetchall()
        for r in res:
            print r[0]
    elif sys.argv[1] == 'clean':
        cur.execute('DELETE FROM reports')
    conn.commit()
    conn.close()
