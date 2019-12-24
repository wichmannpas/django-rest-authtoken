import setuptools

with open('README.md') as fh:
    long_description = fh.read()

setuptools.setup(
    name='django-rest-authtoken',
    version='1.2.4',
    author='Pascal Wichmann',
    author_email='wichmannpas@gmail.com',
    description='A simple auth token auth backend for Django Rest Framework storing cryptographically hashed tokens on server-side.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/wichmannpas/django-rest-authtoken',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
)
