import setuptools

version = {}
with open("sim_racing_tools/version.py") as fp:
    exec(fp.read(), version)

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sim-racing-tools",
    keywords=["Assetto Corsa", "Automation", "Sim Racing"],
    version=version['__version__'],
    author="zephyrj",
    author_email="zephyrj@protonmail.com",
    description="A collection of tools to make sim-racing more fun",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zephyrj/sim-racing-tools",
    project_urls={
        "Bug Tracker": "https://github.com/zephyrj/sim-racing-tools/issues",
    },
    packages=setuptools.find_packages('.'),
    python_requires=">=3.6",
    include_package_data=True,
    install_requires=["setuptools~=65.3.0",
                      "wheel~=0.37.1",
                      "toml~=0.10.2",
                      "six~=1.16.0",
                      "configobj~=5.0.6",
                      "argcomplete~=2.0.0",
                      "pandas~=1.4.4",
                      "plotly~=5.10.0",
                      "pywin32"],
    scripts=[],
    entry_points={
        'console_scripts': ['ac-tools=sim_racing_tools.assetto_corsa.scripts.ac_tools:main',
                            'check-engine=sim_racing_tools.automation.scripts.check_engine:main'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ]
)
