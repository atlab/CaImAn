from setuptools import setup
from os import path
#import os
import numpy as np
from Cython.Build import cythonize

"""
    Installation script for anaconda installers
"""

here = path.abspath(path.dirname(__file__))

setup(
    name='CaImAn',
    version='0.1',
    author='Andrea Giovannucci, Eftychios Pnevmatikakis, Johannes Friedrich, Valentina Staneva, Ben Deverett',
    author_email='agiovannucci@simonsfoundation.org',
    url='https://github.com/agiovann/Constrained_NMF',
    license='GPL-2',
    description='Advanced algorithms for ROI detection and deconvolution of Calcium Imaging datasets.',
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Testers',
        'Topic :: Calcium Imaging :: Analysis Tools',
        'License :: OSI Approved :: GPL-2 License',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='fluorescence calcium ca imaging deconvolution ROI identification',
    packages=['caiman'],
    data_files=[	('', ['LICENSE.txt']),
                 ('', ['README.md'])],
    include_dirs=[np.get_include()],
    ext_modules=cythonize("caiman/source_extraction/cnmf/oasis.pyx")

)
