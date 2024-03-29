from allauth.account.models import EmailAddress, EmailConfirmation
from allauth.socialaccount.models import SocialAccount, SocialToken, SocialApp
from import_export_celery.models.importjob import ImportJob
from import_export_celery.models.exportjob import ExportJob
from import_export_celery.admin import ExportJobAdmin
from django.contrib.admin.sites import NotRegistered
from django.apps import apps as proj_apps
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.postgres.fields.array import ArrayField
from django.forms.widgets import MediaDefiningClass
from modeltranslation.admin import TranslationAdmin
from modeltranslation.translator import translator
from adminsortable2.admin import SortableAdminMixin
from user.models import UserProfile
from .widgets import AdminArrayField

from import_export.admin import ExportActionMixin
from core.resources import UserResource
from ..models import NewsItem


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    readonly_fields = ['filters']
    filter_horizontal = ['manager_of']
    can_delete = False


class CustomUserAdmin(ExportActionMixin, UserAdmin):
    list_display = ('userprofile', 'country', 'type', 'organisation', 'is_staff', 'is_superuser')
    search_fields = ('userprofile__name', 'email', 'userprofile__country__name', 'userprofile__organisation__name')
    inlines = (UserProfileInline,)
    resource_class = UserResource

    def country(self, obj):
        return obj.userprofile.country

    country.allow_tags = True

    def type(self, obj):
        return obj.userprofile.get_account_type_display()

    type.allow_tags = True
    type.short_description = "Account Type"

    def organisation(self, obj):
        return obj.userprofile.organisation

    organisation.allow_tags = True

    def get_list_filter(self, request):
        return super().get_list_filter(request) + ('userprofile__account_type',)

    def lookup_allowed(self, lookup, *args, **kwargs):
        if lookup == 'userprofile__account_type__exact':
            return True
        return super().lookup_allowed(lookup, *args, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        self.fieldsets[0][1]["fields"] = ('password',)
        self.fieldsets[1][1]["fields"] = ('email',)
        self.fieldsets[2][1]["fields"] = ('is_active', 'is_staff', 'is_superuser', 'groups')
        form = super(CustomUserAdmin, self).get_form(request, obj, **kwargs)
        return form


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):  # pragma: no cover
        self.request = request
        self.user_cache = None
        super(AuthenticationForm, self).__init__(*args, **kwargs)

        UserModel = get_user_model()
        self.username_field = UserModel._meta.get_field(UserModel.USERNAME_FIELD)
        if self.fields['username'].label is None:
            self.fields['username'].label = "Email"


class MultiLevelAdminMeta(MediaDefiningClass):
    """
    Metaclass for classes that can have media definitions.
    """
    def __new__(mcs, name, bases, attrs):
        new_class = super(MultiLevelAdminMeta, mcs).__new__(mcs, name, bases, attrs)

        def get_translated_function(language):
            def translated(self, obj):
                translated = True
                for field_name in translator.get_options_for_model(self.model).get_field_names():
                    translated &= bool(getattr(obj, '{}_{}'.format(field_name, language)))
                return translated
            translated.short_description = 'Translated {}'.format(language.upper())
            translated.boolean = True
            return translated

        for language_code, language_name in settings.LANGUAGES:
            setattr(new_class, 'is_translated_{}'.format(language_code), get_translated_function(language_code))

        return new_class


class AllObjectsAdmin(admin.ModelAdmin, metaclass=MultiLevelAdminMeta):
    def get_queryset(self, request):
        return self.model.all_objects.all()

    def get_list_display(self, request):
        list_display = list(super(AllObjectsAdmin, self).get_list_display(request))
        if 'is_active' in list_display:
            return list_display

        language_fields = ['is_translated_{}'.format(l[0]) for l in settings.LANGUAGES]
        return list_display + ['is_active'] + language_fields


class ArrayFieldMixin(object):
    formfield_overrides = {ArrayField: {'form_class': AdminArrayField}}

    class Media:
        js = ('arrayfield.js',)


@admin.register(NewsItem)
class NewsFeedAdmin(SortableAdminMixin, TranslationAdmin):
    list_display = ('__str__', 'order', 'link', 'visible')


admin.site.login_form = CustomAuthenticationForm
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.unregister(EmailAddress)
admin.site.unregister(EmailConfirmation)
admin.site.unregister(SocialAccount)
admin.site.unregister(SocialToken)
admin.site.unregister(SocialApp)
admin.site.unregister(ImportJob)

# renaming the admin section name
iec = proj_apps.get_app_config('import_export_celery')
iec.verbose_name = "Generate Export"

# the order of the loaded apps might change, and here we check if its registered or not
try:
    admin.site.unregister(ExportJob)
except NotRegistered:
    pass


class ExportJobAdminNew(ExportJobAdmin):
    exclude = ('job_status', 'site_of_origin', 'app_label', 'model', )

    readonly_fields = (
        "job_status_info",
        "author",
        "updated_by",
        "file",
        "processing_initiated",
    )


# the order of loaded apps might require this try
try:
    admin.site.unregister(ExportJob)
except NotRegistered:
    pass

# after the unregistering we register the django-import-export-celery ExportJobAdmin again
admin.site.register(ExportJob, ExportJobAdminNew)
