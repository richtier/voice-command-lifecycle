from setuptools import setup


setup(
    name='command_lifecycle',
    packages=['command_lifecycle'],
    version='4.1.0',
    url='https://github.com/richtier/voice-command-lifecycle',
    license='MIT',
    author='Richard Tier',
    author_email='rikatee@gmail.com',
    description='Python library to manage the life-cycle of voice commands.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    include_package_data=True,
    install_requires=[
        'resettabletimer>=0.6.3,<1.0.0',
    ],
    extras_require={
        'test': [
            'pytest==3.2.3',
            'pytest-cov==2.5.1',
            'pytest-sugar==0.9.0',
            'flake8==3.4.0',
            'codecov==2.0.9',
            'twine>=1.11.0,<2.0.0',
            'wheel>=0.31.0,<1.0.0',
            'setuptools>=38.6.0,<39.0.0',
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
