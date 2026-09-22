from setuptools import find_packages, setup

package_name = 'turtlebot_controller'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='mostafa',
    maintainer_email='mostikhaled@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'cmd_vel_Pub_Handler = turtlebot_controller.turtlebot_controller:main',
            'cmd_vel_Sub_Handler = turtlebot_controller.turtlebot_monitor:main',
        ],
    },
)
