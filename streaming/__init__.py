from flask import Flask
import sqlite3
import time


# TODO: Create table that handles "current time"?
create_param_table = """
    CREATE TABLE IF NOT EXISTS parameters
    (distribution TEXT, params TEXT)
"""
# sqlite doesn't allow you to store an array, so params will be written to text
# and then parsed. Bad idea? params field will hold starting values as well, as
# some distributions require a few (AR lags, etc).


# NB: You should not update Flask app config on the fly, per:
#     https://stackoverflow.com/questions/39456672/how-to-reload-a-configuration-file-on-each-request-for-flask
#     No safe way to do it. Instead putting data into a table and updating
#     that.
def create_app():
    app = Flask(__name__)

    conn = sqlite3.connect('mcwi.db')
    c = conn.cursor()
    c.execute(create_param_table)
    conn.commit()
    conn.close()
    # Is creating tables in __init__.py a bad practice?

    return app
