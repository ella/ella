import os

def change_basename(file_path, new_name):
    # Extract path: 'news/img'
    path = os.path.dirname(file_path)

    # Extract current name: 'name.jpg'
    curr_name = os.path.basename(file_path)
    # Split file name and extension: 'name', '.jpg'
    original, ext = os.path.splitext(curr_name)

    # Return the new path: 'news/img/new_name.jpg'
    return os.path.join(path, new_name + ext).replace('\\', '/')

# def change_basename

def add_to_basename(file_path, str):
    # Extract path: 'news/img'
    path = os.path.dirname(file_path)

    # Extract current name: 'name.jpg'
    curr_name = os.path.basename(file_path)
    # Split file name and extension: 'name', '.jpg'
    original, ext = os.path.splitext(curr_name)

    # Return the new path: 'news/img/originalstr.jpg'
    return os.path.join(path, original + str + ext).replace('\\', '/')

# def add_to_basename
