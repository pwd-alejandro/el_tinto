import uuid

from django.db import models
from django.contrib.auth.models import UserManager as BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from phonenumber_field.modelfields import PhoneNumberField

from el_tinto.utils.utils import get_env_value


class UserManager(BaseUserManager):
    """
    User Manager that knows how to create users via email instead of username
    """
    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    
    objects = UserManager()
    
    email = models.EmailField(
        'email address',
        unique=True,
        blank=False,
        null=False,
        error_messages={
            'unique': 'A user with that email already exists.'
        }
    )
    
    phone_number = PhoneNumberField(blank=True)
    first_name = models.CharField(max_length=25, blank=True, default='')
    last_name = models.CharField(max_length=25, blank=True, default='')
    username = None
    preferred_email_days = ArrayField(models.SmallIntegerField(), blank=True, default=list)
    best_user = models.BooleanField(default=False)
    referral_code = models.CharField(max_length=6, blank=True, default='')
    uuid = models.UUIDField(default='')
    referred_by = models.ForeignKey(
        'users.User',
        default=None,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='referred_users'
    )

    # Extra parameters
    # sunday_missing_emails = models.SmallIntegerField(default=4)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    @property
    def user_name(self):
        """
        returns the first name of the user if it exists else returns the email of the user.

        :return:
        user_name: str
        """
        return self.first_name if self.first_name and self.first_name != '' else self.email.split('@')[0]

    @property
    def opened_mails(self):
        """
        returns how many emails the user has opened

        :return:
        opened_mails: int
        """
        return self.sentemails_set.exclude(opened_date=None).count()

    @property
    def referred_users_count(self):
        """
        Calculate referred users invited by current user.
        Referred users are those who have been referred by someone and have opened at least
        one email. They can be active or inactive

        :return:
        referred_users_count: int
        """
        referred_users = User.objects.filter(referred_by=self)

        referred_users_count = 0

        for referred_user in referred_users:
            if referred_user.sentemails_set.exclude(opened_date=None).count() > 0:
                referred_users_count += 1

        return referred_users_count

    @property
    def env(self):
        """
        Returns the environment on which the code is being executed.

        :return:
        env: str
        """
        return get_env_value()

    def save(self, *args, **kwargs):
        from el_tinto.utils.users import create_user_referral_code

        if not self.referral_code:
            self.referral_code = create_user_referral_code(self)
        super(User, self).save(*args, **kwargs)

    def __str__(self):
        return self.email


class Unsuscribe(models.Model):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE)
    boring = models.BooleanField(default=False)
    invasive = models.BooleanField(default=False)
    variety = models.BooleanField(default=False)
    not_used = models.BooleanField(default=False)
    other_email = models.BooleanField(default=False)
    recommendation = models.TextField(default='', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.user}'
