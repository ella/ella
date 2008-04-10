from django.test.testcases import TestCase

from ella.photos.imageop import *
import Image, ImageDraw
from sets import Set
import settings

from ella.photos import models



'''
1. prepare images for comparison:
   source image,
   cropped/stretched images - right results of ImageStretch.generate() method)
2. stretch dimension, crop, stretch
3. compare
'''


class PhotoFake:
    title = None
    description = None
    slug = None
    image = None
    width = None
    height = None
    # Authors and Sources
    authors = []
    source = None
    created = None


class FormatFake:
    name = None
    max_width = None
    max_height = None
    flexible_height = False
    flexible_max_height = None
    stretch = False
    nocrop = False
    resample_quality = 85
    site = None


class FormatedPhotoFake:
    photo = PhotoFake()
    format = FormatFake()
    filename = None
    crop_left = None
    crop_top = None
    crop_width = None
    crop_height = None
    width = None
    height = None


class ImageopTestCase(TestCase):
    fixtures = ['photodata.json']
    '''
    100x100 pix x 3 bytes RGB
    X........X
    ..........
    ..........
    ..........
    ..........
    ..........
    ..........
    ..........
    ..........
    X........X
    '''
    POINT_TL = [ chr(255), chr(153), chr(5) ] #orange
    POINT_TR = [ chr(51),  chr(255), chr(5) ] #green
    POINT_BL = [ chr(255), chr(255), chr(255) ] #white
    POINT_BR = [ chr(36),  chr(5),   chr(107) ] #blue (dark)
    LINE_MIDDLE = [ chr(255), chr(0), chr(0) ] #red red red
    RGB_LINE_MIDDLE = '#ff0000'
    SIDE = 50

    def __imageData(self, size):
        ''' Generates image. Assumes image dimension is rectangular. '''
        #data = ''.join([chr(180) for x in range(30000)])
        height, width = size
        stdPix = (chr(90), chr(90), chr(180))
        data = ''
        for x in range(height * width):
            if x == 0:
                pix = self.POINT_BL
            elif x == width - 1:
                pix = self.POINT_BR
            elif x == (width * (height - 1)):
                pix = self.POINT_TL
            elif x == (width * height - 1):
                pix = self.POINT_TR
            else:
                pix = stdPix
            data += ''.join(pix)
        return data


    def __genPix(self, img):
        data = img.tostring()
        out  = []
        for x in data:
            out.append(x)
            if len(out) == 3:
                yield out
                out = []


    def setUp(self):
        self.__ff = FormatedPhotoFake()
        size = (self.SIDE, self.SIDE)
        im = Image.frombuffer('RGB', size, self.__imageData(size))
        draw = ImageDraw.Draw(im)
        width = size[0]
        coords = (width / 2, 0, width /2, width)
        draw.line(coords, fill=self.RGB_LINE_MIDDLE)
        coords = (0, width / 2, width, width / 2)
        draw.line(coords, fill=self.RGB_LINE_MIDDLE)
        im.save('%s/testik.png' % settings.MEDIA_ROOT, 'PNG')
        self.iStretch = ImageStretch(image=im, formated_photo=self.__ff)


    def testCrop1(self):
        ''' Part one of ImageStretch.crop() test '''
        # don't crop
        img = self.iStretch
        res = img.crop_if_needed()
        self.assertEquals(img.image.tostring(), res.tostring())
        #res.save('/home/jonas.fiala/tmp/crop1.png', 'PNG')


    def testCrop2(self):
        ''' Part two of ImageStretch.crop() test '''
        # should crop
        ff = self.__ff
        ff.crop_width = self.SIDE - 10
        ff.crop_height = self.SIDE - 10
        ff.crop_top = 0
        ff.crop_left = 0
        img = self.iStretch
        res = img.crop_if_needed()
        # top left corner should be visible only
        counter = 0
        tlFound = False
        for pix in self.__genPix(res):
            if pix == self.POINT_TL:
                tlFound = True
            if pix in [ self.POINT_TR, self.POINT_BL, self.POINT_BR ]:
                counter += 1
        self.assertTrue(tlFound)
        self.assertEquals(counter, 0)
        self.assertNotEquals(img.image.tostring(), res.tostring())
        #res.save('/home/jonas.fiala/tmp/crop2.png', 'PNG')


    def testResizeIfNeeded1(self):
        ff = self.__ff
        FORMAT_MAX = self.SIDE + 40 # larger than image size
        ff.format.max_width  = FORMAT_MAX
        ff.format.max_height = FORMAT_MAX
        ff.photo.width  = self.SIDE
        ff.photo.height = self.SIDE
        ff.format.stretch = True
        ff.crop_width = self.SIDE - 10
        ff.crop_height = self.SIDE - 10
        ff.crop_top = 0
        ff.crop_left = 0
        img = self.iStretch
        img._ImageStretch__cropped_photo = img.crop_if_needed()
        res = img.resize_if_needed()
        #res.save('/home/jonas.fiala/tmp/resize1.png', 'PNG')
        self.assertEquals(res.size, (FORMAT_MAX, FORMAT_MAX))


    def testResizeIfNeeded2(self):
        ff = self.__ff
        FORMAT_MAX = self.SIDE - 10 # smaller than image size, no resize needed
        ff.format.max_width  = FORMAT_MAX
        ff.format.max_height = FORMAT_MAX
        ff.photo.width  = self.SIDE
        ff.photo.height = self.SIDE
        ff.format.stretch = True
        ff.crop_width = self.SIDE - 10
        ff.crop_height = self.SIDE - 10
        ff.crop_top = 0
        ff.crop_left = 0
        img = self.iStretch
        img._ImageStretch__cropped_photo = img.crop_if_needed()
        res = img.resize_if_needed()
        self.assertEquals(res, None)


    def testStretchImage1(self):
        ff = self.__ff
        FORMAT_MAX = self.SIDE * 4
        ff.format.max_width  = FORMAT_MAX
        ff.format.max_height = FORMAT_MAX
        ff.photo.width  = self.SIDE
        ff.photo.height = self.SIDE
        ff.format.stretch = True
        ff.crop_width = 0
        ff.crop_height = 0
        ff.crop_top = 0
        ff.crop_left = 0
        img = self.iStretch
        res = img.stretch_image()
        #res.save('/home/jonas.fiala/tmp/stretch1.png', 'PNG')
        self.assertEquals(res.size, (FORMAT_MAX, FORMAT_MAX))
        # all color corners should be found
        counter = 0
        points = Set()
        for item in [ self.POINT_TL, self.POINT_TR, self.POINT_BL, self.POINT_BR ]:
            points.add(str(item))
        for pix in self.__genPix(res):
            if str(pix) in points:
                counter += 1
                points.remove(str(pix))
        self.assertEquals(counter, 4)


    def testStretchImage2(self):
        ff = self.__ff
        FORMAT_MAX = self.SIDE * 4
        ff.format.max_width  = FORMAT_MAX
        ff.format.max_height = FORMAT_MAX
        ff.photo.width  = self.SIDE
        ff.photo.height = self.SIDE
        ff.format.stretch = True
        ff.crop_width = self.SIDE - 1
        ff.crop_height = self.SIDE - 1
        ff.crop_top = 0
        ff.crop_left = 0
        img = self.iStretch
        res = img.stretch_image()
        #res.save('/home/jonas.fiala/tmp/stretch2.png', 'PNG')
        self.assertEquals(res.size, (FORMAT_MAX, FORMAT_MAX))
        # top left corner should be found
        tlFound = False
        for pix in self.__genPix(res):
            if pix == self.POINT_TL:
                tlFound = True
                break
        self.assertTrue(tlFound)




'''
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
'''


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

'''
__test__ = {
    'base' : base,
    'img_tag' : img_tag,
}

if __name__ == '__main__':
    import doctest
    doctest.testmod()
'''
