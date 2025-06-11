from setuptools import setup, find_packages

setup(
    name="rhamaa",
    version="0.1.0",
    description="CLI tools to accelerate Wagtail web development.",
    author="Your Name",
    author_email="your@email.com",
    packages=find_packages(),
    install_requires=[
        "click",
        "wagtail"
    ],
    entry_points={
        "console_scripts": [
            "rhamaa=rhamaa.cli:main"
        ]
    },
    python_requires=">=3.7",
)
