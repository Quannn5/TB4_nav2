import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'tb4_navigation_practice'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'maps'), glob('maps/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='engquan5',
    maintainer_email='engquan5@todo.todo',
    description='TurtleBot 4 SLAM and navigation practice package.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [],
    },
)
