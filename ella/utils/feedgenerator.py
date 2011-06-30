from xml.sax.saxutils import quoteattr

from django.utils.feedgenerator import Rss201rev2Feed
from django.utils.xmlutils import SimplerXMLGenerator

CDATA_CHARS = set('&<>')

class MediaElement(object):
    """
    """
    def __init__(self, tag_name, contents=None, attrs=None):
        self.tag_name = tag_name
        self.contents = contents
        self.attrs = attrs or {}
        self.children = []
        #self.append = self.children.append

    def append(self, element):
        self.children.append(element)

    def add_to(self, handler):
        if self.contents or self.children:
            handler.startElement(self.tag_name, self.attrs)
            for element in self.children:
                element.add_to(handler)
            if self.contents is not None:
                handler.characters(self.contents)
            handler.endElement(self.tag_name)
        else:
            handler.addEmptyElement(self.tag_name, self.attrs)

class CustomXMLGenerator(SimplerXMLGenerator):
    """
    """
    def addEmptyElement(self, name, attrs=None):
        if attrs is None: attrs = {}
        self._write('<' + name)
        for name, value in attrs.iteritems():
            self._write(' %s=%s' % (name, quoteattr(value)))
        self._write('/>')

    def characters(self, content):
        # TODO: figure out how to do this explicitly rather than implicitly
        if any(c in content for c in CDATA_CHARS):
            self._write('<![CDATA[' + content + ']]>')
        else:
            # can't use super, XMLGenerator is an old style class
            SimplerXMLGenerator.characters(self, content)

class MediaRSSFeed(Rss201rev2Feed):
    """
    """
    def write(self, outfile, encoding):
        handler = CustomXMLGenerator(outfile, encoding)
        handler.startDocument()
        handler.startElement(u'rss', self.rss_attributes())
        handler.startElement(u'channel', self.root_attributes())
        self.add_root_elements(handler)
        self.write_items(handler)
        self.endChannelElement(handler)
        handler.endElement(u'rss')

    def rss_attributes(self):
        attrs = super(MediaRSSFeed, self).rss_attributes()
        attrs['xmlns:media'] = 'http://search.yahoo.com/mrss/'
        return attrs

    def add_item_elements(self, handler, item):
        super(MediaRSSFeed, self).add_item_elements(handler, item)
        for media_elem in item.get('media_list', ()):
            media_elem.add_to(handler)
