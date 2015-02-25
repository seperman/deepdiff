from setuptools import setup

try:
    with open('README.txt') as file:
        long_description = file.read()
except:
    long_description = "Deep Difference of dictionaries, iterables, strings and other objects. It will recursively look for all the changes."

setup(name='deepdiff',
      version='0.2.0',
      description='Deep Difference of dictionaries, iterables, strings and other objects. It will recursively look for all the changes.',
      url='https://github.com/erasmose/deepdiff',
      download_url='https://github.com/erasmose/deepdiff/tarball/master',
      author='Seperman',
      author_email='sep@zepworks.com',
      license='MIT',
      packages=['deepdiff'],
      # install_requires=['future', 'six'], # only when python 3
      zip_safe=False,
      long_description=long_description,
      classifiers=[
          "Intended Audience :: Developers",
          "Operating System :: OS Independent",
          "Topic :: Software Development",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.4",
          "Development Status :: 4 - Beta"
      ],
      )
