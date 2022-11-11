# antavia_db_v2
Python tools to migrate the Antavia database to v2.0
---
**Usage**: the script will create and populate a new database on the same server where version 1 is hosted. Migration between servers is not supported. You need to edit the migrate_db.py header section. Then simply run:

> python3 migrate_db.py

If the database needs to be hosted on a different server, it can then be dumped and moved.
