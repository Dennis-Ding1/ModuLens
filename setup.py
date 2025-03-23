from setuptools import setup, find_packages

setup(
    name="modulens",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "openai>=1.3.0",
        "python-dotenv>=1.0.0",
        "transformers>=4.36.0",
        "anthropic>=0.3.11",
        "colorama>=0.4.6",
        "prompt-toolkit>=3.0.38",
        "rich>=13.6.0",
        "pydantic>=2.4.2",
        "google-generativeai>=0.3.1",
        "cohere>=4.37"
    ],
    entry_points={
        "console_scripts": [
            "modulens=modulens.main:main",
        ],
    },
)
 