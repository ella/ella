import Image

def detect_img_type(imagePath):
    try:
        im = Image.open(imagePath)
        return im.format
    except IOError:
        return None

#       left    top   right  bottom
# box = x0,     y0,   x1,    y1
class Formatter(object):
    def __init__(self, image, format, crop_box=None, important_box=None):
        self.image = image
        self.fmt = format
        self.crop_box = crop_box
        self.important_box = important_box

        f = format
        fw, fh = f.max_width, f.max_height
        self.format_ratio = float(fw) / fh

    def get_crop_box(self):
        if self.fmt.nocrop:
            return

        if self.crop_box:
            return self.crop_box

        f = self.fmt
        fw, fh = f.max_width, f.max_height

        iw, ih = self.image.size
        image_ratio = float(iw) / ih

        if iw <= fw and ih <= fh:
            return

        if image_ratio < self.format_ratio:
            # image taller than format
            diff = ih - (iw * fh / fw)
            return (0, diff // 2 , iw, ih - diff // 2)

        elif image_ratio > self.format_ratio:
            # image wider than format
            diff = iw - (ih * fw / fh)
            return (diff // 2, 0, iw - diff // 2, ih)

        else:
            # same ratio as format
            return

    def crop_to_ratio(self):
        crop_box = self.get_crop_box()
        if not crop_box:
            return

        self.image = self.image.crop(crop_box)
    
    def get_resized_size(self):
        f = self.fmt
        fw, fh = f.max_width, f.max_height

        iw, ih = self.image.size
        image_ratio = float(iw) / ih

        if not f.stretch and iw <= fw and ih <= fh:
            return

        if image_ratio == self.format_ratio:
            # same ratio, just resize
            return (fw, fh)

        elif image_ratio < self.format_ratio:
            # image taller than format
            return (fh * iw / ih, fh)

        else: # image_ratio > self.format_ratio
            # image wider than format
            return (fw, fw * ih / iw)

    def resize(self):
        target_size = self.get_resized_size()

        resized_size = self.get_resized_size()
        if not resized_size:
            return

        self.image = self.image.resize(resized_size, Image.ANTIALIAS)

    def format(self):
        self.crop_to_ratio()
        self.resize()
        return self.image

        
