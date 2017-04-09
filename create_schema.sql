create table flickr_photo (
    id integer primary key not null,
    secret text,
    original_secret text,
    server integer,
    farm integer,
    privacy integer,
    date_taken datetime,
    date_uploaded datetime,
    last_update datetime,
    media text,
    url_o text,
    width integer,
    height integer,
    title text,
    description text,
    geo_id integer references geotag(id),
    disk_id integer references disk_photo(id)
);

create table disk_photo (
    id integer primary key,
    drive text,
    path text,
    filename text,
    original_filename text,
    original_jpg integer,
    original_raw text
);

create table geotag (
    id integer primary key not null,
    longitude real,
    latitude real,
    accuracy integer
);

create table flickr_user (
    id integer primary key not null,
    nsid text not null,
    username text not null,
    fullname text not null,
    last_update datetime
);
