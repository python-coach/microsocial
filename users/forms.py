# coding=utf-8
from __future__ import absolute_import
from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.utils.translation import ugettext
from microsocial.forms import BootstrapFormMixin
from users.models import User


class UserProfileForm(forms.ModelForm, BootstrapFormMixin):
    class Meta:
        model = User
        fields = ('avatar', 'first_name', 'last_name', 'sex', 'birth_date', 'city', 'job', 'about_me', 'interests')

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        BootstrapFormMixin.__init__(self)
        self.fields['birth_date'].widget.attrs['placeholder'] = ugettext(u'Введите дату в формате гггг-мм-дд')


class UserPasswordChangeForm(PasswordChangeForm, BootstrapFormMixin):
    def __init__(self, *args, **kwargs):
        super(UserPasswordChangeForm, self).__init__(*args, **kwargs)
        BootstrapFormMixin.__init__(self)
        for field_name in ('old_password', 'new_password1', 'new_password2'):
            self.fields[field_name] = self.fields.pop(field_name)
