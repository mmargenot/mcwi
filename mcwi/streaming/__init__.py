from . import api
from . import client
from . import server

from flask import Flask
import sqlite3
import time


# TODO: Create table that handles "current time"?
create_param_table = """
    CREATE TABLE IF NOT EXISTS parameters
    (distribution TEXT, params BLOB)
"""


def create_app():
    app = Flask(__name__)

    conn = sqlite3.connect('mcwi.db')
    c = conn.cursor()
    c.execute(create_param_table)
    conn.commit()
    conn.close()

    return app
