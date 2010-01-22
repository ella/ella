
from south.db import db
from django.db import models
from ella.polls.models import *
import datetime

class Migration:
    
    depends_on = (
        ("core", "0001_initial"),
        ("photos", "0001_initial"),
    )
 
    def forwards(self, orm):
        
        # Adding model 'Choice'
        db.create_table('polls_choice', (
            ('id', models.AutoField(primary_key=True)),
            ('question', models.ForeignKey(orm.Question, verbose_name=_('Question'))),
            ('choice', models.TextField(_('Choice text'))),
            ('points', models.IntegerField(_('Points'), null=True, blank=False)),
            ('votes', models.IntegerField(_('Votes'), null=True, blank=True)),
        ))
        db.send_create_signal('polls', ['Choice'])
        
        # Adding model 'Contest'
        db.create_table('polls_contest', (
            ('id', models.AutoField(primary_key=True)),
            ('title', models.CharField(_('Title'), max_length=200)),
            ('slug', models.SlugField(_('Slug'), max_length=255)),
            ('category', models.ForeignKey(orm['core.Category'])),
            ('text_announcement', models.TextField(_('Text with announcement'))),
            ('text', models.TextField(_('Text'))),
            ('text_results', models.TextField(_('Text with results'))),
            ('active_from', models.DateTimeField(_('Active from'))),
            ('active_till', models.DateTimeField(_('Active till'))),
            ('photo', models.ForeignKey(orm['photos.Photo'])),
        ))
        db.send_create_signal('polls', ['Contest'])
        
        # Adding model 'Vote'
        db.create_table('polls_vote', (
            ('id', models.AutoField(primary_key=True)),
            ('poll', models.ForeignKey(orm.Poll, verbose_name=_('Poll'))),
            ('user', models.ForeignKey(orm['auth.User'], null=True, verbose_name=_('User'), blank=True)),
            ('time', models.DateTimeField(_('Time'), auto_now=True)),
            ('ip_address', models.IPAddressField(_('IP Address'), null=True)),
        ))
        db.send_create_signal('polls', ['Vote'])
        
        # Adding model 'Result'
        db.create_table('polls_result', (
            ('id', models.AutoField(primary_key=True)),
            ('quiz', models.ForeignKey(orm.Quiz, verbose_name=_('Quiz'))),
            ('title', models.CharField(_('Title'), max_length=200, blank=True)),
            ('text', models.TextField(_('Quiz results text'))),
            ('points_from', models.IntegerField(_('Points dimension from'), null=True)),
            ('points_to', models.IntegerField(_('Points dimension to'), null=True)),
            ('count', models.IntegerField(_('Count'), null=False, blank=False)),
        ))
        db.send_create_signal('polls', ['Result'])
        
        # Adding model 'Question'
        db.create_table('polls_question', (
            ('id', models.AutoField(primary_key=True)),
            ('question', models.TextField(_('Question text'))),
            ('allow_multiple', models.BooleanField(_('Allow multiple choices'), default=False)),
            ('allow_no_choice', models.BooleanField(_('Allow no choice'), default=False)),
            ('quiz', models.ForeignKey(orm.Quiz, null=True, verbose_name=_('Quiz'), blank=True)),
            ('contest', models.ForeignKey(orm.Contest, null=True, verbose_name=_('Contest'), blank=True)),
        ))
        db.send_create_signal('polls', ['Question'])
        
        # Adding model 'Poll'
        db.create_table('polls_poll', (
            ('id', models.AutoField(primary_key=True)),
            ('title', models.CharField(_('Title'), max_length=200)),
            ('text_announcement', models.TextField(_('Text with announcement'), null=True, blank=True)),
            ('text', models.TextField(_('Text'), null=True, blank=True)),
            ('text_results', models.TextField(_('Text with results'), null=True, blank=True)),
            ('active_from', models.DateTimeField(_('Active from'), default=datetime.datetime.now, null=True, blank=True)),
            ('active_till', models.DateTimeField(_('Active till'), null=True, blank=True)),
            ('question', models.ForeignKey(orm.Question, unique=True, verbose_name=_('Question'))),
        ))
        db.send_create_signal('polls', ['Poll'])
        
        # Adding model 'Quiz'
        db.create_table('polls_quiz', (
            ('id', models.AutoField(primary_key=True)),
            ('title', models.CharField(_('title'), max_length=200)),
            ('slug', models.SlugField(_('Slug'), max_length=255)),
            ('category', models.ForeignKey(orm['core.Category'])),
            ('text_announcement', models.TextField(_('text with announcement'))),
            ('text', models.TextField(_('Text'))),
            ('text_results', models.TextField(_('Text with results'))),
            ('active_from', models.DateTimeField(_('Active from'))),
            ('active_till', models.DateTimeField(_('Active till'))),
            ('photo', models.ForeignKey(orm['photos.Photo'])),
            ('has_correct_answers', models.BooleanField(_('Has correct answers'))),
        ))
        db.send_create_signal('polls', ['Quiz'])
        
        # Adding model 'Contestant'
        db.create_table('polls_contestant', (
            ('id', models.AutoField(primary_key=True)),
            ('contest', models.ForeignKey(orm.Contest, verbose_name=_('Contest'))),
            ('datetime', models.DateTimeField(_('Date and time'), auto_now_add=True)),
            ('user', models.ForeignKey(orm['auth.User'], null=True, verbose_name=_('User'), blank=True)),
            ('name', models.CharField(_('First name'), max_length=200)),
            ('surname', models.CharField(_('Last name'), max_length=200)),
            ('email', models.EmailField(_('email'))),
            ('phonenumber', models.CharField(_('Phone number'), max_length=20, blank=True)),
            ('address', models.CharField(_('Address'), max_length=200, blank=True)),
            ('choices', models.TextField(_('Choices'), blank=True)),
            ('count_guess', models.IntegerField(_('Count guess'))),
            ('winner', models.BooleanField(_('Winner'), default=False)),
        ))
        db.send_create_signal('polls', ['Contestant'])
        
        # Adding ManyToManyField 'Quiz.authors'
        db.create_table('polls_quiz_authors', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('quiz', models.ForeignKey(orm.Quiz, null=False)),
            ('author', models.ForeignKey(orm['core.Author'], null=False))
        ))
        
        # Creating unique_together for [contest, email] on Contestant.
        db.create_unique('polls_contestant', ['contest_id', 'email'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Choice'
        db.delete_table('polls_choice')
        
        # Deleting model 'Contest'
        db.delete_table('polls_contest')
        
        # Deleting model 'Vote'
        db.delete_table('polls_vote')
        
        # Deleting model 'Result'
        db.delete_table('polls_result')
        
        # Deleting model 'Question'
        db.delete_table('polls_question')
        
        # Deleting model 'Poll'
        db.delete_table('polls_poll')
        
        # Deleting model 'Quiz'
        db.delete_table('polls_quiz')
        
        # Deleting model 'Contestant'
        db.delete_table('polls_contestant')
        
        # Dropping ManyToManyField 'Quiz.authors'
        db.delete_table('polls_quiz_authors')
        
        # Deleting unique_together for [contest, email] on Contestant.
        db.delete_unique('polls_contestant', ['contest_id', 'email'])
        
    
    
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
            'Meta': {'ordering': "('-active_from',)"},
            'active_from': ('models.DateTimeField', ["_('Active from')"], {}),
            'active_till': ('models.DateTimeField', ["_('Active till')"], {}),
            'category': ('models.ForeignKey', ["orm['core.Category']"], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'photo': ('models.ForeignKey', ["orm['photos.Photo']"], {}),
            'slug': ('models.SlugField', ["_('Slug')"], {'max_length': '255'}),
            'text': ('models.TextField', ["_('Text')"], {}),
            'text_announcement': ('models.TextField', ["_('Text with announcement')"], {}),
            'text_results': ('models.TextField', ["_('Text with results')"], {}),
            'title': ('models.CharField', ["_('Title')"], {'max_length': '200'})
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
            'active_from': ('models.DateTimeField', ["_('Active from')"], {'default': 'datetime.datetime.now', 'null': 'True', 'blank': 'True'}),
            'active_till': ('models.DateTimeField', ["_('Active till')"], {'null': 'True', 'blank': 'True'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'question': ('models.ForeignKey', ["orm['polls.Question']"], {'unique': 'True', 'verbose_name': "_('Question')"}),
            'text': ('models.TextField', ["_('Text')"], {'null': 'True', 'blank': 'True'}),
            'text_announcement': ('models.TextField', ["_('Text with announcement')"], {'null': 'True', 'blank': 'True'}),
            'text_results': ('models.TextField', ["_('Text with results')"], {'null': 'True', 'blank': 'True'}),
            'title': ('models.CharField', ["_('Title')"], {'max_length': '200'})
        },
        'photos.photo': {
            'Meta': {'ordering': "('-created',)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'core.author': {
            'Meta': {'ordering': "('name','slug',)"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'polls.quiz': {
            'Meta': {'ordering': "('-active_from',)"},
            'active_from': ('models.DateTimeField', ["_('Active from')"], {}),
            'active_till': ('models.DateTimeField', ["_('Active till')"], {}),
            'authors': ('models.ManyToManyField', ["orm['core.Author']"], {'verbose_name': "_('Authors')"}),
            'category': ('models.ForeignKey', ["orm['core.Category']"], {}),
            'has_correct_answers': ('models.BooleanField', ["_('Has correct answers')"], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'photo': ('models.ForeignKey', ["orm['photos.Photo']"], {}),
            'slug': ('models.SlugField', ["_('Slug')"], {'max_length': '255'}),
            'text': ('models.TextField', ["_('Text')"], {}),
            'text_announcement': ('models.TextField', ["_('text with announcement')"], {}),
            'text_results': ('models.TextField', ["_('Text with results')"], {}),
            'title': ('models.CharField', ["_('title')"], {'max_length': '200'})
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
    
    complete_apps = ['polls']
