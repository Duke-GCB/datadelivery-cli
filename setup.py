from setuptools import setup

setup(name='datadelivery',
      version='0.0.1',
      description='Command line tool to facility delivery of s3 buckets to other users via D4S2.',
      author='John Bradley',
      license='MIT',
      packages=['datadelivery'],
      install_requires=[
          'requests',
          'PyYAML'
      ],
      entry_points={
          'console_scripts': [
              'datadelivery = datadelivery.__main__:main'
          ]
      },
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Science/Research',
          'Topic :: Utilities',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
      ],
      )
