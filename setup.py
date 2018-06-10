import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='MrDatabase',
    version='0.9.6',
    author='Seeberg',
    author_email='soren.seeberg@gmail.com',
    description='Databasing as easy as it gets!',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/SorenSeeberg/MrDatabase',
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    )
)



