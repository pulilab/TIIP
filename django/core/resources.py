from import_export import resources
from project.models import Project, UNICEFSector, UNICEFGoal, InnovationCategory, CPD, Stage, TechnologyPlatform, \
    HardwarePlatform, NontechPlatform, ISC, PlatformFunction, UNICEFResultArea, InnovationWay
from import_export.fields import Field
from django.utils.translation import ugettext_lazy as _

from country.models import Country, CountryOffice, Currency

from project.serializers import LinkSerializer


class UserResource(resources.ModelResource):  # pragma: no cover
    """
    This class is basically a serializer for the django-import-export module
    TODO: write unit tests if necessary
    Fields:
     - Stats:
       - last login
       - date joined
       - ODK Synced
     - Permissions:
       - Active
       - Staff Status
       - Superuser Status
       - Global portfolio owner
     - Groups
       - groups
     - User Info
       - email address
       - name
       - account type
       - Organization
       - Country
       - Donor
       - Language
    """
    # General Overview
    published = Field(column_name=_('Published?'))
    contact = Field(column_name=_('Contact'))
    team = Field(column_name=_('Team'))
    overview = Field(column_name=_('Overview'))
    narrative = Field(column_name=_('Narrative'))
    country = Field(column_name=_('Country'))
    unicef_office = Field(column_name=_('UNICEF Office'))
