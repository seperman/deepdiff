import os
from setuptools import setup

# if you are not using vagrant, just delete os.link directly,
# The hard link only saves a little disk space, so you should not care
if os.environ.get('USER','') == 'vagrant':
    del os.link

try:
    with open('README.txt') as file:
        long_description = file.read()
except:
    long_description = "Deep Difference of dictionaries, iterables, strings and other objects. It will recursively look for all the changes."

setup(name='deepdiff',
      version='0.6.1',
      description='Deep Difference of dictionaries, iterables, strings and other objects. It will recursively look for all the changes.',
      url='https://github.com/seperman/deepdiff',
      download_url='https://github.com/seperman/deepdiff/tarball/master',
      author='Seperman',
      author_email='sep@zepworks.com',
      license='MIT',
      packages=['deepdiff'],
      zip_safe=False,
      long_description=long_description,
      classifiers=[
          "Intended Audience :: Developers",
          "Operating System :: OS Independent",
          "Topic :: Software Development",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.4",
          "Development Status :: 5 - Production/Stable",
          "License :: OSI Approved :: MIT License"
      ],
      )
