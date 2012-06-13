import json
import os

from flask import Flask, request, g

import db

app = Flask(__name__)

@app.before_request
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
    g.db.execute('INSERT INTO reports (json) VALUES (%s)', (request.data,))

    return json.dumps({'status':'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
