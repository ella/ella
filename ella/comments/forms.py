from datetime import datetime, timedelta


from django import newforms as forms

from django.db import models
from django.contrib.contenttypes.models import ContentType

from django.utils.translation import ugettext


from ella.comments import defaults
from ella.comments.defaults import OPTIONS_NAME, TARGET_NAME, HASH_NAME, PARENT_NAME, FORM_OPTIONS, SUBJECT_LENGTH
from ella.comments.models import Comment, CommentOptions, BannedUser

from ella.core.cache import get_cached_object




class CommentForm(forms.Form):
    def __init__(self, data=None, init_props=defaults.INIT_PROPS, **kwargs):
        super(CommentForm, self).__init__(data=data, **kwargs)
        self.set_init_props(data, init_props)
        self.init_form(self.init_props)

        if not data:
            self.fill_form_values()


    def set_init_props(self, data=None, init_props=defaults.INIT_PROPS):
        """set initial form properties
        form is created from data, if it is bound
        from init_props, if not bound
        from options saved in database, if any
        """
        if data:
            # don't want MultiValueDict here - sorry for this hack - FIXME
            init_props = dict(zip(data.keys(), data.values()))

        # copy defalt settings
        self.init_props = defaults.INIT_PROPS.copy()

        # set actual time
        now = int(datetime.now().strftime('%s'))
        self.init_props['timestamp'] = now
        self.init_props['timestamp_min_valid'] = now - defaults.FORM_TIMEOUT

        # update defaults with form init params
        self.init_props.update(init_props)

        target_ct, target_id = None, None
        try:
            target_ct, target_id = self.init_props[TARGET_NAME].split(defaults.OPTS_DELIM)
            target_ct, target_id = int(target_ct), int(target_id)
            target_contenttype = get_cached_object(ContentType.objects.get_for_model(ContentType), pk=target_ct)
            self.target_object = get_cached_object(target_contenttype, pk=target_id)
        except ValueError:
            pass
        except models.ObjectDoesNotExist:
            pass

        # defaults for this instance
        self.init_props['target_ct'] = target_ct
        self.init_props['target_id'] = target_id

        # find any options updates in database
        self.check_db_options(target_ct, target_id)

        # defaults continue
        self.OPTIONS = self.init_props[OPTIONS_NAME].split(defaults.OPTS_DELIM)
        self.init_props[HASH_NAME] = self.get_hash(self.init_props[OPTIONS_NAME], self.init_props[TARGET_NAME], self.init_props['timestamp'])


    def check_db_options(self, target_ct=None, target_id=None):
        """look in database, if there are no options for this discussion"""
        from django.core.exceptions import ObjectDoesNotExist
        try:
            options = CommentOptions.objects.get(target_ct=target_ct, target_id=target_id)
            self.init_props[OPTIONS_NAME] = options.options
            self.init_props['timestamp_min_valid'] = int(options.timestamp.strftime('%s')) # TODO: everything should be datetime object...
        except ObjectDoesNotExist:
            pass


    def get_hash(self, options='', target='', timestamp=''):
        """
        counts md5 hash of options
        this is simple check, if sent data are the same as expected
        (defined in options)

        """
        import md5
        from django.conf import settings
        timestamp = str(timestamp)
        return md5.new('-'.join((options, target, timestamp, settings.SECRET_KEY,))).hexdigest()


    def init_form(self, init_props=defaults.INIT_PROPS):
        """create form by given init_props"""
        self.add_hidden_inputs()
        self.add_normal_inputs()
        self.arrange_form_by_opts()

    def arrange_form_by_opts(self):
        """arrange form by options"""
        if FORM_OPTIONS['LOGGED_ONLY'] in self.OPTIONS:
            self.add_username_inputs(anonymous=False)
        elif FORM_OPTIONS['UNAUTHORIZED_ONLY'] in self.OPTIONS:
            self.add_username_inputs(registered=False)
        else:
            self.add_username_inputs()


    def add_hidden_inputs(self):
        """new hidden input fields, without initial values"""
        hidden = forms.HiddenInput()
        self.fields[HASH_NAME] = forms.RegexField(self.init_props[HASH_NAME], widget=hidden)
        self.fields[OPTIONS_NAME] = forms.CharField(max_length=defaults.OPTS_LENGTH, required=False, widget=hidden)
        self.fields[TARGET_NAME] = forms.RegexField(r'\d+%s\d+' % defaults.OPTS_DELIM, max_length=defaults.TARGET_LENGTH, widget=hidden)
        self.fields[PARENT_NAME] = forms.IntegerField(required=False, widget=hidden)
        self.fields['timestamp'] = forms.IntegerField(min_value=self.init_props['timestamp_min_valid'], widget=hidden)

    def add_normal_inputs(self):
        """any other normal inputs"""
        textarea = forms.Textarea()
        self.fields['subject'] = forms.CharField(max_length=SUBJECT_LENGTH)
        self.fields['content'] = forms.CharField(max_length=defaults.COMMENT_LENGTH, widget=textarea)

    def add_username_inputs(self, registered=True, anonymous=True):
        """add user validation fields"""
        if registered:
            self.fields['username'] = forms.CharField(max_length=defaults.USERNAME_LENGTH)
            self.fields['password'] = forms.CharField(widget=forms.PasswordInput())

        if anonymous:
            self.fields['nickname'] = forms.CharField(max_length=defaults.NICKNAME_LENGTH)
            self.fields['email'] = forms.EmailField(required=False)

        if registered and anonymous:
            self.fields['reg_anonym_sel'] = forms.CharField(max_length=3, required=True,
                                                             widget=forms.RadioSelect(choices=defaults.USER_CHOICE))
            self.fields['username'].required = False
            self.fields['password'].required = False
            self.fields['nickname'].required = False

            # TODO: check out clean() method and clean_FIELD
            # only for bound forms
            # registered inputs are required if reg_anonym_sel is set to RE
            # anonymous input if it is set AN
            if self.init_props.has_key('reg_anonym_sel'):
                if defaults.USER_CHOICE[0][0] == self.init_props['reg_anonym_sel']:
                    # 'RE' - registered only
                    self.fields['username'].required = True
                    self.fields['password'].required = True
                    if self.init_props.has_key('nickname'): del self.init_props['nickname']
                    if self.init_props.has_key('email'): del self.init_props['email']

                elif defaults.USER_CHOICE[1][0] == self.init_props['reg_anonym_sel']:
                    # 'AN' - anonymous users
                    self.fields['nickname'].required = True
                    self.fields['email'].required = False
                    if self.init_props.has_key('username'): del self.init_props['username']
                    if self.init_props.has_key('password'): del self.init_props['password']


    def fill_form_values(self):
        """fill form initial values - only for nonbound form"""
        # TODO: maybe add decorator for nonbound validation ???
        self.fields[HASH_NAME].initial = self.init_props[HASH_NAME]
        self.fields[OPTIONS_NAME].initial = self.init_props[OPTIONS_NAME]
        self.fields[TARGET_NAME].initial = self.init_props[TARGET_NAME]
        self.fields[PARENT_NAME].initial = self.init_props[PARENT_NAME]
        self.fields['timestamp'].initial = self.init_props['timestamp']


    def clean(self):
        """registered user validation and other cleaning"""
        from django.newforms.util import ValidationError

        if 'username' in self.init_props and 'password' in self.init_props:
            from django.contrib.auth import authenticate, login

            user = authenticate(username=self.init_props['username'], password=self.init_props['password'])
            if not user:
                raise ValidationError, ugettext("Invalid user.")
            elif len(BannedUser.objects.filter(target_ct=self.init_props['target_ct'],
                                                         target_id=self.init_props['target_id'],
                                                         user=user)) > 0:
                raise ValidationError, ugettext("Banned user.")
            else:
                self.cleaned_data['user'] = user

        try:
            # target_ct, target_id validation
            target_ct = self.init_props['target_ct']
            target_id = self.init_props['target_id']
            target_ct = get_cached_object(ContentType.objects.get_for_model(ContentType), pk=target_ct)
            target_object = get_cached_object(target_ct, pk=target_id)

            self.cleaned_data['target_ct'] = target_ct
            self.cleaned_data['target_id'] = target_id
            self.cleaned_data['target_object'] = target_object
        except models.ObjectDoesNotExist:
            raise ValidationError, ugettext("Target object does not exist.")

        return self.cleaned_data


    def save(self, other_values={}):
        """save method for associated model Comment"""
        if not(self.is_bound and self.is_valid()):
            #raise 'Invalid form', 'you cannot save invalid form'
            return False

        values = {}
        for i in Comment._meta.fields:
            if isinstance(i, models.AutoField):
                continue
            if self.cleaned_data.has_key(i.name):
                values[i.name] = self.cleaned_data[i.name]
            if other_values.has_key(i.name):
                values[i.name] = other_values[i.name]

        # Check that this comment isn't duplicate. (Sometimes people post
        # comments twice by mistake.) If it is, fail silently by pretending
        # the comment was posted successfully.
        values_filter = {}
        for i in values:
            if values[i]:
                values_filter[i] = values[i]
        values_filter['submit_date__gte'] = datetime.now() - timedelta(seconds=defaults.POST_TIMEOUT)

        same_posts = Comment.objects.filter(**values_filter)

        if not len(same_posts):
            Comment(**values).save()

    def __repr__(self):
        return 'CommentForm for [%s] with fields %s' % (self.fields['target'].initial, sorted(self.fields.keys()))



"""
Cleanup init_props key names: 'gonzo' => HASH_NAME, ...
and maybe other init_props['string']

should there be an SITE ForeignKey in these models?
-> update komentare/templatetags/comments.py respectively



"""




