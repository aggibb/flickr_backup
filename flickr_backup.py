import sqlite3
import sys, getopt
from FlickrBackup import FlickrPhotos, FlickrBackup


def read_command_line_args(argv):
    try:
        opts, args = getopt.getopt(argv,"hn:p:",["help","numpages=","page="])
    except getopt.GetoptError:
        print 'Usage: ...'
        sys.exit(2)

    numpages = 0
    page_number = 1
    for opt, arg in opts:
        if opt == '-h':
            print 'sys.argv[0] -n <numpages> -p <pagenum>'
            sys.exit()
        elif opt in ("-n", "--numpages"):
            numpages = int(arg)
        elif opt in ("-p", "--page"):
            page_number = int(arg)
    return numpages, page_number


if __name__ == "__main__":
    FlickrBackup.check_database()
    (number_of_pages, pagenum) = read_command_line_args(sys.argv[1:])
    FlickrPhotos.store_photo_details(number_of_pages, pagenum)
