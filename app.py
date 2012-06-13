import json
import os
import psycopg2

from dj_database_url import config as get_db_config
from flask import Flask, request, g

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

app = Flask(__name__)

import logging
app.logger.setLevel(logging.DEBUG)
app.logger.addHandler(logging.FileHandler('/Users/hurley/heroku.txt'))

@app.before_request
def before_request():
    """Set up the database connection so we have it available in the request
    """
    app.logger.debug('cfg = %s' % (str(dbconfig),))
    # First, make sure we have the table we need
    conn = psycopg2.connect(**dbconfig)
    cur = conn.cursor()
    cur.execute('''
            CREATE OR REPLACE FUNCTION ensure_table() RETURNS void AS
            $_$
            BEGIN
                IF NOT EXISTS (
                    SELECT * FROM pg_catalog.pg_tables
                        WHERE tablename = 'reports'
                ) THEN
                    CREATE TABLE reports (json text);
                END IF;
            END;
            $_$ LANGUAGE plpgsql;''')
    cur.execute('SELECT ensure_table()')

    g.db = cur

@app.teardown_request
def teardown_request(arg):
    """Commit our changes and close the database connection to not waste
    resources
    """
    g.db.connection.commit()
    g.db.connection.close()
    g.db = None

@app.route('/')
def index():
    return 'Nothing to see here!'

@app.route('/report', methods=['POST'])
def report():
    rval = {'status':'fail'}
    for k, v in request.form.iteritems():
        try:
            info = json.loads(k)
        except:
            continue

        g.db.execute('INSERT INTO reports (json) VALUES (%s)', (k,))
        rval['status'] = 'ok'
        break

    return json.dumps(rval)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
