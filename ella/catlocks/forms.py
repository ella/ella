from django import forms

CATEGORY_LOCK_FORM = '__CATEGORY_LOCK_FORM__'

class CategoryLockForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)
    def __init__(self, *args, **kwargs):
        self.base_fields[CATEGORY_LOCK_FORM] = forms.IntegerField(widget=forms.HiddenInput, initial=1)
        super(CategoryLockForm, self).__init__(*args, **kwargs)

