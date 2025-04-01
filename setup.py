from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in homegenie_custom_app/__init__.py
from homegenie_custom_app import __version__ as version

setup(
	name="homegenie_custom_app",
	version=version,
	description="Custom Fields",
	author="Homegenie",
	author_email="test@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
