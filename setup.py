import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="simpy_helpers",
    version="1.0.0",
    author="Brian Ambielli",
    author_email="brian.ambielli@gmail.com",
    description="A package to help simplify simpy simulation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bambielli/simpy_helpers",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
