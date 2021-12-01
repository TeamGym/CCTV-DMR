import sqlite3
import pathlib

class Database:
    sql_initialize = """
    CREATE TABLE IF NOT EXISTS cctv (
      id integer PRIMARY KEY,
      location text NOT NULL,
      directory text NOT NULL
    );
    """

    def __init__(self, db_file="db/cctv.db"):
        self.db_file = db_file
        self.connection = None

    def initialize(self):
        pathlib.Path(self.db_file).parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.db_file)
        c = connection.cursor()
        c.execute(self.sql_initialize)
        connection.commit()
