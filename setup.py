from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt") as f:
    install_requires = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="thinktwice",
    version="0.1.0",
    description="Self-Reflecting LLM Agent (Reflexion-Style) — Attempt → Evaluate → Reflect → Retry",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="ThinkTwice Contributors",
    python_requires=">=3.10",
    packages=find_packages(),
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
