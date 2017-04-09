import os, re
from datetime import datetime
from FlickrAccess import create_flickrapi_object
import FlickrBackup
from PIL import Image

def get_date_taken(photo):
    return datetime.strptime(str(photo['datetaken']), "%Y-%m-%d %H:%M:%S")


def get_date_uploaded(photo):
    return datetime.fromtimestamp(int(photo['dateupload']))


def get_last_update(photo):
    return datetime.fromtimestamp(int(photo['lastupdate']))


def get_privacy(photo):
    return (photo['ispublic'] << 2) + (photo['isfriend'] << 1) + photo['isfamily']


def add_photo_to_db(cursor, photo):
    cursor.execute('''insert or ignore into
                    flickr_photo(id, secret, original_secret, server, farm, privacy, date_taken,
                                 date_uploaded, last_update, media, url_o, width, height, title, description)
                    values (:id, :secret, :originalsecret, :server, :farm, :privacy,
                            :date_taken, :date_uploaded, :last_update, :media, :url_o, :width, :height,
                            :title, :description)''',
                   {'id': int(photo['id']), 'secret': photo['secret'], 'originalsecret': photo['originalsecret'],
                    'server': int(photo['server']), 'farm': photo['farm'], 'privacy': get_privacy(photo),
                    'date_taken': get_date_taken(photo), 'date_uploaded': get_date_uploaded(photo),
                    'last_update': get_last_update(photo), 'media': photo['media'], 'url_o': photo['url_o'],
                    'width': int(photo['width_o']), 'height': int(photo['height_o']), 'title': photo['title'],
                    'description': photo['description']['_content']})

    cursor.execute('''insert or ignore into geotag (longitude, latitude, accuracy)
                values (:longitude, :latitude, :accuracy)''',
                   {'longitude': float(photo['longitude']), 'latitude': float(photo['latitude']),
               'accuracy': int(photo['accuracy'])})
    geo_id = cursor.lastrowid
    cursor.execute('''update flickr_photo set geo_id = :geo_id where id = :id''',
                   {'geo_id': geo_id, 'id': int(photo['id'])})
    return None


def update_photo_db_entry(cursor, photo):
    photo_id = int(photo['id'])
    cursor.execute('''update flickr_photo set secret = :secret, original_secret = :original_secret, server = :server,
                    farm = :farm, privacy = :privacy, last_update = :last_update, url_o = :url_o, width = :width,
                    height = :height, title = :title, description = :description
                    where id = :id''',
                   {'id': photo_id, 'secret': photo['secret'], 'original_secret': photo['originalsecret'],
                    'server': int(photo['server']), 'farm': photo['farm'], 'privacy': get_privacy(photo),
                    'last_update': get_last_update(photo), 'url_o': photo['url_o'],
                    'width': int(photo['width_o']), 'height': int(photo['height_o']), 'title': photo['title'],
                    'description': photo['description']['_content']})
    cursor.execute('''select geo_id from flickr_photo where id = :id''', {'id': photo_id})
    geo_id = cursor.fetchone()
    cursor.execute('''update geotag set longitude = :longitude, latitude = :latitude, accuracy = :accuracy
                    where id = :geo_id''',
                   {'longitude': float(photo['longitude']), 'latitude': float(photo['latitude']),
                    'accuracy': int(photo['accuracy']), 'geo_id': geo_id[0]})
    return None


def store_photo_details(number_of_pages, page_number):
    flickr = create_flickrapi_object()
    extras = "description,date_upload,date_taken,last_update,media,original_format,geo,url_o"
    per_page = 100

    total_photos = number_of_pages * per_page
    if number_of_pages == 0:
        resp = flickr.people.getPhotos(user_id=FlickrBackup.get_flickr_nsid(), per_page=1)
        number_of_pages = resp['photos']['pages'] / per_page + 1
        total_photos = resp['photos']['total']
    max_pages = page_number + number_of_pages - 1
    print "Storing details for " + str(total_photos) + " photos (Flickr page " +\
          str(page_number) + " - " + str(max_pages) + ")"

    conn = FlickrBackup.get_database_connection()
    c = conn.cursor()
    start_page = page_number
    num_photos = 1
    while page_number <= max_pages:
        current_page = page_number - start_page + 1
        print "Processing page " + str(current_page) + " of " + str(number_of_pages) +\
              " (Flickr page " + str(page_number) + ")"
        resp = flickr.people.getPhotos(user_id=FlickrBackup.get_flickr_nsid(), page=page_number, per_page=per_page,
                                       extras=extras)
        for photo in resp['photos']['photo']:
            print "  Storing details for photo number " + str(num_photos) + " of " + str(total_photos) +\
                  ", id = " + photo['id'] + " (" + photo['title'] + ")"
            add_photo_to_db(c, photo)
            conn.commit()
            num_photos += 1
        page_number += 1
    conn.close()
    FlickrBackup.record_update_time()


def update_photo_details():
    flickr = create_flickrapi_object()
    extras = "description,date_upload,date_taken,last_update,media,original_format,geo,url_o"
    last_update = FlickrBackup.get_last_update_timestamp()
    conn = FlickrBackup.get_database_connection()
    c = conn.cursor()
    num_pages = 1
    current_page = 1
    page_check = False
    while current_page <= num_pages:
        resp = flickr.photos.recentlyUpdated(user_id=FlickrBackup.get_flickr_nsid(), min_date=last_update,
                                             extras=extras, page=current_page)
        num_pages = resp['photos']['pages']
        if page_check == False:
            if num_pages == 0:
                print "Database is up-to-date"
                break
            else:
                photos_str = 'photo' if (resp['photos']['total'] == '1') else 'photos'
                print "Bringing database up-to-date - updating or adding new details for", resp['photos']['total'], photos_str
                page_check = True
        current_page += 1
        for photo in resp['photos']['photo']:
            c.execute('''select id from flickr_photo where id = :id''', {'id': int(photo['id'])})
            if c.fetchone() is None:
                add_photo_to_db(c, photo)
            else:
                update_photo_db_entry(c, photo)
            conn.commit()
    conn.close()
    FlickrBackup.record_update_time()
    return None

def link_flickr_photos(basedir):
    # change into target directory
    # loop over each jpg/nef etc and find min/max dates from exif
    # retrieve list of photo ids from database within that date range - that do not have a disk file associated with them
    if os.path.exists(basedir):
        os.chdir(basedir)

    print "something"

    FlickrBackup.record_update_time()


def is_original(filename):
    """
    :param filename: name of file on disk to test
    :return: True if filename matches an 'original' format

    Digital cameras still write original files with a DOS 8.3 format which helps simplify the regex.
    """
    original = re.compile('^(dsc|img)\w\d{4}\.(jpg|nef|arw)$', re.IGNORECASE)
    return True if original.match(filename) else False


def get_exif_date_and_dimensions(exif):
    return {tag: exif[exif_tag]
            for tag, exif_tag in zip(['date_taken', 'width', 'height'],
                                     [36867, 40962, 40963])}


def get_exif_info(exifdata):
    exif_info = get_exif_date_and_dimensions(exifdata)
    exif_info['date_taken'] = datetime.strptime(exif_info['date_taken'], "%Y:%m:%d %H:%M:%S")
    return exif_info


def read_image_details(filename):
    image = Image.open(filename)
    if hasattr(image, '_getexif'):
        return get_exif_info(image._getexif())
    else:
        print "Image", filename, "has no EXIF data"
        return None


def store_disk_photo_in_db(path, filename, original_filename):
    input_data = {'path': path, 'filename': filename, 'original_filename': original_filename}
    db = FlickrBackup.get_database_connection()
    c = db.cursor()
    c.execute('''select id from disk_photo where filename = :fname''', {'fname': filename})
    results = c.fetchone()
    if results is None:
        print "Inserting disk file info into database"
        c.execute('''insert into disk_photo(drive, path, filename, original_filename)
                    values("", :path, :filename, :original_filename)''', input_data)
    else:
        print "Updating existing entry for disk file", filename
        input_data['id'] = results[0]
        c.execute('''update disk_photo set path = :path, filename = :filename, original_filename = :original_filename
                    where id = :id''', input_data)
    db.commit()
    return None


def search_db_for_photo(params):
    date_taken = datetime.strptime(params['date_taken'], "%Y:%m:%d %H:%M:%S")
    db = FlickrBackup.get_database_connection()
    c = db.cursor()
    c.execute('''select id from flickr_photo where date_taken = :dt and width = :width and height = :height''',
              {'dt': date_taken, 'width': params['width'], 'height': params['height']})
#    c.execute('''select id from flickr_photo where date_taken = :dt ''',
#              {'dt': date_taken})
    results = c.fetchall()
    db.close()
    return results


def find_original(dirfile):
    return ""


def read_photo_dates(imagefiles):
    image_details = {}
    for imagefile in imagefiles:
        image_details[imagefile] = read_image_details(imagefile)
    return image_details


def get_date_range(image_details):
    start_date = datetime.today()
    end_date = datetime.fromtimestamp(1)
    for imagefile in image_details:
        if image_details[imagefile]['date_taken'] > end_date:
            end_date = image_details[imagefile]['date_taken']
        if image_details[imagefile]['date_taken'] < start_date:
            start_date = image_details[imagefile]['date_taken']
    return start_date, end_date


def get_photos_in_date_range(start, end):
    db = FlickrBackup.get_database_connection()
    c = db.cursor()
    c.execute('''select id from flickr_photo where date_taken between :start and :end''',
              {'start': start, 'end': end})
    results = c.fetchall()
    db.close()
    return [id[0] for id in results]


def is_original_jpg(filename):
    return True if filename.lower().endswith("jpg") else False


def thing():
    for (a,b,c) in os.walk(os.getcwd()):
        print "Current directory =", a
#    print "Subdirectories:"
#    pprint.pprint(b)
#    print "Files:"
#    pprint.pprint(c)
        originals = []
        flickr_photos = {}
        flickr_matches = {}
        print "Files:"
        for dirfile in c:
            if is_original(dirfile):
                originals.append(dirfile)
            if dirfile.endswith(".jpg") or dirfile.endswith(".JPG"):
                photo_id = search_db_for_photo(read_image_details(dirfile))
                if len(photo_id) > 0:
                    print "Found Flickr photo for", dirfile, "with id =", photo_id[0][0]
                    original_filename = find_original(dirfile)
#                    store_disk_photo_in_db(a, dirfile, original_filename)
                else:
                    print "No Flickr photo for", dirfile
#    test_original()
