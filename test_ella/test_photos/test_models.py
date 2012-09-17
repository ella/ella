from django.test import TestCase

from ella.core.models import Source
from ella.photos.models import Photo

from ella.utils.test_helpers import create_photo

from nose import tools

class TestPhotoModel(TestCase):
    " Unit tests for `ella.photos.models.Photo` model. "
    def setUp(self):
        super(TestPhotoModel, self).setUp()

        # Make a few simple assertions regarding the state of the test data
        tools.assert_equals(Source.objects.count(), 0)
        tools.assert_equals(Photo.objects.count(), 0)

        # Create a Source and Category for the tests
        self.source_foo = Source.objects.create(name='foo')
        tools.assert_equals(Source.objects.count(), 1)

    def test_source_is_nulled_on_delete(self):
        """
        Assert that the Source field for Photos are
        set to null (and not deleted) when a `Source` is deleted.
        """
        # Create a new Photo and associate it to the `foo` source
        photo = create_photo(self, source=self.source_foo)
        tools.assert_equals(Photo.objects.count(), 1)

        # Delete the `source`
        self.source_foo.delete()

        # Assert that the photo remains, but the `source` field is nulled
        tools.assert_equals(Photo.objects.count(), 1)
        tools.assert_equals(Source.objects.count(), 0)
        photo = Photo.objects.get(id=photo.id)
        tools.assert_equals(photo.source, None)
