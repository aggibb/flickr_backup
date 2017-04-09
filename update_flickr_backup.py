import sqlite3
import sys
from FlickrBackup import FlickrPhotos, FlickrBackup


def check_database():
    try:
        FlickrBackup.get_database_summary()
    except sqlite3.Error as e:
        print "Error establishing database connection:", e.args[0]
        print "Please run 'setup_flickr_backup' first "
        sys.exit(1)


if __name__ == "__main__":
    check_database()
    FlickrPhotos.update_photo_details()
    # should also trigger an update of the disk photo table as well - at some point in the future!
