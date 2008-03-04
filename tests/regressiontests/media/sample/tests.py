
media_queue_test = r"""
>>> from ella.media.queue import dummy
>>> import doctest
>>> doctest.testmod(dummy)
(0, 12)

"""

media_upload_test = r"""

clean test dir, create test file

>>> import os, shutil
>>> from django.conf import settings

>>> shutil.rmtree(settings.UPLOAD_ROOT, True)
>>> os.makedirs(settings.UPLOAD_ROOT)

>>> file_name = os.path.join(settings.UPLOAD_ROOT, 'media_upload_test.txt')
>>> f = open(file_name, 'w')
>>> f.write('abcd' * 10 ** 3)
>>> f.close()

emulate upload of a file

>>> from ella.media.uploader.models import Upload
>>> from ella.media.models import Media, FormattedFile

>>> Upload.objects.count() == Media.objects.count() == FormattedFile.objects.count() == 0
True
>>> u = Upload(file=file_name, title='test file', type='file')
>>> u.save()
COMMAND:
mkdir -p /tmp/upload/
head -c10 /tmp/upload//894aa55a08ddb4e0e94fa50348ddd5fa3ea58a3f > /tmp/upload//894aa55a08ddb4e0e94fa50348ddd5fa3ea58a3f-head_C10
OUTPUT:
<BLANKLINE>
STATUS:
0
<BLANKLINE>
<BLANKLINE>
COMMAND:
mkdir -p /tmp/upload/
head -c20 /tmp/upload//894aa55a08ddb4e0e94fa50348ddd5fa3ea58a3f > /tmp/upload//894aa55a08ddb4e0e94fa50348ddd5fa3ea58a3f-head_C20
OUTPUT:
<BLANKLINE>
STATUS:
0
<BLANKLINE>
<BLANKLINE>
>>> Upload.objects.values('hash')
[{'hash': u'894aa55a08ddb4e0e94fa50348ddd5fa3ea58a3f'}]
>>> Media.objects.values('hash')
[{'hash': u'894aa55a08ddb4e0e94fa50348ddd5fa3ea58a3f'}]
>>> FormattedFile.objects.values('hash')
[{'hash': u'0c6fc1f631cba5ba7209adf34e8ddfb9fda27258'}, {'hash': u'b323823bd53410fe55c8154b1f63564815da3592'}]

"""


__test__ = {
    'media_queue_test': media_queue_test,
    'media_upload_test': media_upload_test,
}


if __name__ == '__main__':
    import doctest
    doctest.testmod()

