Building
=========

Install Visual Studio code and load this project.

On VSCode command prompt run following:

* Run Task > Build Project


Initializing Database
======================

You will need following databases created on your local PostgreSQL:

* contrace
* contrace_warehouse
* contrace_cache

On VSCode command prompt run following sequence:

* Run Task > Generate Migrations
* Run Task > Update Database
* Run Task > MorpCC: Create Default Admin User (admin:admin)

Starting Up
===========

* Run Task > Start Application

Login as ``admin``, with password ``admin``
