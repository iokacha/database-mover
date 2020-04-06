# dependencies :
  - gcloud 
  - gsutil
  - postgresql
    - pg_dump
    - pg_restore
    - psql
  - mysql
    - mysqldump
    - mysql-client

# install dependencies 
  * In the source database VM, As postgres user, install gcloud & gsutil: 
    - install gcloud            : curl https://sdk.cloud.google.com | bash
    - login to gcloud           : gcloud auth login
    - setup default project     : gcloud config set core/project my-hosting-project
    - To check everything is ok : gsutil ls 


# On the source database machines
  - sudo su - postgres
  - cd /tmp && rm -rf /tmp/dump && python mover/dump.py


# Restore procedure : On GCP edge machine : 
  - 
    * For Postgresql :
      Install psql client : https://www.postgresql.org/download/linux/debian/
      ```
        echo 'deb http://apt.postgresql.org/pub/repos/apt/ stretch-pgdg main' > /etc/apt/sources.list.d/pgdg.list
        wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
        sudo apt-get update
        apt-get install postgresql-11 -y
      ```
    * For MySQL : 
      Install mysql utilities.
      ```
        apt-get install -y mysql-server
      ```



  - Scp restore script: 
      * gcloud compute scp --recurse mover  my-gcp-edge-machine:~
  - Patch the database : [//]: # temporary file size exceeds temp_file_limit
      * gcloud sql instances patch data-replication-poc  --database-flags temp_file_limit=2147483647,work_mem=32768, maintenance_work_mem=2097152,autovacuum=off
                  
  - Run the restore VM ( n1-standard-2 (2 vCPUs, 7.5 GB memory)): 
    * For Postgres Run the restore VM :
        
        export DATABASE_SERVER_TO_PROCESS=prd-psql-server-db-01
        export PGPASSWORD=MY-SECURE-PASS
        export CLOUDSQL_SERVER=1.2.3.4 # or your db fqdb
        python mover/restore.py --hostname $DATABASE_SERVER_TO_PROCESS
        
    * For MySQL Run the restore VM :
        
        export DATABASE_SERVER_TO_PROCESS=prd-mysql-server-db-01
        export MYSQLDUMP_USER=root
        export MYSQLDUMP_PASSWORD=MY-SECURE-PASS
        export CLOUDSQL_SERVER=1.2.3.4 # or your db fqdb
        python mover/restore_mysql.py --hostname $DATABASE_SERVER_TO_PROCESS



# Restore Users and Grants 
  - pg_dumpall -g  > globals.sql

# Analytics
  * Dump
  * Restore