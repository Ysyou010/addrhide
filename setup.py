from setuptools import setup, find_packages

setup(
    name='addrhide',
    version='1.0.0',
    description='M3U API Key Hiding Proxy Plugin',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests',
        'flask'
    ],
)
