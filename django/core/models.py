from django.conf import settings
from django.db import models
from django.db.models import QuerySet
from django.db.models.query_utils import Q
from modeltranslation.manager import MultilingualQuerySet
from sorl.thumbnail import ImageField, get_thumbnail


class GetObjectOrNoneMixin(object):
    def get_object_or_none(self, select_for_update=False, **kwargs):
        """
        Hides Exception handling boilerplate when querying for single objects.
        Locks object (if selected for update) if exists else None
        """
        try:
            if select_for_update:
                return self.select_for_update().get(**kwargs)
            else:
                return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None


class ParentByIDMixin:
    @classmethod
    def get_parent_id(cls, object_id, parent_field):
        try:
            instance = cls.objects.get(id=object_id)
        except cls.DoesNotExist:
            return None
        else:
            return getattr(instance, '{}_id'.format(parent_field), None)


class GetObjectOrNoneQueryset(GetObjectOrNoneMixin, QuerySet):
    pass


class GetObjectOrNoneMultilingualQueryset(GetObjectOrNoneMixin, MultilingualQuerySet):
    pass


class ExtendedModel(models.Model):
    """
    Adds nice to have behaviors to the Model class, such as:
        - adds timestamps on create, update
        - simplifies single object queries by removing Exception handling boilerplate
    """
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    modified = models.DateTimeField(auto_now=True, auto_now_add=False)

    objects = GetObjectOrNoneQueryset.as_manager()

    class Meta:
        abstract = True


class ExtendedMultilingualModel(ExtendedModel):
    objects = GetObjectOrNoneMultilingualQueryset.as_manager()

    class Meta:
        abstract = True


class ActiveQuerySet(GetObjectOrNoneMixin, QuerySet):
    def __init__(self, *args, **kwargs):
        super(ActiveQuerySet, self).__init__(*args, **kwargs)

        if self.model:
            self.add_intial_q()

    def delete(self):
        self.update(is_active=False)

    def add_intial_q(self):
        self.query.add_q(Q(is_active=True))

    def force_delete(self):
        super(ActiveQuerySet, self).delete()


class SoftDeleteModel(models.Model):
    is_active = models.BooleanField(default=True)

    # IMPORTANT: The order of these two queryset is important. The normal queryset has to be defined first to have that
    #            as a default queryset
    all_objects = QuerySet.as_manager()
    objects = ActiveQuerySet.as_manager()

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        self.is_active = False
        self.save()


class CustomNameOrderedQuerySet(ActiveQuerySet):

    special_names = {
        'NA',
        'N/A',
        'Unknown',
        'Other',
        'Bespoke',
        'No'
    }

    def custom_ordered(self):
        items = self.all()
        items_front = []
        items_back = []
        for item in items:
            if item.get("name", None) in self.special_names:  # pragma: no cover
                items_front.append(item)
            else:
                items_back.append(item)

        return items_front + items_back


class ExtendedNameOrderedSoftDeletedModel(SoftDeleteModel, ExtendedModel):
    name = models.CharField(max_length=512)

    all_objects = QuerySet.as_manager()
    objects = CustomNameOrderedQuerySet.as_manager()

    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self):
        return self.name


class NewsItem(ExtendedModel):
    title = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=1024, blank=True)
    alt_text = models.CharField(max_length=128, blank=True)
    link = models.URLField()
    link_text = models.CharField(max_length=64, default="Read more >")
    visible = models.BooleanField(default=True)
    image = ImageField(upload_to='news_images', null=True, blank=True)
    order = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta:
        ordering = ['-order', '-id']

    def __str__(self):
        return self.title if self.title else 'No title'

    @property
    def thumbnail(self):
        try:
            if self.image:
                return get_thumbnail(self.image, f'x{settings.THUMBNAIL_HEIGHT}')
            else:  # pragma: no cover
                return None
        except OSError:  # pragma: no cover
            return None
