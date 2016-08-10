from setuptools import setup, find_packages

efetch_description = (
    u'Efetch is a plugin based web api for viewing and analyzing files using the dfVFS pathspec.'
)

setup(
    name=u'efetch',
    version=u'0.6 Alpha',
    descript=efetch_description,
    packages=find_packages(),
    url=u'https://github.com/maurermj08/efetch',
    license=u'Apache License Version 2.0',
    author=u'Michael Maurer',
    classifiers=[
        u'Development Status :: 4 - Beta',
        u'Environment :: Web Environment',
        u'Operating System :: OS Independent',
        u'Programming Language :: Python',
    ],
    install_requires=frozenset([u'argparse>=1.2.1',
                      u'bottle>=0.12.8',
                      u'dfvfs>=20150708',
                      u'elasticsearch>=2.1.0',
                      u'pefile>=1.2.10_139',
                      u'Yapsy>=1.11.223',
                      u'Pillow>=3.3.0',
                      u'Registry>=0.4.2',
                      u'python_magic>=0.4.12',
                      u'Requests>=2.10.0',
                      u'cherrypy>=5.0.0',
                      u'ExifRead>=2.1.0',
                      u'rison>=1.0',
                      u'python-registry>=1.0']),
    dependency_links=[u'https://github.com/maurermj08/rison/tarball/master#egg=rison-1.1',
                      u'https://github.com/williballenthin/python-registry/tarball/master#egg=python-registry-1.2'],
    author_email=u'maurermj08@gmail.com',
)