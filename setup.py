from setuptools import setup, find_packages

setup(
    name="flexiflow",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
        "networkx>=3.0",
        "requests>=2.28.0",
    ],
    author="Lokesh",
    author_email="meta2web3@gmail.com",
    description="A hybrid agentic framework for scalable, multimodal AI systems.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/LogeswaranA/flexiflow",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)