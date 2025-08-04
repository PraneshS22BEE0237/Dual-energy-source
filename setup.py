from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="dual-energy-source",
    version="1.0.0",
    author="AI Assistant",
    author_email="ai.assistant@example.com",
    description="AI-Powered Dual Energy Source Management System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/dual-energy-source",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/dual-energy-source/issues",
        "Documentation": "https://github.com/yourusername/dual-energy-source/wiki",
        "Source Code": "https://github.com/yourusername/dual-energy-source",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering",
        "Topic :: Home Automation",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "hardware": [
            "RPi.GPIO>=0.7.0",
            "adafruit-circuitpython-ads1x15>=2.2.0",
            "w1thermsensor>=2.0.0",
        ],
        "dev": [
            "pytest>=6.0.0",
            "black>=22.0.0",
            "pylint>=2.12.0",
        ],
        "visualization": [
            "matplotlib>=3.5.0",
            "plotly>=5.0.0",
            "dash>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "dual-energy=src.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.json", "*.html", "*.css", "*.js"],
    },
    keywords="energy management, AI, machine learning, renewable energy, solar, thermal, battery, IoT, raspberry pi",
)
