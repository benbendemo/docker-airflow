#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Provide 2 ways to create airflow user.

After enter into docker-airflow postgres container, you can easily
use below to connect to db

psql -U airflow -h 127.0.0.1 -p 5432 -d airflow
psql -U docker -h 127.0.0.1 -p 5432 -d docker
psql -U postgres -h 127.0.0.1 -p 5432 -d postgres
"""

# Method 1(not sccuess):
from airflow import models, settings
from airflow.contrib.auth.backends.password_auth import PasswordUser

user = PasswordUser(models.User())
user.username = 'admin'
user.email = 'admin@test.com'
user.password = 'test'
user.firstname = 'admin'
user.lastname = 'user'

session = settings.Session()
session.add(user)
session.commit()
session.close()


# Method 2:
# airflow create_user -r Admin -u admin -e admin@example.com -f admin -l user -p test

