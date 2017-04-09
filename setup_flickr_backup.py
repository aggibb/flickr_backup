from FlickrBackup import FlickrAccess, FlickrBackup
import sys


print "Setting up Flickr backup: authenticating with Flickr..."
try:
    flickr = FlickrAccess.create_flickrapi_object()
except:
    print "Authentication failed... :-("
    sys.exit(1)

print "Authentication successful - creating the backup database"
FlickrBackup.create_flickr_backup_db()
