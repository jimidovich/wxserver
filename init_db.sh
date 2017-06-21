#!/bin/bash

mysql -u root -p -e "create database $1 CHARACTER SET utf8 COLLATE utf8_general_ci"
mysql -u root -p -D$1<db_bare_init.sql
