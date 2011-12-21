import datetime
import locale
from cStringIO import StringIO

from djangosanetesting import UnitTestCase

from ella.utils.feedgenerator import MediaElement, CustomXMLGenerator, MediaRSSFeed

PUB_DATE = datetime.datetime(2012, 12, 23)
ENCODING = locale.getpreferredencoding()

MEDIA_FEED = """\
<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:atom="http://www.w3.org/2005/Atom" version="2.0" xmlns:media="http://search.yahoo.com/mrss/">\
<channel>\
<title>title</title>\
<link>link</link>\
<description>description</description>\
<atom:link href="url" rel="self"></atom:link>\
<lastBuildDate>Sun, 23 Dec 2012 00:00:00 -0000</lastBuildDate>\
<item>\
<title>title</title>\
<link>link</link>\
<description>description</description>\
<pubDate>Sun, 23 Dec 2012 00:00:00 -0000</pubDate>\
</item>\
</channel>\
</rss>"""

class TestFeedGenerator(UnitTestCase):
    """
    """
    def test_empty_tag(self):
        outfile = StringIO()
        handler = CustomXMLGenerator(outfile, ENCODING)
        handler.addEmptyElement(u'a')
        self.assert_equals('<a/>', outfile.getvalue())
        outfile.close()

    def test_empty_tag_with_attributes(self):
        outfile = StringIO()
        handler = CustomXMLGenerator(outfile, ENCODING)
        handler.addEmptyElement(u'a', {'b': 'c'})
        self.assert_equals('<a b="c"/>', outfile.getvalue())
        outfile.close()

    def test_cdata_contents(self):
        outfile = StringIO()
        handler = CustomXMLGenerator(outfile, ENCODING)
        handler.addQuickElement(u'a', '<>')
        self.assert_equals('<a><![CDATA[<>]]></a>', outfile.getvalue())
        outfile.close()

class TestMediaFeed(UnitTestCase):
    """
    """
    def test_media_element(self):
        outfile = StringIO()
        handler = CustomXMLGenerator(outfile, ENCODING)
        root = MediaElement('root')
        elem = MediaElement('a', 'd', {'b': 'c'})
        root.append(elem)
        root.add_to(handler)
        self.assert_equals('<root><a b="c">d</a></root>', outfile.getvalue())
        outfile.close()

    def test_media_feed(self):
        outfile = StringIO()
        feed = MediaRSSFeed('title', 'link', 'description', feed_url='url')
        feed.add_item('title', 'link', 'description', pubdate=PUB_DATE)
        feed.write(outfile, ENCODING)
        self.assert_equals(outfile.getvalue(), MEDIA_FEED)
        outfile.close()
