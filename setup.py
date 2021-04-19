import setuptools

version = {}
with open("sim_racing_tools/version.py") as fp:
    exec(fp.read(), version)

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Sim-racing-tools",
    version=version['__version__'],
    author="zephyrj",
    author_email="zephyrj@protonmail.com",
    description="A collection of tools to make sim-racing more fun",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zephyrj/sim-racing-tools",
    packages=setuptools.find_packages('.'),
    package_dir={'': 'sim_racing_tools'},
    include_package_data=True,
    install_requires=['setuptools~=54.2.0',
                      'toml~=0.10.2',
                      'six~=1.15.0',
                      'configobj~=5.0.6',
                      'pandas~=1.2.3',
                      'plotly~=4.14.3'],
    scripts=[],
    entry_points={
        'console_scripts': [],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3.0",
        "Operating System :: OS Independent",
    ]
)