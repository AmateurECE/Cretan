import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cretan",
    version="0.0.1",
    author="Ethan Twardy",
    author_email="ethan.twardy@gmail.com",
    description="Transport generic message broker",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AmateurECE/Cretan",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5.3',
    install_requires=[
        'discord.py',
        'psutil',
        'discord',
        'appdirs',
    ],
    provides=['cretan'],
    scripts=['scripts/cretan-daemon', 'scripts/cretan-send'],
)
