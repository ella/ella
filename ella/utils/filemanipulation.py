import shutil
import os

from django.conf import settings


def file_rename(old_path='', new_name='', new_ext=None, move=True):
    """
    Renames a file, keeping the extension.

    Parameters:

    * old_path: the file path relative to MEDIA_ROOT
    * new_name: the new basename of the file (no extension)
    * new_ext: adds new extension
    * move: do not move

    Returns the new file path on success.
    Returns the original old_path on error.

    inspired by: http://code.djangoproject.com/wiki/CustomUploadAndFilters
    """
    # return if no file or file_name given
    if not (old_path and new_name):
        return old_path

    # get important three parts
    dir_base, old_name, extension = split_path(old_path)

    if new_ext is None:
        # if new extension is not given, use old one
        new_ext = extension

    # to be sure createpath again
    old_file = old_name + extension
    new_file = new_name + new_ext
    old_absolute_path = os.path.join(settings.MEDIA_ROOT, dir_base, old_file)
    new_absolute_path = os.path.join(settings.MEDIA_ROOT, dir_base, new_file)

    # try to rename
    try:
        if move:
            shutil.move(old_absolute_path, new_absolute_path)
    except IOError:
        return old_path

    # return new relative path
    new_path = os.path.join(dir_base, new_file)
    return new_path


def split_path(file_path=''):
    """
    return triplet (dir_base, file_name, file_extension)
    """
    # to be sure, someone wasn't crazy enough
    file_path = file_path.replace('\\', '/')

    dir_base, file_full = os.path.split(file_path)
    file_name, file_extension = os.path.splitext(file_full)

    return (dir_base, file_name, file_extension,)

