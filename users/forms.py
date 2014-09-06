# coding=utf-8
from __future__ import absolute_import
from django import forms
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
