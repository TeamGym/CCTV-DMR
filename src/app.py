#!/usr/bin/env python3

import web, db
import logging as l

# Connect to database
# and run web server

def main():
    l.basicConfig(level=l.INFO)
    try:
        database = db.Database()
        database.initialize()
        web.run(database)
        database.connection.close()
    except Exception as e:
        l.exception(e)

if __name__ == '__main__':
    main()
