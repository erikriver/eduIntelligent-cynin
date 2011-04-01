from setuptools import setup, find_packages
import os

version = '0.2'

setup(name='eduintelligent.zipcontent',
      version=version,
      description="Static content in zip",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        ],
      keywords='zip file publish',
      author='Erik Rivera Morales',
      author_email='erik@iservices.com.mx',
      url='http://www.iservices.com.mx/',
      license='LGPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['eduintelligent'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
