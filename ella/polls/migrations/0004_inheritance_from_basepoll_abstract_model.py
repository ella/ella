
from south.db import db
from django.db import models
from ella.polls.models import *
import datetime

class Migration:

    def forwards(self, orm):

        """
        Poll
          * changing fields defined by BasePoll abstract model
        """

        # Changing field 'Poll.text'
        db.alter_column('polls_poll', 'text', models.TextField(_('Text')))

        # Adding field 'Poll.active_from'
        db.alter_column('polls_poll', 'active_from', models.DateTimeField(_('Active from'), blank=True, null=True))

        # Changing field 'Poll.active_till'
        db.alter_column('polls_poll', 'active_till', models.DateTimeField(_('Active till'), blank=True, null=True))

        # Changing field 'Poll.text_results'
        db.alter_column('polls_poll', 'text_results', models.TextField(_('Text with results')))

        # Changing field 'Poll.text_announcement'
        db.alter_column('polls_poll', 'text_announcement', models.TextField(_('Text with announcement')))

        # Changing field 'Poll.active_from'
        db.alter_column('polls_poll', 'active_from', models.DateTimeField(_('Active from')))


        """
        Contest
          * inheritance from Publishable - will be done by other migration
        """
        # Changing field 'Quiz.text_announcement'
        db.add_column('polls_contest', 'text_announcement', models.TextField(_('Text with announcement')))

        # Adding field 'Contest.active_from'
        db.alter_column('polls_contest', 'active_from', models.DateTimeField(_('Active from'), blank=True, null=True))

        # Adding field 'Contest.active_till'
        db.alter_column('polls_contest', 'active_till', models.DateTimeField(_('Active till'), blank=True, null=True))



        """
        Quiz
          * changing fields defined by BasePoll abstract model
          * inheritance from Publishable - will be done by other migration
        """

        # Changing field 'Quiz.text_announcement'
        db.add_column('polls_quiz', 'text_announcement', models.TextField(_('Text with announcement')))

        # Adding field 'Quiz.active_from'
        db.alter_column('polls_quiz', 'active_from', models.DateTimeField(_('Active from'), blank=True, null=True))

        # Adding field 'Quiz.active_till'
        db.alter_column('polls_quiz', 'active_till', models.DateTimeField(_('Active till'), blank=True, null=True))



    def backwards(self, orm):

        """
        Poll
          * fields defined by BasePoll abstract model
        """

        # Changing field 'Poll.text'
        db.alter_column('polls_poll', 'text', models.TextField(_('Text'), null=True, blank=True))

        # Changing field 'Poll.active_till'
        db.alter_column('polls_poll', 'active_till', models.DateTimeField(_('Active till'), null=True, blank=True))

        # Changing field 'Poll.text_results'
        db.alter_column('polls_poll', 'text_results', models.TextField(_('Text with results'), null=True, blank=True))

        # Changing field 'Poll.text_announcement'
        db.alter_column('polls_poll', 'text_announcement', models.TextField(_('Text with announcement'), null=True, blank=True))

        # Changing field 'Poll.active_from'
        db.alter_column('polls_poll', 'active_from', models.DateTimeField(_('Active from'), default=datetime.datetime.now, null=True, blank=True))


        """
        Contest
          * inheritance from Publishable - will be done by other migration
        """

        # Changing field 'Contest.text_announcement'
        db.alter_column('polls_contest', 'text_announcement', models.TextField(_('text with announcement')))

        # Deleting field 'Contest.publishable_ptr'
        #db.delete_column('polls_contest', 'publishable_ptr_id')

        # Adding field 'Contest.category'
        #db.add_column('polls_contest', 'category', models.ForeignKey(orm['core.Category']))

        # Adding field 'Contest.id'
        #db.add_column('polls_contest', 'id', models.AutoField(primary_key=True))

        # Adding field 'Contest.photo'
        #db.add_column('polls_contest', 'photo', models.ForeignKey(orm['photos.Photo']))

        # Adding field 'Contest.slug'
        #db.add_column('polls_contest', 'slug', models.SlugField(_('Slug'), max_length=255))

        # Adding field 'Contest.title'
        #db.add_column('polls_contest', 'title', models.CharField(_('Title'), max_length=200))


        """
        Quiz
          * changing fields defined by BasePoll abstract model
          * inheritance from Publishable - will be done by other migration
        """

        # Changing field 'Quiz.text_announcement'
        db.alter_column('polls_quiz', 'text_announcement', models.TextField(_('text with announcement')))

        # Deleting field 'Quiz.publishable_ptr'
        #db.delete_column('polls_quiz', 'publishable_ptr_id')

        # Adding field 'Quiz.title'
        #db.add_column('polls_quiz', 'title', models.CharField(_('title'), max_length=200))

        # Adding field 'Quiz.slug'
        #db.add_column('polls_quiz', 'slug', models.SlugField(_('Slug'), max_length=255))

        # Adding field 'Quiz.photo'
        #db.add_column('polls_quiz', 'photo', models.ForeignKey(orm['photos.Photo']))

        # Adding field 'Quiz.category'
        #db.add_column('polls_quiz', 'category', models.ForeignKey(orm['core.Category']))

        # Adding field 'Quiz.id'
        #db.add_column('polls_quiz', 'id', models.AutoField(primary_key=True))

        # Adding ManyToManyField 'Quiz.authors'
        #db.create_table('polls_quiz_authors', (
        #    ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
        #    ('quiz', models.ForeignKey(orm.Quiz, null=False)),
        #    ('author', models.ForeignKey(orm['core.author'], null=False))
        #))



    models = {}

    """
    models = {
        'core.category': {
            'Meta': {'ordering': "('site','tree_path',)", 'unique_together': "(('site','tree_path'),)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'polls.choice': {
            'choice': ('models.TextField', ["_('Choice text')"], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'points': ('models.IntegerField', ["_('Points')"], {'null': 'True', 'blank': 'False'}),
            'question': ('models.ForeignKey', ["orm['polls.Question']"], {'verbose_name': "_('Question')"}),
            'votes': ('models.IntegerField', ["_('Votes')"], {'null': 'True', 'blank': 'True'})
        },
        'auth.user': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'polls.contest': {
            'Meta': {'ordering': "('-active_from',)", '_bases': ['ella.core.models.publishable.Publishable']},
            'active_from': ('models.DateTimeField', ["_('Active from')"], {}),
            'active_till': ('models.DateTimeField', ["_('Active till')"], {}),
            'publishable_ptr': ('models.OneToOneField', ["orm['core.Publishable']"], {}),
            'text': ('models.TextField', ["_('Text')"], {}),
            'text_announcement': ('models.TextField', ["_('Text with announcement')"], {}),
            'text_results': ('models.TextField', ["_('Text with results')"], {})
        },
        'polls.vote': {
            'Meta': {'ordering': "('-time',)"},
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('models.IPAddressField', ["_('IP Address')"], {'null': 'True'}),
            'poll': ('models.ForeignKey', ["orm['polls.Poll']"], {'verbose_name': "_('Poll')"}),
            'time': ('models.DateTimeField', ["_('Time')"], {'auto_now': 'True'}),
            'user': ('models.ForeignKey', ["orm['auth.User']"], {'null': 'True', 'verbose_name': "_('User')", 'blank': 'True'})
        },
        'polls.result': {
            'count': ('models.IntegerField', ["_('Count')"], {'null': 'False', 'blank': 'False'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'points_from': ('models.IntegerField', ["_('Points dimension from')"], {'null': 'True'}),
            'points_to': ('models.IntegerField', ["_('Points dimension to')"], {'null': 'True'}),
            'quiz': ('models.ForeignKey', ["orm['polls.Quiz']"], {'verbose_name': "_('Quiz')"}),
            'text': ('models.TextField', ["_('Quiz results text')"], {}),
            'title': ('models.CharField', ["_('Title')"], {'max_length': '200', 'blank': 'True'})
        },
        'polls.question': {
            'allow_multiple': ('models.BooleanField', ["_('Allow multiple choices')"], {'default': 'False'}),
            'allow_no_choice': ('models.BooleanField', ["_('Allow no choice')"], {'default': 'False'}),
            'contest': ('models.ForeignKey', ["orm['polls.Contest']"], {'null': 'True', 'verbose_name': "_('Contest')", 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'question': ('models.TextField', ["_('Question text')"], {}),
            'quiz': ('models.ForeignKey', ["orm['polls.Quiz']"], {'null': 'True', 'verbose_name': "_('Quiz')", 'blank': 'True'})
        },
        'polls.poll': {
            'Meta': {'ordering': "('-active_from',)"},
            'active_from': ('models.DateTimeField', ["_('Active from')"], {}),
            'active_till': ('models.DateTimeField', ["_('Active till')"], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'question': ('models.ForeignKey', ["orm['polls.Question']"], {'unique': 'True', 'verbose_name': "_('Question')"}),
            'text': ('models.TextField', ["_('Text')"], {}),
            'text_announcement': ('models.TextField', ["_('Text with announcement')"], {}),
            'text_results': ('models.TextField', ["_('Text with results')"], {}),
            'title': ('models.CharField', ["_('Title')"], {'max_length': '200'})
        },
        'core.publishable': {
            'Meta': {'app_label': "'core'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label','model'),)", 'db_table': "'django_content_type'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'photos.photo': {
            'Meta': {'ordering': "('-created',)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'core.source': {
            'Meta': {'app_label': "'core'"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'core.author': {
            'Meta': {'ordering': "('name','slug',)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'polls.quiz': {
            'Meta': {'ordering': "('-active_from',)", '_bases': ['ella.core.models.publishable.Publishable']},
            'active_from': ('models.DateTimeField', ["_('Active from')"], {}),
            'active_till': ('models.DateTimeField', ["_('Active till')"], {}),
            'has_correct_answers': ('models.BooleanField', ["_('Has correct answers')"], {}),
            'publishable_ptr': ('models.OneToOneField', ["orm['core.Publishable']"], {}),
            'text': ('models.TextField', ["_('Text')"], {}),
            'text_announcement': ('models.TextField', ["_('Text with announcement')"], {}),
            'text_results': ('models.TextField', ["_('Text with results')"], {})
        },
        'polls.contestant': {
            'Meta': {'ordering': "('-datetime',)", 'unique_together': "(('contest','email',),)"},
            'address': ('models.CharField', ["_('Address')"], {'max_length': '200', 'blank': 'True'}),
            'choices': ('models.TextField', ["_('Choices')"], {'blank': 'True'}),
            'contest': ('models.ForeignKey', ["orm['polls.Contest']"], {'verbose_name': "_('Contest')"}),
            'count_guess': ('models.IntegerField', ["_('Count guess')"], {}),
            'datetime': ('models.DateTimeField', ["_('Date and time')"], {'auto_now_add': 'True'}),
            'email': ('models.EmailField', ["_('email')"], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', ["_('First name')"], {'max_length': '200'}),
            'phonenumber': ('models.CharField', ["_('Phone number')"], {'max_length': '20', 'blank': 'True'}),
            'surname': ('models.CharField', ["_('Last name')"], {'max_length': '200'}),
            'user': ('models.ForeignKey', ["orm['auth.User']"], {'null': 'True', 'verbose_name': "_('User')", 'blank': 'True'}),
            'winner': ('models.BooleanField', ["_('Winner')"], {'default': 'False'})
        }
    }
    """

    complete_apps = ['polls']
