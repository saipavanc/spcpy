# setup.py

from setuptools import setup, find_packages

setup(
    name='spcpy',
    version='0.0.0',
    packages=find_packages(),
    install_requires=[
        # List your package dependencies here, e.g.,
        'numpy',
        # 'requests',
    ],
    author='Sai Pavan Chitta',
    author_email='saipavanchitta1998@gmail.com',
    description='Collection of methods and tools, some misc, mostly for numerical simulations.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/saipavanc/spcpy',  # Replace with your repository URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # Change if you use a different license
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
