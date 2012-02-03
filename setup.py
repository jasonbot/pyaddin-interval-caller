from distutils.core import setup

setup(name='tickextension',
      version='1.0',
      description=('Event loop hook to allow ArcGIS Add-In Extensions '
                   'written in Python to be called at regular intervals'),
      author='Jason Scheirer',
      author_email='jscheirer@esri.com',
      packages=['tickextension']
     )
