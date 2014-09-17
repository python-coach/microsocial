# coding=utf-8
from __future__ import absolute_import
import datetime
from django.contrib import messages
from django.contrib.auth import login, BACKEND_SESSION_KEY
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView, View
from users.forms import UserProfileForm, UserPasswordChangeForm, UserEmailChangeForm, UserWallPostForm, SearchForm
from users.models import User, FriendInvitation
from django.utils.translation import ugettext as _


class UserProfileView(TemplateView):
    template_name = 'users/profile.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.user = get_object_or_404(User, pk=kwargs['user_id'])
        self.is_my_profile = self.user == request.user
        self.wallpost_form = UserWallPostForm(request.POST or None)
        return super(UserProfileView, self).dispatch(request, *args, **kwargs)

    def get_wall_posts(self):
        paginator = Paginator(self.user.wall_posts.select_related('author'), 20)
        page = self.request.GET.get('page')
        try:
            wall_posts = paginator.page(page)
        except PageNotAnInteger:
            wall_posts = paginator.page(1)
        except EmptyPage:
            wall_posts = paginator.page(paginator.num_pages)
        return wall_posts

    def get_context_data(self, **kwargs):
        context = super(UserProfileView, self).get_context_data(**kwargs)
        context['is_my_profile'] = self.is_my_profile
        context['profile_user'] = self.user
        context['wall_posts'] = self.get_wall_posts()
        context['wallpost_form'] = self.wallpost_form
        if not self.is_my_profile:
            context['is_my_friend'] = User.friendship.are_friends(self.request.user, self.user)
        return context

    def post(self, request, *args, **kwargs):
        if self.wallpost_form.is_valid():
            post = self.wallpost_form.save(commit=False)
            post.user = self.user
            post.author = request.user
            post.save()
            messages.success(request, _(u'Сообщение успешно добавлено.'))
            return redirect(request.path)
        return self.get(request, *args, **kwargs)


class UserSettingsView(TemplateView):
    template_name = 'users/settings.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        action = request.POST.get('action')
        self.profile_form = UserProfileForm(
            (request.POST if action == 'profile' else None),
            (request.FILES if action == 'profile' else None),
            prefix='profile', instance=request.user
        )
        self.password_form = UserPasswordChangeForm(request.user, (request.POST if action == 'password' else None),
                                                    prefix='password')
        self.email_form = UserEmailChangeForm(request.user, (request.POST if action == 'email' else None),
                                              prefix='email')
        return super(UserSettingsView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UserSettingsView, self).get_context_data(**kwargs)
        context['profile_form'] = self.profile_form
        context['password_form'] = self.password_form
        context['email_form'] = self.email_form
        return context

    def post(self, request, *args, **kwargs):
        if self.profile_form.is_valid():
            self.profile_form.save()
            messages.success(request, _(u'Профиль успешно сохранен.'))
            return redirect(request.path)
        elif self.password_form.is_valid():
            self.password_form.save()
            request.user.backend = request.session[BACKEND_SESSION_KEY]
            login(request, request.user)
            messages.success(request, _(u'Пароль успешно изменен.'))
            return redirect(request.path)
        elif self.email_form.is_valid():
            self.email_form.save()
            messages.success(request, _(u'Email успешно изменен.'))
            return redirect(request.path)
        return self.get(request, *args, **kwargs)


class UserFriendsView(TemplateView):
    template_name = 'users/friends_friends.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(UserFriendsView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UserFriendsView, self).get_context_data(**kwargs)
        context['friends_menu'] = 'friends'
        paginator = Paginator(self.request.user.friends.all(), 20)
        page = self.request.GET.get('page')
        try:
            items = paginator.page(page)
        except PageNotAnInteger:
            items = paginator.page(1)
        except EmptyPage:
            items = paginator.page(paginator.num_pages)
        context['items'] = items
        return context


class UserIncomingView(TemplateView):
    template_name = 'users/friends_incoming.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(UserIncomingView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UserIncomingView, self).get_context_data(**kwargs)
        context['friends_menu'] = 'incoming'
        paginator = Paginator(self.request.user.incoming_friend_invitations.all(), 20)
        page = self.request.GET.get('page')
        try:
            items = paginator.page(page)
        except PageNotAnInteger:
            items = paginator.page(1)
        except EmptyPage:
            items = paginator.page(paginator.num_pages)
        context['items'] = items
        return context


class UserOutcomingView(TemplateView):
    template_name = 'users/friends_outcoming.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(UserOutcomingView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UserOutcomingView, self).get_context_data(**kwargs)
        context['friends_menu'] = 'outcoming'
        paginator = Paginator(self.request.user.outcoming_friend_invitations.all(), 20)
        page = self.request.GET.get('page')
        try:
            items = paginator.page(page)
        except PageNotAnInteger:
            items = paginator.page(1)
        except EmptyPage:
            items = paginator.page(paginator.num_pages)
        context['items'] = items
        return context


class FriendshipAPIView(View):
    @method_decorator(login_required)
    @method_decorator(require_POST)
    def dispatch(self, request, *args, **kwargs):
        method_name = '_action_%s' % request.POST.get('action', '')
        if not hasattr(self, method_name):
            raise Http404
        default_url = getattr(self, method_name)()
        return redirect(request.POST.get('next') or default_url or 'main')

    def _get_int_or_none(self, attr_name):
        try:
            return self.request.POST.get(attr_name)
        except (ValueError, TypeError):
            pass

    def _action_add_to_friends(self):
        user_id = self._get_int_or_none('user_id')
        if user_id:
            try:
                r = FriendInvitation.objects.add(self.request.user, user_id)
            except ValueError, e:
                messages.warning(self.request, e)
            else:
                if r == 1:
                    messages.success(self.request, _(u'Заявка успешно отправлена и ожидает рассмотрения.'))
                elif r == 2:
                    messages.success(self.request, _(u'Пользователь успешно добавлен в друзья.'))
                    return 'user_friends'
        return 'user_outcoming'

    def _action_delete_from_friends(self):
        user_id = self._get_int_or_none('user_id')
        if user_id:
            if User.friendship.delete(self.request.user, user_id):
                messages.success(self.request, _(u'Пользователь успешно удален из друзей.'))
        return 'user_friends'

    def _action_cancel_outcoming(self):
        user_id = self._get_int_or_none('user_id')
        if user_id:
            FriendInvitation.objects.filter(from_user=self.request.user, to_user=user_id).delete()
            messages.success(self.request, _(u'Заявка успешно отменена.'))
        return 'user_outcoming'

    def _action_approve(self):
        user_id = self._get_int_or_none('user_id')
        if user_id:
            try:
                FriendInvitation.objects.approve(user_id, self.request.user)
            except ValueError, e:
                messages.warning(self.request, e)
            else:
                messages.success(self.request, _(u'Заявка успешно подтверждена. Пользователь добавлен в друзья.'))
        return 'user_incoming'

    def _action_reject(self):
        user_id = self._get_int_or_none('user_id')
        if user_id:
            try:
                FriendInvitation.objects.reject(user_id, self.request.user)
            except ValueError, e:
                messages.warning(self.request, e)
            else:
                messages.success(self.request, _(u'Заявка успершно отклонена.'))
        return 'user_incoming'


class SearchView(TemplateView):
    template_name = 'users/search.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.form = SearchForm(request.GET or None)
        return super(SearchView, self).dispatch(request, *args, **kwargs)

    def get_filtered_qs(self, qs):
        self.form.is_valid()
        if not hasattr(self.form, 'cleaned_data'):
            return qs
        if self.form.cleaned_data.get('name'):
            query = None
            for val in self.form.get_values_list('name'):
                q = Q(first_name__icontains=val) | Q(last_name__icontains=val)
                if query is None:
                    query = q
                else:
                    query |= q
            if query:
                qs = qs.filter(query)
        if self.form.cleaned_data.get('sex'):
            qs = qs.filter(sex=self.form.cleaned_data['sex'])
        if self.form.cleaned_data.get('by_from'):
            qs = qs.filter(birth_date__gte=datetime.datetime(self.form.cleaned_data['by_from'], 1, 1))
        if self.form.cleaned_data.get('by_to'):
            qs = qs.filter(birth_date__lt=datetime.datetime(self.form.cleaned_data['by_to'] + 1, 1, 1))
        for field_name in ('city', 'job', 'about_me', 'interests'):
            query = None
            for val in self.form.get_values_list(field_name):
                q = Q(**{'%s__icontains' % field_name: val})
                if query is None:
                    query = q
                else:
                    query |= q
            if query:
                qs = qs.filter(query)
        return qs

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)
        context['form'] = self.form
        qs = self.get_filtered_qs(User.objects.all())
        paginator = Paginator(qs, 20)
        page = self.request.GET.get('page')
        try:
            items = paginator.page(page)
        except PageNotAnInteger:
            items = paginator.page(1)
        except EmptyPage:
            items = paginator.page(paginator.num_pages)
        context['items'] = items
        return context
