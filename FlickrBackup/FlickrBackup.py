import os
import sqlite3
from datetime import datetime


def get_backup_directory():
    return os.path.join(os.path.expanduser('~'),'.flickr')


def check_database():
    try:
        get_database_summary()
    except sqlite3.Error as e:
        print "Error establishing database connection:", e.args[0]
        print "Please run 'setup_flickr_backup' first "
        sys.exit(1)


def get_flickr_user_from_auth():
    flickr_oauth_db_filename = os.path.join(get_backup_directory(),'oauth-tokens.sqlite')
    with sqlite3.connect(flickr_oauth_db_filename) as oconn:
        c = oconn.cursor()
        c.execute('''select user_nsid, username, fullname from oauth_tokens''')
        flickr_user_id = c.fetchone()
    oconn.close()
    return {'nsid': flickr_user_id[0], 'username': flickr_user_id[1], 'fullname': flickr_user_id[2],
            'created_on': datetime.now()}


def store_flickr_user_details(c):
    flickr_user = get_flickr_user_from_auth()
    c.execute('''insert into flickr_user (nsid, username, fullname, last_update)
        values (:nsid, :username, :fullname, :created_on)''',flickr_user)
    print "Stored details for Flickerite " + flickr_user['fullname'] + " (" + flickr_user['username'] + ") in backup db"
    return None


def get_flickr_backup_db():
    return os.path.join(get_backup_directory(),'flickr_backup.sqlite')


def create_flickr_backup_db():
    flickr_db_filename = get_flickr_backup_db()
    if not os.path.exists(flickr_db_filename):
        with sqlite3.connect(flickr_db_filename) as conn:
            print "Creating new Flickr backup database,", flickr_db_filename
            schema_file = 'create_schema.sql'
            with open(schema_file, 'rt') as f:
                schema = f.read()
            conn.executescript(schema)
            store_flickr_user_details(conn.cursor())
            conn.commit()
        conn.close()
    else:
        get_database_summary()
    return flickr_db_filename


def show_db_details(conn):
    cursor = conn.cursor()
    cursor.execute('''select count(id) from flickr_photo''')
    number_of_entries = cursor.fetchone()[0]
    cursor.execute('''select nsid, username, fullname from flickr_user''')
    flickr_user = cursor.fetchone()
    print "Database set up for " + flickr_user[2] + " (" + flickr_user[1] +\
          "), and currently contains " + str(number_of_entries) + " entries"
    return None


def get_database_summary():
    flickr_db_filename = get_flickr_backup_db()
    if os.path.exists(flickr_db_filename):
        with sqlite3.connect(flickr_db_filename) as conn:
            print "Found existing database,", flickr_db_filename, "- will use this one"
            show_db_details(conn)
        conn.close()
    else:
        raise sqlite3.Error("Flickr backup database does not yet exist")
    return None


def get_database_connection():
    flickr_db_filename = get_flickr_backup_db()
    if not os.path.exists(flickr_db_filename):
        create_flickr_backup_db()
    return sqlite3.connect(flickr_db_filename)


def get_flickr_nsid():
    with get_database_connection() as conn:
        c = conn.cursor()
        c.execute('''select nsid from flickr_user''')
        flickr_nsid = c.fetchone()
    conn.close()
    return flickr_nsid[0]


def record_update_time():
    with get_database_connection() as conn:
        c = conn.cursor()
        c.execute('''update flickr_user set last_update = :last_update''', {'last_update': datetime.now()})
    conn.close()
    return None


def get_last_update_timestamp():
    with get_database_connection() as conn:
        c = conn.cursor()
        c.execute('''select last_update from flickr_user''')
        last_update = c.fetchone()
    conn.close()
    return last_update[0]
