from datetime import datetime
import logging

from django.db import models, connection
from django.db.models import Q
from django.conf import settings

from ella.core.models import Listing, Publishable, Category
from ella.utils import remove_diacritical

ERROR_MESSAGES = {
    'cannot': 'This Publishable object cannot be exported'
}
log = logging.getLogger('ella.exports')

def cmp_listing_or_meta(x, y):
    " Sorts items in descending order. "
    from ella.ellaexports.models import ExportPosition
    def return_from_datetime(obj):
        if type(obj) == Listing:
            return obj.publish_from
        elif type(obj) == ExportPosition:
            return obj.visible_from

    classes = (Listing, ExportPosition,)
    if type(x) not in classes or type(y) not in classes:
        raise NotImplementedError

    date_x = return_from_datetime(x)
    date_y = return_from_datetime(y)
    if date_x > date_y:
        return -1
    elif date_x < date_y:
        return 1
    return 0

class ExportItemizer(object):
    """
    Class encapsulates process of querying Export models, 
    setting query parameters and iterating over result items.

    One can iterate over an ExportItemizer instance.
    """

    def __init__(self, slug=None, category=None, data_formatter=None):
        """
        Creates ExportItemizer instance. Export items can be queried by slug
        or by category parameters.

        If data_formatter parameter is present, it should contain object with callable
        member(self, publishable, export=None, export_category=None) .
        """
        from ella.ellaexports.models import Export
        # object members init
        self.__items = tuple()
        self.__counter = 0
        self._datetime_from = datetime.now()
        self._max_visible_items = None
        self.category = None
        self.export = None
        self.exports = tuple()
        self.data_formatter = data_formatter
        if not data_formatter:
            self.data_formatter = Export.objects.get_export_data #default data formatter

        if slug:
            self.exports = Export.objects.filter(slug=slug)
            self.export = self.exports[0]
        elif category:
            self.category = category

    def set_max_visible_items(self, value):
        " Accepts value as string, unicode, int or long. "
        if not value:
            return
        if type(value) in (str, unicode,):
            ivalue = int(value)
            self._max_visible_items = ivalue
        elif type(value) in (int, long,):
            self._max_visible_items = value

    def get_max_visible_items(self):
        return self._max_visible_items

    max_visible_items = property(get_max_visible_items, set_max_visible_items)

    def set_datetime_from(self, value):
        " Accepts value as string, unicode or datetime. "
        from ella.ellaexports.models import DATETIME_FORMAT
        if not value:
            return
        if type(value) in (str, unicode,):
            self._datetime_from = datetime.strptime(value, DATETIME_FORMAT)
        else:
            self._datetime_from = value

    def get_datetime_from(self):
        return self._datetime_from

    datetime_from = property(get_datetime_from, set_datetime_from)

    def next(self):
        if not self.__items:
            self.__execute_query()
        if self.__counter >= len(self.__items):
            self.__counter = 0
            raise StopIteration
        else:
            c = self.__counter
            self.__counter += 1
            return self.__items[c]

    def __getitem__(self, key):
        if not self.__items:
            self.__execute_query()
        return self.__items[key]

    def __iter__(self):
        return self

    def __insert_to_position(self, fix_positions, out):
        """ 
        Insert elements in fix_positions queryset to specified position
        in list specified by parameter out.

        Fixed-positioned items have higher priority than existing items in list 
        given in parameter out.

        This method changes "out" parameter.
        """
        tmp = list()
        positions = fix_positions.order_by('position')
        last_position = positions[0].position
        for i in range(len(positions)):
            item = positions[i]
            diff = item.position - last_position
            if diff > 1:
                # gap found
                # append items from out up to diff, then append item
                for x in range(diff - 1):
                    tmp.append(out.pop(0))
            tmp.append(item)
            last_position = item.position

        for remaining in range(len(out)):
            tmp.append(out.pop(0))

        for t in tmp:
            out.append(t)

    def __get_publishable(self, obj):
        from ella.ellaexports.models import ExportPosition
        if type(obj) == Listing:
            return obj.placement.publishable
        elif type(obj) == ExportPosition:
            return obj.object.publishable
        else:
            raise NotImplementedError

    def __get_overloaded_publishable(self, obj, export):
        """ 
        @return publishable object with overloaded attributes 
        title, photo, description. 

        Adds property obj.export_thumbnail_url, feed_updated.
        """
        from ella.ellaexports.models import FEED_DATETIME_FORMAT
        pub = self.__get_publishable(obj)
        field_dict = self.data_formatter(pub, export=export)
        if field_dict['title'].strip():
            pub.title = field_dict['title']
        if field_dict['photo']:
            pub.photo = field_dict['photo']
        if field_dict['description'].strip():
            pub.description = field_dict['description']

        feed_updated = pub.publish_from
        if 'visible_from' in field_dict:
            feed_updated = field_dict['visible_from']
        elif 'updated' in pub.__dict__:
            feed_updated = updated

        pub.export_thumbnail_url = None
        pub.feed_updated_raw_datetime = feed_updated
        pub.feed_updated = feed_updated.strftime(FEED_DATETIME_FORMAT)
        if pub.photo:
            formated = pub.photo.get_formated_photo(export.photo_format.name)
            #pub.export_thumbnail_url = u'%s%s' % (settings.MEDIA_URL, formated.url)
            if formated:
                pub.export_thumbnail_url = formated.url
        return pub

    def __execute_query(self):
        """
        generates export items for certain category or specific Export.

        @param   category   category asociated with Export
        @param   export     use Export object rather than category.
        @param   datetime_from  optional parameter 

        Functionality:
        1. URL format is /category/path/to/any/depth/[content_type/]
        2. Sort export items by its main placement and listings.
        3. Override item's title, photo, description if ExportMeta for item and Export is present.
        4. Override item's position and visibility timerange if defined.
        """
        from ella.ellaexports.models import Export, ExportPosition, ExportMeta,\
        POSITION_IS_NOT_OVERLOADED
        use_export = None
        use_category = self.category
        pre_out = list()
        if not self.export:
            exports = Export.objects.filter(category=use_category)
        else:
            exports = (self.export,)
            use_category = self.export.category
        if exports:
            use_export = exports[0]
            self.export = exports[0]
            if not self._max_visible_items:
                max_items = use_export.max_visible_items
            else:
                max_items = self._max_visible_items
            # Find fitting ExportPositions
            positions = ExportPosition.objects.filter(
                Q(visible_to__gte=self._datetime_from) | Q(visible_to__isnull=True),
                export=use_export, 
                position__exact=POSITION_IS_NOT_OVERLOADED,
                visible_from__lte=self._datetime_from,
            )
            fix_positions = ExportPosition.objects.filter(
                Q(visible_to__gte=self._datetime_from) | Q(visible_to__isnull=True),
                export=use_export, 
                position__gt=POSITION_IS_NOT_OVERLOADED,
                visible_from__lte=self._datetime_from,
            )
            objects = list()
            if use_export.use_objects_in_category:
                objects = list(Listing.objects.get_listing(
                    use_category, 
                    count=max_items * 2,
                    now=self._datetime_from
                ))
            #log.debug(remove_diacritical('Items via Listing: %s' % objects))
            map(lambda i: objects.append(i), positions)
            #log.debug(remove_diacritical('Items via ExportPosition: %s' % positions))
            objects.sort(cmp=cmp_listing_or_meta)
            #log.debug(remove_diacritical('Export items sorted: %s' % objects))
            if fix_positions:
                # Assign positions of items (if position is overloaded via ExportPosition)
                self.__insert_to_position(fix_positions, objects)
            #log.debug(remove_diacritical('Export items (overloaded positions): %s' % objects))
            pre_out = objects[:max_items]
        else:
            # Get listed objects for category
            if use_export.use_objects_in_category:
                objects = list(Listing.objects.get_listing(use_category))
                objects.sort(cmp=cmp_listing_or_meta)
                pre_out = objects
        # extract Publishable objects from Listing/ExportPosition objects
        self.__items = list()
        for i in pre_out:
            pub = self.__get_overloaded_publishable(i, export=use_export)
            self.__items.append(pub)

class ExportManager(models.Manager):

    def get_items_for_slug(self, slug, datetime_from=None, max_visible_items=None):
        from ella.ellaexports.models import Export
        exports = Export.objects.filter(slug=slug)
        if not exports:
            return list()
        e = ExportItemizer(slug=slug)
        if datetime_from:
            e.datetime_from = datetime_from
        else:
            e.datetime_from = datetime.now()
        e.max_visible_items = max_visible_items
        e.export = exports[0]
        return e
        """
        return self.get_items_for_category(
            export=exports[0], 
            datetime_from=datetime_from, 
            max_visible_items=max_visible_items
        )
        """
    
    def get_items_for_category(
            self, 
            category=None, 
            export=None, 
            datetime_from=None,
            max_visible_items=None
        ):
        e = ExportItemizer(category=category)
        if not datetime_from:
            e.datetime_from = datetime.now()
        else:
            e.datetime_from = datetime_from
        print 'Get Items for Category: datetime_from', e.datetime_from
        e.max_visible_items = max_visible_items
        if export:
            e.export = export
        return e

    def get_export_data(self, publishable, export=None, export_category=None):
        """ 
        @return dict containing keys: title, photo, description, [visible_from]. 
        If export parameter is None, first export fitting publishable's category
        is used.
        """
        from ella.ellaexports.models import Export, ExportPosition, ExportMeta
        from ella.ellaexports.models import UnexportableException
        if export:
            pub_export = export
        else:
            category = publishable.category
            if export_category:
                category = export_category
            pub_export = Export.objects.filter(category=category)
            if not pub_export:
                raise UnexportableException(ERROR_MESSAGES['cannot'])
            pub_export = pub_export[0]
        
        # Try to find ExportMeta and ExportPosition for given publishable
        metas = ExportMeta.objects.filter(publishable=publishable)
        pos = None
        out = dict()
        # FIXME simplify follwing code (cycle tries to find appropriate ExportMeta for selected Export)
        for meta in metas:
            positions = ExportPosition.objects.filter(object=meta, export=pub_export)
            if not positions:
                return {
                    'title': meta.title,
                    'photo': meta.photo,
                    'description': meta.description
                }

            pos = positions[0]
            return {
                'title': pos.object.title,
                'photo': pos.object.photo,
                'description': pos.object.description,
                'visible_from': pos.visible_from
            }

        if not pos:
            return {
                'title': publishable.title,
                'photo': publishable.photo,
                'description': publishable.description
            }

# EOF
