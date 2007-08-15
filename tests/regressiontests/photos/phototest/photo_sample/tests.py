from django.test.testcases import TestCase

class PhotoUploadTestCase(TestCase):
    fixtures = [ '', '', ]

    def setUp(self):
        pass

    def testUpload(self):
        self.assertTrue(False, 'UAAA')

    def testCropping(self):
        self.assertTrue(False, 'UAAA')

    def tearDown(self):
        self.assertTrue(False, 'UAAA')



base = r'''
>>> 10
1
'''

img_tag = r'''
>>> 10
1
# existing formated foto

# non existing format

'''

__test__ = {
    'base' : base,
    'img_tag' : img_tag,
}

if __name__ == '__main__':
    import doctest
    doctest.testmod()

