""" Setup file """
import os
import sys

from setuptools import setup, find_packages
from version_helper import git_version


HERE = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(HERE, 'README.rst')).read()
CHANGES = open(os.path.join(HERE, 'CHANGES.rst')).read()

REQUIREMENTS = [
    'boto>=2.20.1',
]

if sys.version_info[:2] < (2, 7):
    REQUIREMENTS.extend(['unittest2'])

if __name__ == "__main__":
    setup(
        name='flywheel',
        description="Object mapper for Amazon's DynamoDB",
        long_description=README + '\n\n' + CHANGES,
        classifiers=[
            'Programming Language :: Python',
        ],
        author='Steven Arcangeli',
        author_email='steven@highlig.ht',
        url='http://github.com/mathcamp/flywheel',
        zip_safe=False,
        include_package_data=True,
        packages=find_packages(),
        entry_points={
            'nose.plugins': [
                'dynamolocal=flywheel.tests:DynamoLocalPlugin',
            ],
        },
        install_requires=REQUIREMENTS,
        tests_require=REQUIREMENTS,
        **git_version()
    )