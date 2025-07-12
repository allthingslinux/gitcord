"""
Setup script for GitCord bot.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="gitcord",
    version="1.0.0",
    author="GitCord Team",
    author_email="team@gitcord.com",
    description="A Discord bot for Git integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gitcord/gitcord",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "gitcord=gitcord.bot:run_bot",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
