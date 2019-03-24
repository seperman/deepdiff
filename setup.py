import os
import re
import sys
from setuptools import setup

if sys.version[0] == '2':  # pragma: no cover
    sys.exit('Python 2 is not supported anymore. The last version of DeepDiff that supported Py2 was 3.3.0')

# if you are not using vagrant, just delete os.link directly,
# The hard link only saves a little disk space, so you should not care
if os.environ.get('USER', '') == 'vagrant':
    del os.link


VERSIONFILE = "deepdiff/__init__.py"
with open(VERSIONFILE, "r") as the_file:
    verstrline = the_file.read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))


def get_reqs(filename):
    with open(filename, "r") as reqs_file:
        reqs = reqs_file.readlines()
        reqs = list(map(lambda x: x.replace('==', '>='), reqs))
    return reqs


reqs = get_reqs("requirements.txt")

with open('README.md') as file:
    long_description = file.read()


setup(name='deepdiff',
      version=verstr,
      description='Deep Difference and Search of any Python object/data.',
      url='https://github.com/seperman/deepdiff',
      download_url='https://github.com/seperman/deepdiff/tarball/master',
      author='Seperman',
      author_email='sep@zepworks.com',
      license='MIT',
      packages=['deepdiff'],
      zip_safe=True,
      test_suite="tests",
      include_package_data=True,
      tests_require=['mock'],  # 'numpy==1.11.2' numpy is needed but comes already installed with travis
      long_description=long_description,
      long_description_content_type='text/markdown',
      install_requires=reqs,
      python_requires='>=3.4',
      classifiers=[
          "Intended Audience :: Developers",
          "Operating System :: OS Independent",
          "Topic :: Software Development",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7",
          "Programming Language :: Python :: Implementation :: PyPy",
          "Development Status :: 5 - Production/Stable",
          "License :: OSI Approved :: MIT License"
      ],
      )
