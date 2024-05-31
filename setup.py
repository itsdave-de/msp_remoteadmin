from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in msp_remoteadmin/__init__.py
from msp_remoteadmin import __version__ as version

setup(
	name="msp_remoteadmin",
	version=version,
	description="Remote connection management application to servers configured in the MSP",
	author="Luiz Costa",
	author_email="l.costa@itsdave.de",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
