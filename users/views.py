# coding=utf-8
from __future__ import absolute_import
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from users.forms import UserProfileForm
from users.models import User
from django.utils.translation import ugettext as _


class UserProfileView(TemplateView):
    template_name = 'users/profile.html'

    def dispatch(self, request, *args, **kwargs):
        self.user = get_object_or_404(User, pk=kwargs['user_id'])
        return super(UserProfileView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UserProfileView, self).get_context_data(**kwargs)
        context['profile_user'] = self.user
        return context


class UserSettingsView(TemplateView):
    template_name = 'users/settings.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.profile_form = UserProfileForm(request.POST or None, request.FILES or None,
                                            prefix='profile', instance=request.user)
        return super(UserSettingsView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UserSettingsView, self).get_context_data(**kwargs)
        context['profile_form'] = self.profile_form
        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        if action == 'profile' and self.profile_form.is_valid():
            self.profile_form.save()
            messages.success(request, _(u'Профиль успешно сохранен.'))
            return redirect(request.path)
        return self.get(request, *args, **kwargs)
