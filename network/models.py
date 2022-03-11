from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import User as DjangoUser
from django.core.validators import validate_email
from django.db import models
from django.db.models import Model
from django.utils.translation import gettext_lazy as _


class Group(Model):
    name = models.CharField(_('نام'), max_length=150)
    description = models.CharField(_('توضیحات'), max_length=250)
    owner = models.OneToOneField('network.User', on_delete=models.PROTECT, related_name='owned_group',
                                 related_query_name='owned_group')


class User(AbstractBaseUser):
    name = models.CharField(_('نام'), max_length=150)
    email = models.EmailField(_('email address'), unique=True)
    group = models.ForeignKey(Group, on_delete=models.PROTECT, related_name='users', related_query_name='users',
                              blank=True, null=True)

    USERNAME_FIELD = 'email'


class JoinRequest(Model):
    group = models.ForeignKey(Group, on_delete=models.PROTECT, related_name='join_requests',
                              related_query_name='join_requests')
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='join_requests',
                             related_query_name='join_requests')
    date = models.DateTimeField(_('Date Created'), null=True, blank=True, auto_now_add=True)


class ConnectionRequest(Model):
    requester = models.ForeignKey(Group, on_delete=models.PROTECT, related_name='sent_requests',
                                  related_query_name='sent_requests')

    requestee = models.ForeignKey(Group, on_delete=models.PROTECT, related_name='received_requests',
                                  related_query_name='received_requests')
    date = models.DateTimeField(_('Date Created'), null=True, blank=True, auto_now_add=True)
    accepted = models.BooleanField(default=False)


class ChatMessage(Model):
    user_from = models.ForeignKey(User, on_delete=models.PROTECT, related_name='sent_messages',
                                  related_query_name='sent_messages')

    user_to = models.ForeignKey(User, on_delete=models.PROTECT, related_name='received_messages',
                                related_query_name='received_messages')
    message = models.CharField(_('متن پیام'), max_length=250)
    date = models.DateTimeField(_('Date Created'), null=True, blank=True, auto_now_add=True)
