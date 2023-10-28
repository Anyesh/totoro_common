from setuptools import setup

setup(
    name="totoro",
    version="0.0.1",
    author="Anish Shrestha",
    requires=[
        "Flask==2.2.2",
        "PyJWT==2.8.0",
    ],
    package_dir={
        "totoro.helpers": "helpers",
    },
    include_package_data=True,
)
