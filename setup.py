from setuptools import setup, find_packages
import ella

install_requires = [
    'setuptools>=0.6b1',
    'Django<1.7',
    'south>=0.7',
    'Pillow',
    'pytz',
    'django-appdata>=0.1.0',
]

tests_require = [
    'nose',
    'coverage',
    'mock',
    'feedparser',
    'redis',
]

long_description = open('README.rst').read()

setup(
    name='ella',
    version=ella.__versionstr__,
    description='Ella - Django powered CMS',
    long_description=long_description,
    author='Ella Development Team',
    author_email='dev@ella-cms.com',
    license='BSD',
    url='https://github.com/ella/ella',

    packages=find_packages(
        where='.',
        exclude=('doc', 'test_ella', )
    ),

    include_package_data=True,

    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=install_requires,

    test_suite='test_ella.run_tests.run_all',
    tests_require=tests_require,
)
