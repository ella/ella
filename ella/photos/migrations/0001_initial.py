
from south.db import db
from django.db import models
import datetime
from south.v2 import SchemaMigration

class Migration(SchemaMigration):

    depends_on = (
        ("core", "0001_initial"),
    )

    def forwards(self, orm):

        # Adding model 'Photo'
        db.create_table('photos_photo', (
            ('id', models.AutoField(primary_key=True)),
            ('title', models.CharField(_('Title'), max_length=200)),
            ('description', models.TextField(_('Description'), blank=True)),
            ('slug', models.SlugField(_('Slug'), max_length=255)),
            ('image', models.ImageField(height_field='height', width_field='width')),
            ('width', models.PositiveIntegerField(editable=False)),
            ('height', models.PositiveIntegerField(editable=False)),
            ('source', models.ForeignKey(orm['core.Source'], null=True, verbose_name=_('Source'), blank=True)),
            ('created', models.DateTimeField(default=datetime.datetime.now, editable=False)),
        ))
        db.send_create_signal('photos', ['Photo'])

        # Adding model 'FormatedPhoto'
        db.create_table('photos_formatedphoto', (
            ('id', models.AutoField(primary_key=True)),
            ('photo', models.ForeignKey(orm.Photo)),
            ('format', models.ForeignKey(orm.Format)),
            ('filename', models.CharField(max_length=300, editable=False)),
            ('crop_left', models.PositiveIntegerField()),
            ('crop_top', models.PositiveIntegerField()),
            ('crop_width', models.PositiveIntegerField()),
            ('crop_height', models.PositiveIntegerField()),
            ('width', models.PositiveIntegerField(editable=False)),
            ('height', models.PositiveIntegerField(editable=False)),
        ))
        db.send_create_signal('photos', ['FormatedPhoto'])

        # Adding model 'Format'
        db.create_table('photos_format', (
            ('id', models.AutoField(primary_key=True)),
            ('name', models.CharField(_('Name'), max_length=80)),
            ('max_width', models.PositiveIntegerField(_('Max width'))),
            ('max_height', models.PositiveIntegerField(_('Max height'))),
            ('flexible_height', models.BooleanField(_('Flexible height'))),
            ('flexible_max_height', models.PositiveIntegerField(_('Flexible max height'), null=True, blank=True)),
            ('stretch', models.BooleanField(_('Stretch'))),
            ('nocrop', models.BooleanField(_('Do not crop'))),
            ('resample_quality', models.IntegerField(_('Resample quality'), default=85)),
            ('site', models.ForeignKey(orm['sites.Site'])),
        ))
        db.send_create_signal('photos', ['Format'])

        # Adding ManyToManyField 'Photo.authors'
        db.create_table('photos_photo_authors', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('photo', models.ForeignKey(orm.Photo, null=False)),
            ('author', models.ForeignKey(orm['core.Author'], null=False))
        ))

        # Creating unique_together for [photo, format] on FormatedPhoto.
        db.create_unique('photos_formatedphoto', ['photo_id', 'format_id'])



    def backwards(self, orm):

        # Deleting model 'Photo'
        db.delete_table('photos_photo')

        # Deleting model 'FormatedPhoto'
        db.delete_table('photos_formatedphoto')

        # Deleting model 'Format'
        db.delete_table('photos_format')

        # Dropping ManyToManyField 'Photo.authors'
        db.delete_table('photos_photo_authors')

        # Deleting unique_together for [photo, format] on FormatedPhoto.
        db.delete_unique('photos_formatedphoto', ['photo_id', 'format_id'])



    models = {
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'db_table': "'django_site'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'photos.formatedphoto': {
            'Meta': {'unique_together': "(('photo','format'),)"},
            'crop_height': ('models.PositiveIntegerField', [], {}),
            'crop_left': ('models.PositiveIntegerField', [], {}),
            'crop_top': ('models.PositiveIntegerField', [], {}),
            'crop_width': ('models.PositiveIntegerField', [], {}),
            'filename': ('models.CharField', [], {'max_length': '300', 'editable': 'False'}),
            'format': ('models.ForeignKey', ["orm['photos.Format']"], {}),
            'height': ('models.PositiveIntegerField', [], {'editable': 'False'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'photo': ('models.ForeignKey', ["orm['photos.Photo']"], {}),
            'width': ('models.PositiveIntegerField', [], {'editable': 'False'})
        },
        'photos.photo': {
            'Meta': {'ordering': "('-created',)"},
            'authors': ('models.ManyToManyField', ["orm['core.Author']"], {'related_name': "'photo_set'", 'verbose_name': "_('Authors')"}),
            'created': ('models.DateTimeField', [], {'default': 'datetime.datetime.now', 'editable': 'False'}),
            'description': ('models.TextField', ["_('Description')"], {'blank': 'True'}),
            'height': ('models.PositiveIntegerField', [], {'editable': 'False'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'image': ('models.ImageField', [], {'height_field': "'height'", 'width_field': "'width'"}),
            'slug': ('models.SlugField', ["_('Slug')"], {'max_length': '255'}),
            'source': ('models.ForeignKey', ["orm['core.Source']"], {'null': 'True', 'verbose_name': "_('Source')", 'blank': 'True'}),
            'title': ('models.CharField', ["_('Title')"], {'max_length': '200'}),
            'width': ('models.PositiveIntegerField', [], {'editable': 'False'})
        },
        'photos.format': {
            'Meta': {'ordering': "('name','-max_width',)"},
            'flexible_height': ('models.BooleanField', ["_('Flexible height')"], {}),
            'flexible_max_height': ('models.PositiveIntegerField', ["_('Flexible max height')"], {'null': 'True', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'max_height': ('models.PositiveIntegerField', ["_('Max height')"], {}),
            'max_width': ('models.PositiveIntegerField', ["_('Max width')"], {}),
            'name': ('models.CharField', ["_('Name')"], {'max_length': '80'}),
            'nocrop': ('models.BooleanField', ["_('Do not crop')"], {}),
            'resample_quality': ('models.IntegerField', ["_('Resample quality')"], {'default': '85'}),
            'site': ('models.ForeignKey', ["orm['sites.Site']"], {}),
            'stretch': ('models.BooleanField', ["_('Stretch')"], {})
        },
        'core.source': {
            'Meta': {'ordering': "('name',)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'core.author': {
            'Meta': {'ordering': "('name','slug',)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['photos']
