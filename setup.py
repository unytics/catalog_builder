import setuptools


VERSION = '0.7'


with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()


setuptools.setup(
    name='catalog_builder',
    packages=['catalog_builder'],
    version=VERSION,
    author='Unytics',
    author_email='paul.marcombes@unytics.io',
    description='Data Catalogs Made Easy',
    long_description=long_description,
    long_description_content_type='text/markdown',
    download_url=f'https://github.com/unytics/catalog_builder/archive/refs/tags/v{VERSION}.tar.gz',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        'mkdocs-material',
        'mkdocs-awesome-pages-plugin',
        'click',
        'click-help-colors',
        'pyarrow',
        'pandas',
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'catalog = catalog_builder.cli:cli',
        ],
    },
)