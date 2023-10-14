from setuptools import setup

setup(
    name="ml_collab",
    version="0.1.0",
    description="ML Lib for Collaborative-based RecSys",
    packages=["ml_collab"],
    install_requires=["numpy==1.25.1", "pandas==2.0.3", "pyspark==3.4.1"],
)
