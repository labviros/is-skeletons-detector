from setuptools import setup, find_packages

setup(
    name='is_skeletons_detector',
    version='0.0.1',
    description='',
    url='http://github.com/labviros/is-skeletons-detector',
    author='labviros',
    license='MIT',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'is-skeletons-detector-stream=is_skeletons_detector.stream:main',
            'is-skeletons-detector-rpc=is_skeletons_detector.rpc:main',
        ],
    },
    zip_safe=False,
    install_requires=[
        'is-wire==1.1.2',
        'is-msgs==1.1.7',
        'opencv-python==3.3.1.*',
    ],
)