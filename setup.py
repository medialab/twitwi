from setuptools import setup, find_packages

with open('./README.md', 'r') as f:
    long_description = f.read()

setup(name='twitwi',
      version='0.19.2',
      description='A collection of Twitter-related helper functions for python.',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='http://github.com/medialab/twitwi',
      license='MIT',
      author='Béatrice Mazoyer, Guillaume Plique, Benjamin Ooghe-Tabanou',
      author_email='guillaume.plique@sciencespo.fr',
      keywords='twitter',
      python_requires='>=3.4',
      packages=find_packages(exclude=['scripts', 'test']),
      package_data={'docs': ['README.md']},
      install_requires=[
        'pytz>=2019.3',
        'twitter==2.0a2',
        'ural>=0.31.1'
      ],
      zip_safe=True)
