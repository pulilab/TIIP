from django.contrib.postgres.fields import HStoreField
from django.db import models, transaction
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from core.models import ExtendedModel
from .tasks import send_user_request_to_admins


class Organisation(ExtendedModel):
    name = models.CharField(unique=True, max_length=255)

    class Meta:
        ordering = ['name']

    def __str__(self):  # pragma: no cover
        return self.name


class UserProfile(ExtendedModel):
    IMPLEMENTER = 'I'
    DONOR = 'D'
    DONOR_ADMIN = 'DA'
    SUPER_DONOR_ADMIN = 'SDA'
    GOVERNMENT = 'G'
    COUNTRY_ADMIN = 'CA'
    SUPER_COUNTRY_ADMIN = 'SCA'
    INVENTORY = 'Y'
    ACCOUNT_TYPE_CHOICES = (
        (IMPLEMENTER, _('Implementer')),
        (DONOR, _('Investor Viewer')),
        (DONOR_ADMIN, _('Investor Admin')),
        (SUPER_DONOR_ADMIN, _('Investor System Admin')),
        (GOVERNMENT, _('Government Viewer')),
        (COUNTRY_ADMIN, _('Government Admin')),
        (SUPER_COUNTRY_ADMIN, _('Government System Admin')),
        (INVENTORY, _('Inventory User')),
    )

    account_type = models.CharField(
        max_length=3,
        choices=ACCOUNT_TYPE_CHOICES,
        default=IMPLEMENTER,
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, null=True)
    organisation = models.ForeignKey(Organisation, blank=True, null=True, on_delete=models.SET_NULL)
    country = models.ForeignKey('country.Country', null=True, on_delete=models.SET_NULL)
    donor = models.ForeignKey('country.Donor', related_name='userprofiles', null=True, on_delete=models.SET_NULL)
    language = models.CharField(max_length=2, choices=settings.LANGUAGES, default='en')
    global_portfolio_owner = models.BooleanField(default=False)
    filters = HStoreField(default=dict, blank=True)
    manager_of = models.ManyToManyField('country.CountryOffice', related_name="country_managers",
                                        verbose_name='Country Manager Of', blank=True)

    def __str__(self):
        return "{} <{}>".format(self.name, self.user.email) if self.name else ""

    def is_government_type(self):
        return self.account_type in [self.GOVERNMENT, self.COUNTRY_ADMIN, self.SUPER_COUNTRY_ADMIN]

    def is_investor_type(self):
        return self.account_type in [self.DONOR, self.DONOR_ADMIN, self.SUPER_DONOR_ADMIN]


@receiver(pre_save, sender=UserProfile)
def admin_request_on_change(sender, instance, **kwargs):
    if instance.id:
        old_account_type = UserProfile.objects.get(id=instance.id).account_type
        if instance.account_type != UserProfile.IMPLEMENTER and instance.account_type != old_account_type:
            instance.__trigger_send = True


@receiver(post_save, sender=UserProfile)
def admin_request_on_create(sender, instance, created, **kwargs):
    if created and instance.account_type != UserProfile.IMPLEMENTER or getattr(instance, '__trigger_send', False):
        transaction.on_commit(lambda: send_user_request_to_admins.apply_async(args=(instance.pk, )))
