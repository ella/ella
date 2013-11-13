from PIL import Image, ExifTags

from ella.photos.conf import photos_settings

TAGS = dict((b,a) for a,b in ExifTags.TAGS.items())

class Formatter(object):
    def __init__(self, image, format, crop_box=None, important_box=None):
        self.image = image
        self.fmt = format
        self.crop_box = crop_box
        self.important_box = important_box

        # precompute and store a bunch of numbers
        f = format
        self.fw, self.fh = f.max_width, f.max_height
        self.format_ratio = float(self.fw) / self.fh

        iw, ih = self.image.size
        self.image_ratio = float(iw) / ih

    def format(self):
        """
        Crop and resize the supplied image. Return the image and the crop_box used.
        If the input format is JPEG and in EXIF there is information about rotation, use it and rotate resulting image.
        """
        if hasattr(self.image, '_getexif'):
            self.rotate_exif()
        crop_box = self.crop_to_ratio()
        self.resize()
        return self.image, crop_box

    def set_format(self):
        """
        Check if the format has a flexible height, if so check if the ratio
        of the flexible format is closer to the actual ratio of the image. If
        so use that instead of the default values (f.max_width, f.max_height).
        """
        f = self.fmt

        if f.flexible_height and f.flexible_max_height:
            flexw, flexh = self.fw, f.flexible_max_height
            flex_ratio = float(flexw) / flexh

            if abs(flex_ratio - self.image_ratio) < abs(self.format_ratio - self.image_ratio):
                self.fh = flexh
                self.format_ratio = flex_ratio

    def get_crop_box(self):
        """
        Get coordinates of the rectangle defining the new image boundaries. It
        takes into acount any specific wishes from the model (explicitely
        passed in crop_box), the desired format and it's options
        (flexible_height, nocrop) and mainly it's ratio. After dimensions of
        the format were specified (see set_format), crop the image to the same
        ratio.
        """

        # check if the flexible height option is active and applies
        self.set_format()


        if self.fmt.nocrop:
            # cropping not allowed
            return

        if self.crop_box:
            # crop coordinates passed in explicitely
            return self.crop_box

        iw, ih = self.image.size

        if iw <= self.fw and ih <= self.fh:
            # image fits in the target format, no need to crop
            return

        if self.image_ratio < self.format_ratio:
            # image taller than format
            diff = ih - (iw * self.fh / self.fw)
            return (0, diff // 2 , iw, ih - diff // 2)

        elif self.image_ratio > self.format_ratio:
            # image wider than format
            diff = iw - (ih * self.fw / self.fh)
            return (diff // 2, 0, iw - diff // 2, ih)

        else:
            # same ratio as format
            return

    def center_important_part(self, crop_box):
        """
        If important_box was specified, make sure it lies inside the crop box.
        """
        if not self.important_box:
            return crop_box

        # shortcuts
        ib = self.important_box
        cl, ct, cr, cb = crop_box
        iw, ih = self.image.size

        # compute the move of crop center onto important center
        move_horiz = (ib[0] + ib[2]) // 2 - (cl + cr) // 2
        move_verti = (ib[1] + ib[3]) // 2 - (ct + cb) // 2

        # make sure we don't get out of the image
        # ... horizontaly
        if move_horiz > 0:
            move_horiz = min(iw - cr, move_horiz)
        else:
            move_horiz = max(-cl, move_horiz)

        # .. and verticaly
        if move_verti > 0:
            move_verti = min(ih - cb, move_verti)
        else:
            move_verti = max(-ct, move_verti)

        # move the crop_box
        return (cl + move_horiz, ct + move_verti, cr + move_horiz, cb + move_verti)


    def crop_to_ratio(self):
        " Get crop coordinates and perform the crop if we get any. "
        crop_box = self.get_crop_box()

        if not crop_box:
            return

        crop_box = self.center_important_part(crop_box)

        iw, ih = self.image.size
        # see if we want to crop something from outside of the image
        out_of_photo = min(crop_box[0], crop_box[1]) < 0 or crop_box[2] > iw or crop_box[3] > ih
        # check whether there's transparent information in the image
        transparent = self.image.mode in ('RGBA', 'LA')

        if photos_settings.DEFAULT_BG_COLOR != 'black' and out_of_photo and not transparent:
            # if we do, just crop the image to the portion that will be visible
            updated_crop_box = (
                max(0, crop_box[0]), max(0, crop_box[1]), min(iw, crop_box[2]), min(ih, crop_box[3]),
            )
            cropped = self.image.crop(updated_crop_box)

            # create new image of the proper size and color
            self.image = Image.new('RGB', (crop_box[2] - crop_box[0], crop_box[3] - crop_box[1]), photos_settings.DEFAULT_BG_COLOR)
            # and paste the cropped part into it's proper position
            self.image.paste(cropped, (abs(min(crop_box[0], 0)), abs(min(crop_box[1], 0))))
        else:
            # crop normally if not the case
            self.image = self.image.crop(crop_box)
        return crop_box

    def get_resized_size(self):
        """
        Get target size for the stretched or shirnked image to fit within the
        target dimensions. Do not stretch images if not format.stretch.

        Note that this method is designed to operate on already cropped image.
        """
        f = self.fmt
        iw, ih = self.image.size

        if not f.stretch and iw <= self.fw and ih <= self.fh:
            return

        if self.image_ratio == self.format_ratio:
            # same ratio, just resize
            return (self.fw, self.fh)

        elif self.image_ratio < self.format_ratio:
            # image taller than format
            return (self.fh * iw / ih, self.fh)

        else: # self.image_ratio > self.format_ratio
            # image wider than format
            return (self.fw, self.fw * ih / iw)

    def resize(self):
        """
        Get target size for a cropped image and do the resizing if we got
        anything usable.
        """
        resized_size = self.get_resized_size()
        if not resized_size:
            return

        self.image = self.image.resize(resized_size, Image.ANTIALIAS)

    def rotate_exif(self):
        """
        Rotate image via exif information.
        Only 90, 180 and 270 rotations are supported.
        """
        exif = self.image._getexif() or {}
        rotation = exif.get(TAGS['Orientation'], 1)

        rotations = {
            6: -90,
            3: -180,
            8: -270,
        }
        if rotation not in rotations:
            return

        self.image = self.image.rotate(rotations[rotation])

