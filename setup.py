import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


with open('requirements.txt', 'r') as f:
    dependencies = [line.strip() for line in f.readlines()]

setuptools.setup(
    name="pringles-devs",
    version="0.0.2",
    author="Colonel Pringles",
    # author_email="example@email.com",
    description="A DEVS model composition library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/colonelpringles/pringles",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    install_requires=dependencies
)
