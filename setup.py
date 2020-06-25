from setuptools import setup, find_packages

install_requires = [
    'panel',
    'param',
    'holoviews',
    'xarray',
    'pyproj',
]

setup(
    name='covid_dashboard',
    version='0.0.0',
    packages=find_packages(),
    install_requires=install_requires,
)
