from setuptools import setup


setup(
    name='command_lifecycle',
    packages=['command_lifecycle'],
    version='2.0.0',
    url='https://github.com/richtier/voice-command-lifecycle',
    license='MIT',
    author='Richard Tier',
    author_email='rikatee@gmail.com',
    description='Python library to manage the life-cycle of voice commands.',
    long_description=open('docs/README.rst').read(),
    include_package_data=True,
    install_requires=[],
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
