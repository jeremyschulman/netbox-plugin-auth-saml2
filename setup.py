from setuptools import find_packages, setup

setup(
    name='netbox-plugin-auth-saml2',
    version='2.0',
    description='Netbox plugin for SAML2 auth',
    author='Jeremy Schulman',
    license='Apache 2.0',
    install_requires=[],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
