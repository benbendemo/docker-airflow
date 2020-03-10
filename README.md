# docker-airflow

[![Docker Build status](https://img.shields.io/docker/build/puckel/docker-airflow?style=plastic)](https://hub.docker.com/r/puckel/docker-airflow/tags?ordering=last_updated)

This repository forked from [puckel/docker-airflow](https://github.com/puckel/docker-airflow).

 You need to visit the above link to see the original content of his docker-airflow image.

Based on his version, I have adjust some parameters and add some little utilities and make some changes.

## Changes

* Add `airflow-common-library-master` utility
* Update the default settings in `airflow.cfg`
* Use Tsinghua Debian mirror to replace default Debian apt-get source, see `apt-source.list`
* Add an `email-templates` for airflow to automatically send alert email and success email
* Use Douban PIP mirror to replace default PIP source, see `pip.conf`
* As for `Dockerfile`, i have added some more Debian apt packages and Python pip packages
* In `script/airflow_create_user.py`, there are two ways to create airflow login user when RBAC enabled.Oh forget to inform that it's defaulted to enable RBAC in `airflow.cfg`

## Details change in airflow.cfg

1. sql_alchemy_conn` was initialize to postgresql connection per the usename and password created during docker-compose command execute.

   `sql_alchemy_conn = postgresql://airflow:airflow@postgres:5432/airflow`

2. Update webserver `web_server_master_timeout` to 600 seconds

3. Update webserver `web_server_worker_timeout` to 600 seconds

4. Update webserver `worker_refresh_interval` to 300 seconds

5. Update webserver gunicorn `workers` to 2 instead of 4

6. Update webserver `authenticate` to True and update `auth_backend` to "airflow.contrib.auth.backends.password_auth" in order to enable airflow RBAC login

7.  Update email `subject_template` to "/usr/local/airflow/email-templates/subject_template.txt" and update `html_content_template` to "/usr/local/airflow/email-templates/content_template.html"

8. Update smtp sections to enable sending emails

## Installation

Pull the image from the Docker repository.

    docker pull benbendemo/docker-airflow

## Build

Same as  [puckel/docker-airflow](https://github.com/puckel/docker-airflow) told.

# Wanna help?

Talk with me to communicate.
