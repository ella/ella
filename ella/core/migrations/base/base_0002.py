
from south.db import db
from django.db import models
from django.utils.datastructures import SortedDict
from django.conf import settings

def alter_foreignkey_to_int(table, field, null=True):
    '''
    real alter foreignkeyField to integerField
    with all constraint deletion
    '''
    if null:
        int_field = models.IntegerField(null=True, blank=True)
    else:
        int_field = models.IntegerField()
    fk_field = '%s_id' % field
    db.alter_column(table, fk_field, int_field)
    db.rename_column(table, fk_field, field)
    # i think it is because of constraint deletion
    db.add_column(table, fk_field, int_field)
    db.delete_column(table, fk_field)
    #db.delete_index(table, [fk_field])

def migrate_foreignkey(app_label, model, table, field, orm, null=False):
    s = {
        'app_label': app_label,
        'model': model,
        'table': table,
        'field': field,
        'fk_field': '%s_id' % field,
    }
    db.execute('''
        UPDATE
            `%(table)s` tbl
            JOIN `core_publishable` pub ON (tbl.`%(field)s` = pub.`old_id`)
            JOIN `django_content_type` ct ON (pub.`content_type_id` = ct.`id` AND ct.`app_label` = '%(app_label)s' AND ct.`model` = '%(model)s')
        SET
            tbl.`%(field)s` = pub.`id`;
        ''' % s
    )
    db.rename_column(s['table'], s['field'], s['fk_field'])
    if null:
        fk = models.ForeignKey(orm['%(app_label)s.%(model)s' % s], null=True, blank=True)
    else:
        fk = models.ForeignKey(orm['%(app_label)s.%(model)s' % s])
    db.alter_column(s['table'], s['fk_field'], fk)

    target_table = ('%s_%s' % (app_label, model)).lower()

    #  make it a FK
    db.execute(
        'ALTER TABLE `%s` ADD CONSTRAINT `%s_refs_publishable_ptr_id_%s` FOREIGN KEY (`%s`) REFERENCES `%s` (`publishable_ptr_id`);' % (
            table,
            s['fk_field'],
            abs(hash((table, target_table))),
            s['fk_field'],
            target_table
        )
    )


class BasePublishableDataMigration:
    depends_on = (
        ('core', '0002_02_publishable_columns'),
    )
    run_before = (
        ('core', '0002_03_move_publishable_data'),
    )

    models = {
        'core.publishable': {
            'Meta': {'app_label': "'core'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
    }

    app_label = ''
    model = ''
    table = '%s_%s' % (app_label, model)
    publishable_uncommon_cols = {}

    def alter_self_foreignkeys(self, orm):
        '''
        alter and migrate all tables that has foreign keys to this model
        '''
        # drop foreign key constraint from intermediate table
        alter_foreignkey_to_int('%s_authors' % self.table, self.model)

    def move_self_foreignkeys(self, orm):
        '''
        alter all data from tables that has foreign keys to this model
        '''
        # update authors
        db.execute('''
            INSERT INTO
                `core_publishable_authors` (`publishable_id`, `author_id`)
            SELECT
                art.`publishable_ptr_id`, art_aut.`author_id`
            FROM
                `%(table)s` art INNER JOIN `%(table)s_authors` art_aut ON (art.`id` = art_aut.`%(model)s`);
            ''' % self.substitute
        )
        db.delete_table('%s_authors' % self.table)

    @property
    def publishable_cols(self):
        c = {
            'title': 'title',
            'slug': 'slug',
            'category_id': 'category_id',
            'photo_id': 'photo_id',
        }
        c.update(self.publishable_uncommon_cols)
        return SortedDict(c)

    @property
    def substitute(self):
        return {
            'app_label': self.app_label,
            'model': self.model,
            'table': self.table,
            'cols_to': ', '.join(self.cols_to),
            'cols_from': ', '.join(['a.`%s`' % c for c in self.cols_from]),
        }

    @property
    def cols_to(self):
        return self.publishable_cols.keys()

    @property
    def cols_from(self):
        return self.publishable_cols.values()

    @property
    def generic_relations(self):
        # TODO find better way then this hardcoded...
        # TODO: this should be solved via plugins
        keys = ('table', 'ct_id', 'obj_id', 'unique_keys')
        gens = []
        if 'tagging' in settings.INSTALLED_APPS:
            gens.append(('tagging_taggeditem', 'content_type_id', 'object_id', ('tag_id','content_type_id','object_id')))
        if 'ella.oldcomments' in settings.INSTALLED_APPS:
            gens.append(('comments_comment', 'target_ct_id', 'target_id', None))
        if 'ella.positions' in settings.INSTALLED_APPS:
            gens.append(('positions_position', 'target_ct_id', 'target_id', None))
        if 'ella.ratings' in settings.INSTALLED_APPS:
            gens.append(('ratings_totalrate', 'target_ct_id', 'target_id', None))
            gens.append(('ratings_agg', 'target_ct_id', 'target_id', None))
            gens.append(('ratings_rating', 'target_ct_id', 'target_id', None))

        return [dict(zip(keys, v)) for v in gens]

    def backwards(self, orm):
        pass

    def forwards(self, orm):
        print "Old data migration is disabled"
        # migrate publishables
        self.forwards_publishable(orm)
        # migrate generic relations
#        self.forwards_generic_relations(orm)
        # migrate placements
#        self.forwards_placements(orm)
        # migrate related
#        self.forwards_related(orm)

    def forwards_publishable(self, orm):
        '''
        creation of publishable objects

        TODO: sync publish_from
        '''

        # move the data
#        db.execute('''
#            INSERT INTO
#                `core_publishable` (old_id, content_type_id, %(cols_to)s)
#            SELECT
#                a.id, ct.id, %(cols_from)s
#            FROM
#                `%(table)s` a, `django_content_type` ct
#            WHERE
#                ct.`app_label` = '%(app_label)s' AND  ct.`model` = '%(model)s';
#            ''' % self.substitute
#        )

        # add link to parent
        db.add_column(self.table, 'publishable_ptr', models.IntegerField(null=True, blank=True))

        # update the link
#        db.execute('''
#            UPDATE
#                `core_publishable` pub
#                JOIN `%(table)s` art ON (art.`id` = pub.`old_id`)
#                JOIN `django_content_type` ct ON (pub.`content_type_id` = ct.`id` AND ct.`app_label` = '%(app_label)s' AND ct.`model` = '%(model)s')
#            SET
#                art.`publishable_ptr` = pub.`id`;
#            ''' % self.substitute
#        )

        # remove constraints from all models reffering to us
#        self.alter_self_foreignkeys(orm)

        # drop primary key
        db.alter_column(self.table, 'id', models.IntegerField())
        db.drop_primary_key(self.table)

        # replace it with a link to parent
        db.rename_column(self.table, 'publishable_ptr', 'publishable_ptr_id')
        db.alter_column(self.table, 'publishable_ptr_id', models.ForeignKey(orm['core.Publishable'], unique=True))
        db.create_primary_key(self.table, 'publishable_ptr_id')

        #  make it a FK
#        db.execute(
#            'ALTER TABLE `%s` ADD CONSTRAINT `publishable_ptr_id_refs_id_%s` FOREIGN KEY (`publishable_ptr_id`) REFERENCES `core_publishable` (`id`);' % (
#                self.table,
#                abs(hash((self.table, 'core_publishable'))),
#            )
#        )

        # move data, that were pointing to us
#        self.move_self_foreignkeys(orm)

        # drop duplicate columns
        db.delete_column(self.table, 'id')
        for column in self.cols_from:
            db.delete_column(self.table, column)

    def forwards_generic_relations(self, orm):
        '''
        Updates all generic relations
        '''
        for gen in self.generic_relations:
            sub = dict.copy(self.substitute)
            sub.update(gen)
            if gen['unique_keys']:
                db.delete_unique(gen['table'], gen['unique_keys'])
            db.execute('''
                UPDATE
                    `%(table)s` gen
                    JOIN `core_publishable` pub ON (gen.`%(ct_id)s` = pub.`content_type_id` AND gen.`%(obj_id)s` = pub.`old_id`)
                    JOIN `django_content_type` ct ON (pub.`content_type_id` = ct.`id` AND ct.`app_label` = '%(app_label)s' AND  ct.`model` = '%(model)s')
                SET
                    gen.`%(obj_id)s` = pub.`id`;
            ''' % sub)
            if gen['unique_keys']:
                db.create_unique(gen['table'], gen['unique_keys'])

    def forwards_placements(self, orm):
        '''
        migrate placements
        '''
        db.execute('''
            UPDATE
                `core_placement` plac
                JOIN `core_publishable` pub ON (plac.`target_ct_id` = pub.`content_type_id` AND plac.`target_id` = pub.`old_id`)
                JOIN `django_content_type` ct ON (pub.`content_type_id` = ct.`id` AND ct.`app_label` = '%(app_label)s' AND  ct.`model` = '%(model)s')
            SET
                plac.`publishable_id` = pub.`id`;
            ''' % self.substitute
        )

    def forwards_related(self, orm):
        pass

