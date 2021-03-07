from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='netbox-plugin-auth-saml2',
    version='2.3',
    description='Netbox plugin for SAML2 auth',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Jeremy Schulman',
    license='Apache 2.0',
    install_requires=[],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
