from setuptools import setup, find_packages
import djangobaselibrary

version = "%d.%d.%d" % djangobaselibrary.VERSION

setup(
    name = 'djangobaselibrary',
    version = version,
    description = 'django base library',
    long_description = '\n'.join((
        'django base library',
        'template for other libs',
    )),
    author = 'centrum holdings s.r.o',
    author_email = 'author_email@example.com',
    license = 'BSD',
    url = 'http://example.com',

    packages = find_packages(
        where = '.',
        exclude = ('docs', 'tests')
    ),

    include_package_data = True,

    entry_points={
        'setuptools.file_finders': ['dummy = setuptools_entry:dummylsfiles'],
    },

    install_requires = [
        'setuptools>=0.6b1',
    ],

    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)

