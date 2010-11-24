from django.utils.feedgenerator import Rss201rev2Feed
from django.utils.xmlutils import SimplerXMLGenerator

class MediaElement(object):
    """
    """
    def __init__(self, tag_name, attrs=None, contents=None, children=None):
        self.tag_name = tag_name
        self.attrs = attrs or {}
        self.contents = contents
        self.children = children or []

    def add_to(self, handler):
        handler.startElement(self.tag_name, self.attrs)
        for element in self.children:
            element.add_to(handler)
        if self.contents is not None:
            # TODO: CDATA
            handler.characters(self.contents)
        handler.endElement(self.tag_name)

class CDataXMLGenerator(SimplerXMLGenerator):
    """
    """
    def addCDataElement(self, name, contents=None, attrs=None):
        if attrs is None: attrs = {}
        self.startElement(name, attrs)
        if contents is not None:
            self._write('<![CDATA[' + contents + ']]>')
        self.endElement(name)

class MediaRSSFeed(Rss201rev2Feed):
    """
    """
    # TODO: Use CDataXMLGenerator as handler.
    #def write(self, outfile, encoding): pass

    def rss_attributes(self):
        attrs = super(MediaRSSFeed, self).rss_attributes()
        attrs['xmlns:media'] = 'http://search.yahoo.com/mrss/'
        return attrs

    def add_item_elements(self, handler, item):
        super(MediaRSSFeed, self).add_item_elements(handler, item)
        if 'media_list' in item:
            for media_elem in item['media_list']:
                media_elem.add_to(handler)
