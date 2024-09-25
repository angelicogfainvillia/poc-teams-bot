import setuptools
import os


def read_requirements():
    """Read the requirements.txt file and return a list of dependencies."""
    with open("./requirements.txt") as f:
        return f.read().splitlines()


setuptools.setup(
    name="inviscopilot",
    version="0.8.2",
    author="Your Name or Organization",
    author_email="your.email@example.com",
    description="InviscoPilot is a comprehensive library designed to enhance the capabilities of AI-driven applications, focusing on efficient data management, seamless Azure integrations, and robust information retrieval systems. It provides specialized tools for embedding management, vector storage handling, and interaction with Azure services, facilitating advanced data processing and retrieval tasks within enterprise environments.",
    long_description_content_type="text/markdown",
    url="https://gitlab.invillia.com/inaction/invillia-aimanagment-botintelligence-bot",
    package_dir={"": "."},  # Specify the root package directory as current
    packages=setuptools.find_packages(
        where="."
    ),  # Automatically find all packages in the current directory
    install_requires=read_requirements(),
    python_requires=">=3.10",
    include_package_data=True,
    zip_safe=False,
)
