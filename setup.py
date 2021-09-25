#!/usr/bin/env python
"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'face_recognition_models==0.3.0',
    'dlib==19.22.0',
    'numpy==1.21.0',
    'opencv-python-headless==4.5.3.56',
    'scipy==1.7.0',
    'sharedmem==0.3.8',
    'Click>=7.0',
]

test_requirements = []

setup(
    author="Naresh R",
    author_email='ghostwriternr@gmail.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Create low-poly art from any image",
    entry_points={
        'console_scripts': [
            'lowpolify=lowpolify.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='lowpolify',
    name='lowpolify',
    packages=find_packages(include=['lowpolify', 'lowpolify.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/ghostwriternr/lowpolify',
    version='0.1.0',
    zip_safe=False,
)
