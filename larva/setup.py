from setuptools import setup

setup(
    name = "larva count",
    version = "0.0.1",
    author = "Polawat Phetra",
    author_email = "pphetra@gmail.com",
    description = ("create spreadsheet that contain larva survey results with CI, HI index"),
    license = "MIT",
    keywords = "larva,podd",
    url = "https://github.com/openpodd/larva-report",
    packages=['larva'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
    install_requires=[
        'psycopg2',
        'pandas'
    ]
)