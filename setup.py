from setuptools import setup

setup(
    name="totoro",
    version="0.0.1",
    author="Anish Shrestha",
    python_requires=">=3.11.5",
    install_requires=[
        "Flask==2.2.2",
        "werkzeug==2.2.2",
        "PyJWT==2.8.0",
        "requests==2.31.0",
    ],
    package_dir={
        "totoro.helpers": "helpers",
    },
    include_package_data=True,
)
