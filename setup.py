from setuptools import setup, find_packages
import ella

# all fields marked with TODO: REPLACE
# must be filled with some meanigful values

VERSION = (0, 0, 0, 0)
__version__ = VERSION
__versionstr__ = '.'.join(map(str, VERSION))

setup(
    name = 'ella',
    version = __versionstr__,
    description = 'Ella Django CMS Project', # TODO: REPLACE
    long_description = '\n'.join((
        'Ella Django CMS Project',
        '',
        'this project (python module) is meant as a template',
        'for any centrumholdings django based',
        '(even non-django, pure python) libraries',
    )),
    author = 'centrum holdings s.r.o', # TODO: REPLACE
    author_email='devel@centrumholdings.com', # TODO: REPLACE
    license = 'BSD', # TODO: REPLACE
    url='http://git.netcentrum.cz/projects/django/GIT/ella.git/', # TODO: REPLACE

    packages = find_packages(
        where = '.',
        exclude = ('docs', 'tests')
    ),

    include_package_data = True,

    # TODO: REPLACE
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
    install_requires = [
        'setuptools>=0.6b1',
    ],
    setup_requires = [
        'setuptools_dummy',
    ],
)

