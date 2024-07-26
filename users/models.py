import random
import datetime

from django.conf import settings
from django.utils.crypto import get_random_string
from phonenumber_field.modelfields import PhoneNumberField
from rest_framework.exceptions import NotAcceptable
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core import validators
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, send_mail



from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField
from rest_framework.exceptions import NotAcceptable
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client



class UserManager(BaseUserManager):

    
    def create_user(self, username=None,email=None,phone_number=None, password=None, **extra_fields):

        """ create user with email or phone number and password"""

        
        if username is None:
            if email:
                username = email.split('@', 1)[0]
            if phone_number:
                username = random.choice('abcdefghijklmnopqrstuvwxyz') + str(phone_number)[-7:]
            while User.objects.filter(username=username).exists():
                username += str(random.randint(10, 99))
            
        email = self.normalize_email(email)
        user = self.model(phone_number=phone_number, username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save() 

        return user          

    def create_superuser(self,username,email,phone_number, password, **extra_fields):
        """ create superuser with email or phone number and password """
        
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(username ,email,phone_number, password, **extra_fields)
        
        
class User(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Username, password and email are required. Other fields are optional.
    """
    username = models.CharField(_('username'), max_length=32, unique=True,blank=True,
                                help_text=_(
                                    'Required. 30 characters or fewer starting with a letter. Letters, digits and underscore only.'),
                                validators=[
                                    validators.RegexValidator(r'^[a-zA-Z][a-zA-Z0-9_\.]+$',
                                                              _('Enter a valid username starting with a-z. '
                                                                'This value may contain only letters, numbers '
                                                                'and underscore characters.'), 'invalid'),
                                ],
                                error_messages={
                                    'unique': _("A user with that username already exists."),
                                }
                                )
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    email = models.EmailField(_('email address'), unique=True)
    phone_number= PhoneNumberField(_('mobile'), 
                                          validators=[
                                              validators.RegexValidator(r'^989[0-3,9]\d{8}$',
                                                                        ('Enter a valid mobile number.'), 'invalid'),
                                          ],
                                         
                                          )
    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin site.'))
    is_verified = models.BooleanField(_('verify'), default=False)
    is_active = models.BooleanField(_('active'), default=False,
                                    help_text=_('Designates whether this user should be treated as active. '
                                                'Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    last_seen = models.DateTimeField(_('last seen date'), null=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = [ 'email','phone_number']

    class Meta:
        
        db_table = 'users'
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """
        Returns the short name for the user.
        """
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)

    @property
    def is_loggedin_user(self):
        """
        Returns True if user has actually logged in with valid credentials.
        """
        return self.phone_number is not None or self.email is not None

    def save(self, *args, **kwargs):
        if self.email is not None and self.email.strip() == '':
            self.email = None
        super().save(*args, **kwargs)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nick_name = models.CharField(_('nick_name'), max_length=150, blank=True)
    avatar = models.ImageField(_('avatar'), blank=True)
    birthday = models.DateField(_('birthday'), null=True, blank=True)
    gender = models.BooleanField(_('gender'), help_text=_('female is False, male is True, null is unset'), null=True)
    address = models.ForeignKey(verbose_name=_('address'), to='Address', null=True, on_delete=models.SET_NULL)
    email = models.EmailField(_('email address'), blank=False)
    # phone_number= models.ForeignKey(User,related_name='mobile',on_delete=models.CASCADE,  blank=False,
                                         
    #                                       )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)    

    class Meta:
        db_table = 'user_profiles'
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')

    @property
    def get_first_name(self):
        return self.user.first_name

    @property
    def get_last_name(self):
        return self.user.last_name

    def get_nickname(self):
        return self.nick_name if self.nick_name else self.user.username


class Address(models.Model):



    user = models.ForeignKey(User, related_name="addresses", on_delete=models.CASCADE)
    # address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)
    country = CountryField()
    city = models.CharField(max_length=100)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True)



    




    class Meta:
        db_table = 'user_address'
        verbose_name = _('address')
        verbose_name_plural = _('address')
        # unique_together = ('user', 'device_uuid')

    def __str__(self):
        return self.user.get_full_name()

# class Province(models.Model):
#     name = models.CharField(max_length=50)
#     is_valid = models.BooleanField(default=True)
#     modified_at = models.DateTimeField(auto_now=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.name


class Activation(models.Model):


    user = models.OneToOneField(User, related_name='phone',on_delete=models.CASCADE)
    phone_number = PhoneNumberField()
    security_code = models.CharField(max_length=120)
    is_verified = models.BooleanField(default=False)
    sent = models.DateTimeField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.phone_number.as_e164

    def generate_security_code(self):
        """
        Returns a unique random `security_code` for given `TOKEN_LENGTH` in the settings.
        Default token length = 6
        """
        token_length = getattr(settings, "TOKEN_LENGTH", 6)
        return get_random_string(token_length, allowed_chars="0123456789")

    def is_security_code_expired(self):
        expiration_date = self.sent + datetime.timedelta(
            minutes=settings.TOKEN_EXPIRE_MINUTES
        )
        return expiration_date <= timezone.now()

    def send_confirmation(self):
        twilio_account_sid = settings.TWILIO_ACCOUNT_SID
        twilio_auth_token = settings.TWILIO_AUTH_TOKEN
        twilio_phone_number = settings.TWILIO_PHONE_NUMBER

        self.security_code = self.generate_security_code()

        # print(
        #     f'Sending security code {self.security_code} to phone {self.phone_number}')

        if all([twilio_account_sid, twilio_auth_token, twilio_phone_number]):
            try:
                twilio_client = Client(twilio_account_sid, twilio_auth_token)
                twilio_client.messages.create(
                    body=f"Your activation code is {self.security_code}",
                    to=str(self.phone_number),
                    from_=twilio_phone_number,
                )
                self.sent = timezone.now()
                self.save()
                return True
            except TwilioRestException as e:
                print(e)
        else:
            print("Twilio credentials are not set")

    def check_verification(self, security_code):
        if (
            not self.is_security_code_expired()
            and security_code == self.security_code
            and not self.is_verified
        ):
            self.is_verified = True
            self.save()
        else:
            raise NotAcceptable(
                _(
                    "Your security code is wrong, expired or this phone is verified before."
                )
            )

        return self.is_verified

