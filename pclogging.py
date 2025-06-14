#
#
# logging system from Project Curacao
# filename: pclogger.py
# Version 1.0 10/04/13
#
# contains logging data
#

CRITICAL = 50
ERROR = 40
WARNING = 30
INFO = 20
DEBUG = 10
NOTSET = 0

import sys
import time

# Check for user imports
try:
    import conflocal as config
except ImportError:
    import config

if config.enable_MySQL_Logging:
    import MySQLdb as mdb

def log(level, source, message):
    if config.enable_MySQL_Logging:
        LOWESTDEBUG = 0

        if level >= LOWESTDEBUG:
            con = None
            cur = None
            try:
                # print("trying database")
                con = mdb.connect(
                    'localhost',
                    config.MySQL_User,
                    config.MySQL_Password,
                    'GroveWeatherPi'
                )
                cur = con.cursor()

                query = "INSERT INTO systemlog(TimeStamp, Level, Source, Message) VALUES(UTC_TIMESTAMP(), %i, '%s', '%s')" % (
                    level,
                    source,
                    message
                )
                # print("query=%s" % query)

                cur.execute(query)
                con.commit()

            except mdb.Error as e:
                print("Error %d: %s" % (e.args[0], e.args[1]))
                if con:
                    con.rollback()

            finally:
                if cur:
                    cur.close()
                if con:
                    con.close()

                del cur
                del con
