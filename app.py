import json
import os

from flask import Flask, request, g

import db

app = Flask(__name__)

def before_request():
    """Set up the database connection so we have it available in the request
    """
    # First, make sure we have the table we need
    conn = db.get_conn()
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

    return cur

def teardown_request(cur):
    """Commit our changes and close the database connection to not waste
    resources
    """
    cur.connection.commit()
    cur.connection.close()

@app.route('/')
def index():
    return 'Nothing to see here!'

@app.route('/report', methods=['POST'])
def report():
    cur = before_request()
    cur.execute('INSERT INTO reports (json) VALUES (%s)', (request.data,))
    teardown_request(cur)

    return json.dumps({'status':'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
