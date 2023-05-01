from setuptools import find_packages, setup

setup(
    name='src',
    packages=find_packages(),
    version='1.0.0',
    description='ICU Prediction API',
    author='Bas Vonk',
    license='',
    install_requires=[
        'mysqlclient==1.4.2',
        'flask==2.3.2',
        'faker==1.0.4',
        'numpy==1.16.2',
        'pandas==0.24.2',
        'coloredlogs==10.0'
    ]
)
