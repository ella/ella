import Image

from ella.utils.filemanipulation import file_rename



def detect_img_type(imagePath):
    try:
        im = Image.open(imagePath)
        return im.format
    except IOError:
        return None

def get_img_size(imagePath):
    """ returns tuple (width, height) of image """
    try:
        import pdb; pdb.set_trace()
        im = Image.open(imagePath)
        return {
            'width': im.size[0],
            'height': im.size[1]
}
    except IOError:
        return None

class ImageOperation(object):

    def __init__(self, **kwargs):
        self.image = None
        if 'filename' in kwargs:
            self.open_image(kwargs['filename'])
        elif 'image' in kwargs:
            self.image = kwargs['image']

    def open_image(self, filename):
        ''' Nacte obrazek. Vraci image objekt (PIL). '''
        self.image = Image.open(filename)

    def save_image(self, image, filename, format='JPEG', **kwargs):
        self.image.save(filename, format, **kwargs)

class ImageStretch(ImageOperation):

    def __init__(self, **kwargs):
        ImageOperation.__init__(self, **kwargs)
        if not 'formated_photo' in kwargs:
            raise KeyError('formated_photo kwarg missing!')
        self.__fpi = kwargs['formated_photo']

    def __get_stretch_dimension(self, flex=False):
        """ Method return stretch dimension of crop to fit inside max format rectangle """
        fpi = self.__fpi
        # TODO: compensate for rounding error
        self.__fmt_width = fpi.format.max_width
        if flex:
            self.__fmt_height = fpi.format.flexible_max_height
        else:
            self.__fmt_height = fpi.format.max_height

        crop_ratio = float(fpi.crop_width) / fpi.crop_height
        self.__format_ratio = float(self.__fmt_width) / self.__fmt_height
        if self.__format_ratio < crop_ratio :
            stretch_width = self.__fmt_width
            stretch_height = min(self.__fmt_height, int(stretch_width / crop_ratio)) # dimension must be integer
        else: #if(fpi.photo.ratio() < fpi.crop_ratio()):
            stretch_height = self.__fmt_height
            stretch_width = min(self.__fmt_width, int(stretch_height * crop_ratio))
        return (stretch_width, stretch_height)

    def resize_if_needed(self):
        cropped_photo = self.__cropped_photo
        fpi = self.__fpi
        # we don't have to resize the image if stretch isn't specified and the image fits within the format
        if fpi.crop_width < fpi.format.max_width and fpi.crop_height < fpi.format.max_height:
            if not fpi.format.stretch:
                return cropped_photo
            # resize image to fit format
            if self.__auto and not fpi.format.nocrop:
                if self.__my_ratio > self.__format_ratio:
                    diff = fpi.photo.width - (self.__fmt_width * fpi.photo.height / self.__fmt_height)
                    fpi.crop_left = diff / 2
                    fpi.crop_width = fpi.photo.width - diff
                    cropped_photo = cropped_photo.crop((fpi.crop_left, fpi.crop_top, fpi.crop_left + fpi.crop_width, fpi.crop_top + fpi.crop_height))

                elif self.__my_ratio < self.__format_ratio:
                    diff = fpi.photo.height - (self.__fmt_height * fpi.photo.width / self.__fmt_width)
                    fpi.crop_top = diff / 2
                    fpi.crop_height = fpi.photo.height - diff
                    cropped_photo = cropped_photo.crop((fpi.crop_left, fpi.crop_top, fpi.crop_left + fpi.crop_width, fpi.crop_top + fpi.crop_height))

            return cropped_photo.resize(self.__get_stretch_dimension(), Image.ANTIALIAS)
        else:
            return None

    def crop_to_fit(self):
        # crop image to fit
        cropped_photo = self.__cropped_photo
        fpi = self.__fpi
        stretched_photo = None
        if fpi.crop_width > fpi.format.max_width or fpi.crop_height > fpi.format.max_height:
            flex = False
            if self.__auto and not fpi.format.nocrop:
                # crop the image to conform to the format ration
                if self.__my_ratio < self.__format_ratio and fpi.format.flexible_height:
                        self.__format_ratio2 = float(self.__fmt_width) / fpi.format.flexible_max_height
                        if self.__my_ratio < self.__format_ratio2 or abs(self.__format_ratio - self.__my_ratio) > abs(self.__format_ratio2 - self.__my_ratio):
                            flex = True
                            self.__fmt_height = fpi.format.flexible_max_height
                            self.__format_ratio = float(self.__fmt_width) / self.__fmt_height

                if self.__my_ratio > self.__format_ratio:
                    diff = fpi.photo.width - (self.__fmt_width * fpi.photo.height / self.__fmt_height)
                    fpi.crop_left = diff / 2
                    fpi.crop_width = fpi.photo.width - diff
                    cropped_photo = cropped_photo.crop((fpi.crop_left, fpi.crop_top, fpi.crop_left + fpi.crop_width, fpi.crop_top + fpi.crop_height))

                elif self.__my_ratio < self.__format_ratio:
                    diff = fpi.photo.height - (self.__fmt_height * fpi.photo.width / self.__fmt_width)
                    fpi.crop_top = diff / 2
                    fpi.crop_height = fpi.photo.height - diff
                    cropped_photo = cropped_photo.crop((fpi.crop_left, fpi.crop_top, fpi.crop_left + fpi.crop_width, fpi.crop_top + fpi.crop_height))

                if fpi.crop_width < self.__fmt_width and fpi.crop_height < self.__fmt_height:
                    if fpi.format.stretch:
                        # resize image to fit format
                        stretched_photo = cropped_photo.resize(self.__get_stretch_dimension(flex), Image.ANTIALIAS)
                    else:
                        stretched_photo = cropped_photo
            if stretched_photo is None:
            # shrink the photo to fit the format
                return cropped_photo.resize(self.__get_stretch_dimension(flex), Image.ANTIALIAS)
        else:
            return None

    def crop_if_needed(self):
        fpi = self.__fpi
        source = self.image
        # if crop specified
        if fpi.crop_width and fpi.crop_height:
            # generate crop
            cropBox = (fpi.crop_left, fpi.crop_top, fpi.crop_left + fpi.crop_width, fpi.crop_top + fpi.crop_height)
            cropped_photo = source.crop(cropBox)
            self.__auto = False
        else: # else stay original
            fpi.crop_left, fpi.crop_top = 0, 0
            fpi.crop_width, fpi.crop_height = source.size
            cropped_photo = source
            self.__auto = True
        return cropped_photo

    def stretch_image(self):
        ''' Stretchne obrazek a vrati ho. '''
        fpi = self.__fpi
        source = self.image
        # if crop specified
        self.__cropped_photo = self.crop_if_needed()
        self.__fmt_width = fpi.format.max_width
        self.__fmt_height = fpi.format.max_height
        self.__my_ratio = float(fpi.photo.width) / fpi.photo.height
        self.__format_ratio = float(self.__fmt_width) / self.__fmt_height

        resized = self.resize_if_needed()
        cropped = self.crop_to_fit()
        if resized:
            stretched_photo = resized
        elif cropped:
            stretched_photo = cropped
        else:
            stretched_photo = self.__cropped_photo
        return stretched_photo
