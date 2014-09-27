from setuptools import setup #, find_packages

try:
    with open('README.md') as file:
        long_description = file.read()
except:
    long_description = "Deep Difference of dictionaries, iterables, strings and other objects. It will recursively look for all the changes."

setup(name='deepdiff',
      version='0.1',
      description='Deep Difference of dictionaries, iterables, strings and other objects. It will recursively look for all the changes.',
      url='https://github.com/erasmose/deepdiff',
      download_url='https://github.com/erasmose/deepdiff/tarball/master',
      author='Erasmose (Sep Dehpour)',
      author_email='sep@zepworks.com',
      license='MIT',
      packages=['deepdiff'],
      zip_safe=False,
      long_description=long_description,
      classifiers=[
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development"
        ],
      )