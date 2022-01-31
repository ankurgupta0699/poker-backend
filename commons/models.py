from django.db import models
from rest_framework import exceptions

from accounts import constants as accounts_constants
from commons import (
    constants as common_constants,
    managers as commons_managers
)
from poker_backend import settings


class Timestamp(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class EmailVerification(Timestamp):
    SIGNUP = 0
    GROUP = 1
    POKERBOARD = 2

    PURPOSE = [
        (SIGNUP, 'Signup'),
        (GROUP, 'Group'),
        (POKERBOARD, 'Pokerboard')
    ]
    
    email = models.EmailField(blank=True)
    name = models.CharField(
        max_length=accounts_constants.FIRST_NAME_LAST_NAME_MAX_LENGTH, blank=True)
    token_key = models.CharField(max_length=common_constants.TOKEN_MAX_LENGTH, unique=True)
    is_used = models.BooleanField(default=False)
    purpose = models.PositiveSmallIntegerField(choices=PURPOSE, default=SIGNUP)


class Invitation(Timestamp):
    PENDING = 0
    ACCEPTED = 1
    DECLINED = 2
    CANCELLED = 3

    INVITATION_STATUS = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (DECLINED, 'Declined'),
        (CANCELLED, 'Cancelled')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
    status = models.PositiveSmallIntegerField(choices=INVITATION_STATUS, default=PENDING)
    verification = models.ForeignKey(EmailVerification, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class SoftDelete(Timestamp):
    is_deleted = models.BooleanField(default=False)

    # manager for objects which are not soft-deleted
    objects = commons_managers.SoftDeleteManager()

    # manager for all the objects; including soft-deleted
    all_objects = models.Manager()

    def restore(self):
        self.is_deleted = False
        self.save()

    # overriding the default delete method
    def delete(self):
        self.is_deleted = True
        self.save()

    def hard_delete(self):
        raise exceptions.PermissionDenied
        # super().delete()

    class Meta:
        abstract = True
