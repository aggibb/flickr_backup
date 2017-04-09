## flickr_backup: a collection of tools for backing up photo details from Flickr

I've been using Flickr for over a decade now and have uploaded some 14000+ photos. As part of my efforts to keep my Flickr account in sync with my local photo collection, I decided to conjure up some command-line tools for linking the two. This is my first step: just keeping a record of what I have on Flickr. My goal is to link this database with the actual files on disk to make it easier to replace photos, and to create local versions of Flickr sets and collections.

### What it does

The core of this collection stores a local copy of the photo details as stored on Flickr in a SQLite database. Currently, tools exist to:
* set up the database (and get Flickr access);
* backup the photo details for your entire photostream;
* update an existing back with new details.

Authentication with Flickr is handled with the `flickrapi` module, which stores credentials in its own SQLite database in the `~/.flickr` directory. This collection kinda piggy-backs on that and also stores its database (along with the Flickr access key and secret) in the same location. Respectively, these files are called `flickr_backup.sqlite` and `flickr_backup.ini`.

### Stored information

The backup contains information relevant to the original photo (such as creation date/time, pixel dimensions) along with information that Flickr creates and stores itself (such as an ID, server farm ID, URL to the photo, upload and modified dates) and any user-defined data (e.g. title, description, privacy settings). Geolocation data are stored if present.

Notes are not stored at this time.

As part of the authentication process, your Flickr username, NSID, and full name are also stored.

Take a look at `create_schema.sql` to get the full list of information stored in the database.

### Usage

The tools should be run in the order below.

#### setup_flickr_backup.py

Establishes the database and obtains Flickr authentication credentials. The user must provide a Flickr API key and secret when prompted.

#### flickr_backup.py

The main backup tool, `flickr_backup` retrieves photo details a single page (of 100 photos) at a time, reads the photo details, and stores them in the database, repeating this step until all photos have been backed up.

Options:

* `-n`, `--numpages` - number of "pages" of photos to store

* `-p`, `--pagenum` - specific page number to backup

These two options should be used in tandem if the backup is to be carried out in stages.

The date/time of last update is stored in the database.

#### update_flickr_backup.py

Checks for new or updated photos since the last backup, and stores the details in the database.

### Important note

This code does not provide any authentication credentials nor an API key/secret pair to access Flickr. You will need to obtain your own API key and secret from Flickr and enter these parameters when running the setup script. Do not give these to anyone else and don't commit them to a public repository, lest they be misused in your name.

The `flickrapi` module handles the authentication and redirects you to your favourite web browser to sign-in to Flickr and authorize (read-only) access for these tools.

#### Other notes

Right now these tools only work under a Unix-like environment.

No photos are downloaded: only the photo details. (Photo download will be a future addition.)

### Required Python modules

* `sqlite3`
* `flickrapi`: https://stuvel.eu/flickrapi

## License and copyright

This software is licensed under GPL-3.0+.

Copyright &copy; 2016-2017 [Andy Gibb](https://aggibb.github.io/)
