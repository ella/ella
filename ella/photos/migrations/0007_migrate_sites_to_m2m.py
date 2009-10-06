
from south.db import db
from django.db import models
from ella.photos.models import *

FORMAT_FIELDS = (
    'max_width',
    'max_height',
    'flexible_height',
    'flexible_max_height',
    'stretch',
    'nocrop',
    'resample_quality',
)

class Migration:
    
    def forwards(self, orm):
        result = db.execute('''
            SELECT
                name,
                id,
                site_id,
                %s
            FROM
                photos_format
            ''' % ', '.join(FORMAT_FIELDS) )
        rows = result
        formats = {}

        # collect all formats in dictionary:
        # {name:
        #   {
        #       (FORMAT_FIELDS): [
        #           (id, site_id),
        #           ...
        #       ],
        #       ...
        #   },
        #   ...
        # }
        for row in rows:
            formats.setdefault(row[0], {}).setdefault(tuple(row[3:]), []).append((row[1], row[2]))

        for name, details in formats.items():
            for fields, ids in details.items():
                id = None
                for id_site in ids:
                    if id == None:
                        id = id_site[0]

                    db.execute('INSERT INTO photos_format_sites (format_id, site_id) VALUES (%s, %s)', (id, id_site[1]))

                    if id != id_site[0]:
                        db.execute('DELETE FROM photos_formatedphoto WHERE format_id = %s', (id_site[0],))
                        db.execute('DELETE FROM photos_format WHERE id = %s', (id_site[0],))
    
    def backwards(self, orm):
        "Write your backwards migration here"

        result = db.execute('SELECT id FROM photos_format')
        for row in result:
            id = row[0]
            # take the first site for every format...
            min_site = db.execute('SELECT MIN(site_id) FROM photos_format_sites WHERE format_id = %s', (id, ))[0]

            # ... put it onto the format ...
            db.execute('UPDATE photos_format SET site_id = %s WHERE id = %s', (min_site, id, ))

            # ... and remove the site from the m2m
            db.execute('DELETE FROM photos_format_sites WHERE format_id = %s AND site_id = %s', (id, site_id, ))

        # copy all the remaining sites from m2m to format as new rows
        db.execute('''
            INSERT INTO
                photos_format 
                (site_id, name, %s)
            SELECT
                pfs.site_id, pf.name, %s
            FROM
                photos_format as pf INNER JOIN photos_format_sites as pfs ON (pfs.format_id = pf.id)
            ''' % (
                ', '.join(FORMAT_FIELDS),
                ', '.join(map(lambda f: 'pf.'+f, FORMAT_FIELDS))
            )
        )
        
        # DELETE formats with no site
        db.execute('DELETE FROM photos_format WHERE site_id IS NULL')
    
