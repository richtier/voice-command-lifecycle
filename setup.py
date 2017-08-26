from setuptools import setup

import pip.download
from pip.req import parse_requirements
import pypandoc


def get_requirements():
    requirements = parse_requirements(
        'requirements.txt',
        session=pip.download.PipSession()
    )
    return [str(r.req) for r in list(requirements)]


setup(
    name='command_lifecycle',
    packages=['command_lifecycle'],
    version='0.4.0',
    url='https://github.com/richtier/voice-command-lifecycle',
    license='MIT',
    author='Richard Tier',
    author_email='rikatee@gmail.com',
    description='Python library to manage the life-cycle of voice commands.',
    long_description=pypandoc.convert('README.md', 'rst'),
    include_package_data=True,
    install_requires=get_requirements(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
