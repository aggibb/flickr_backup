import os
import flickrapi
import ConfigParser
import webbrowser
import FlickrBackup


def authenticate_flickr_access(flickr):
    if not flickr.token_valid(perms=u'read'):
        print "Now we need to approve read-only access to your Flickr account"
        flickr.get_request_token(oauth_callback='oob')
        authorize_url = flickr.auth_url(perms=u'read')
        webbrowser.open_new_tab(authorize_url)
        verifier = unicode(str(raw_input('Enter the verifier code from Flickr: ')), 'utf-8')
        flickr.get_access_token(verifier)
    return


def request_api_key_and_secret_from_user():
    print "To continue, you'll need to enter an API key and secret from Flickr"
    key = str(raw_input('Enter Flickr API key: '))
    secret = str(raw_input('Enter Flickr API secret: '))
    return key, secret


def write_api_key_and_secret_to_config(flickr_cfg):
    (api_key, api_secret) = request_api_key_and_secret_from_user()
    config = ConfigParser.RawConfigParser()
    config_section = 'flickr_backup'
    config.add_section(config_section)
    config.set(config_section, 'key', api_key)
    config.set(config_section, 'secret', api_secret)
    with open(flickr_cfg, 'wb') as config_file:
        config.write(config_file)


def get_flickr_backup_config():
    flickr_dir = FlickrBackup.get_backup_directory()
    if not os.path.exists(flickr_dir):
        os.mkdir(flickr_dir)
    flickr_cfg = os.path.join(flickr_dir, 'flickr_backup.ini')
    if not os.path.exists(flickr_cfg):
        write_api_key_and_secret_to_config(flickr_cfg)
    return flickr_cfg


def get_api_key_and_secret():
    flickr_config_file = get_flickr_backup_config()
    flickr_config = ConfigParser.ConfigParser()
    flickr_config.read(flickr_config_file)
    app_key = flickr_config.get('flickr_backup', 'key')
    app_secret = flickr_config.get('flickr_backup', 'secret')
    return app_key, app_secret


def create_flickrapi_object():
    app_key, app_secret = get_api_key_and_secret()
    flickr = flickrapi.FlickrAPI(app_key, app_secret, format="parsed-json")
    authenticate_flickr_access(flickr)
    return flickr
