import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'semantic_nav'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        (os.path.join('share', package_name), ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='owl',
    maintainer_email='zesmaeili85@gmail.com',
    description='YOLO + SMC semantic navigation',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'yolo_detector = semantic_nav.yolo_detector_node:main',
            'obstacle_aware_controller = semantic_nav.obstacle_aware_controller:main',
        ],
    },
)
