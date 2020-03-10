from setuptools import find_packages, setup

setup(name='airflow_common_lib',
        version='0.9.11',
        description='Library for common airflow task',
        packages=find_packages(where='./src'),
        package_dir={
            '': 'src'
        },
        install_requires=(
            'hvac'
        ),
        setup_requires=(
            'pytest-runner',
        ),
        tests_require=(
            'pytest-cov',
        ),
        zip_safe=False)
