from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='footparse',
      version='0.1',
      description='A collection of parsers for football websites.',
      long_description=readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
      ],
      keywords='football soccer parse scrape exctract website elo data results stats',
      url='https://github.com/kickoffai/footparse',
      author='Lucas Maystre',
      author_email='lucas@maystre.ch',
      license='MIT',
      packages=['footparse'],
      install_requires=[
          'requests',
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      include_package_data=True,
      zip_safe=False)
