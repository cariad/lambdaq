from pathlib import Path

from setuptools import setup

from lambdaq import __version__

readme_path = Path(__file__).parent / "README.md"

with open(readme_path, encoding="utf-8") as f:
    long_description = f.read()

classifiers = [
    "License :: OSI Approved :: MIT License",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Typing :: Typed",
]

if "a" in __version__:
    classifiers.append("Development Status :: 3 - Alpha")
elif "b" in __version__:
    classifiers.append("Development Status :: 4 - Beta")
else:
    classifiers.append("Development Status :: 5 - Production/Stable")

classifiers.sort()

setup(
    author="Cariad Eccleston",
    author_email="cariad@cariad.earth",
    classifiers=classifiers,
    description=(
        "Helps you write Amazon Web Services Lambda functions called by Step "
        "Functions via SQS"
    ),
    include_package_data=True,
    install_requires=[
        "boto3~=1.0",
    ],
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    name="lambdaq",
    packages=[
        "lambdaq",
        "lambdaq.types",
    ],
    package_data={
        "lambdaq": ["py.typed"],
        "lambdaq.types": ["py.typed"],
    },
    project_urls={
        "Project": "https://github.com/cariad/lambdaq",
    },
    python_requires=">=3.10",
    version=__version__,
)
