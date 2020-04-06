import os

LOCAL_BASEDIR = os.getenv("LOCAL_BASEDIR", "/tmp/dump")  
REMOTE_BASEDIR = os.getenv("REMOTE_BASEDIR", "/tmp/dump")
GCS_BASEDIR = os.getenv("GCS_BASEDIR", "dump") 
GCS_BUCKETNAME = os.getenv("GCS_BUCKETNAME", "gs://my-database-migration-bucket") 
CLOUDSQL_SERVER = os.getenv("CLOUDSQL_SERVER", "1.2.3.4") 
CLOUDSQL_PASSWORD = os.getenv("PGPASSWORD", "password")
CLOUDSQL_SUPERUSER= os.getenv('PGUSER', "postgres")

# mysql section
MYSQLDUMP_USER = os.getenv("MYSQLDUMP_USER", "myusername")
MYSQLDUMP_PASSWORD= os.getenv('MYSQLDUMP_PASSWORD', "mypassword")
MYSQLDUMP_EXTRA_ARGS = " -u {MYSQLDUMP_USER} --password={MYSQLDUMP_PASSWORD} ".format(
  MYSQLDUMP_USER=MYSQLDUMP_USER,
  MYSQLDUMP_PASSWORD=MYSQLDUMP_PASSWORD
)

DATABASES = {
  "prd-psql-server-db-01": [
    "psql-db-01",
  ],
  "prd-psql-server-db-02": [
    "psql-db-02",
  ]
}

MYSQL_DATABASES = {
  "prd-mysql-server-db-01": [
    "mysql-db-01"
  ],
  "prd-mysql-server-db-02": [
    "mysql-db-02"
  ],
}

