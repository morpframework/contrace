from setuptools import setup, find_packages
import sys
import os

version = '0.1.0'

setup(name='contrace',
      version=version,
      description="",
      long_description="""\
      """,
      classifiers=[],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Contrace Team',
      author_email='no-reply@kagesenshi.org',
      url='http://github.com/morpframework/contrace',
      license='GPLv3+',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      python_requires=">=3.7",
      install_requires=[
          # -*- Extra requirements: -*-
          'morpfw>=0.2.1rc4',
          # 
          'morpcc>=0.1.0a3'
          # 
      ],
      extras_require={
          'test': [
              'morpfw[test]',
          ]
      },
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
