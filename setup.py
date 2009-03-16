from setuptools import setup, find_packages

setup(
    name = 'ella',
    version = '0.9',
    description = 'ella - django cms',
    long_description = '\n'.join((
        'ella project',
        'content management system written in django',
    )),
    author = 'centrum holdings s.r.o',
    license = 'BSD',

    packages = find_packages(
        where = '.',
        exclude = ('docs', 'tests')
    ),

    include_package_data = True,

    entry_points = {
        'setuptools.file_finders': ['dummy = setuptools_entry:dummylsfiles'],
    },

    install_requires = [
        'setuptools>=0.6b1',
    ],

    classifiers = [
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],

)

