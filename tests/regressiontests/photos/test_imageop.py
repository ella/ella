#from django.test.testcases import TestCase
import unittest
from ella.photos.imageop import *
import Image

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


class ImageopTestCase(unittest.TestCase):
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
        #im.save('/home/jonas.fiala/tmp/testik.png', 'PNG')
        self.iStretch = ImageStretch(image=im, formated_photo=self.__ff)


    def testCrop1(self):
        ''' Part one of ImageStretch.crop() test '''
        # don't crop
        img = self.iStretch
        res = img.crop_if_needed()
        self.assertEquals(img.image.tostring(), res.tostring())


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


    def testResizeIfNeeded(self):
        ff = self.__ff
        ff.format.max_width  = 88
        ff.format.max_height = 88
        ff.photo.width  = self.SIDE
        ff.photo.height = self.SIDE


    '''
    def testStretchDimension(self):
        res.save('/home/jonas.fiala/tmp/crop.png', 'PNG')
        pass


    def testCrop2Fit(self):
        pass


    def testStretchImage(self):
        pass
    '''


if __name__ == '__main__':
    unittest.main()
