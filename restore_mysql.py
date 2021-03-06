#!/usr/bin/env python2
from loggers import logger
from common import * 
import argparse


def run_copy_data_to_local(db):
  cmd = """
    gsutil -m \
    cp -r {GCS_BUCKETNAME}/{GCSDIR}/data \
    {REMOTEDUMPDIR}
  """.format(
    GCSDIR=db.get("gcs_dir"),
    REMOTEDUMPDIR=db.get("remote_dir"),
    GCS_BUCKETNAME=GCS_BUCKETNAME
  )
  return run_cmd(cmd)

def run_create_database(db, print_output=False):
  create_cmd = """
    mysql \
    --verbose \
    -h {TARGET_SERVER} \
    {MYSQLDUMP_EXTRA_ARGS} \
    -e 'create database {DATABASENAME};'
  """.format(
    DATABASENAME=db.get("database"),
    TARGET_SERVER=CLOUDSQL_SERVER,
    MYSQLDUMP_EXTRA_ARGS=MYSQLDUMP_EXTRA_ARGS
  )
  return run_cmd(create_cmd, print_output)


def run_restore_to_cloudsql(db, print_output=True):  
  restore = """
    mysql \
    -h {TARGET_SERVER} \
    {MYSQLDUMP_EXTRA_ARGS} \
    {DATABASENAME} < {REMOTEDUMPDIR}/data/data.sql
  """.format(
    DATABASENAME=db.get("database"),
    REMOTEDUMPDIR=db.get("remote_dir"),
    TARGET_SERVER=CLOUDSQL_SERVER,
    MYSQLDUMP_EXTRA_ARGS=MYSQLDUMP_EXTRA_ARGS
  )
  return run_cmd(restore, print_output=True)



def __run(hostname):
  dbs = databases_to_process(hostname, db_kind="MYSQL")

  for db in dbs:
    dbname = db.get("database")
    logger.info("==> Processing %s" % dbname)
    is_restorable = (
      check_flag(db, DUMP_DONE_FLAG) and 
      (not check_flag(db, RESTORE_DONE_FLAG)) and 
      (not check_flag(db, LOCKDB_FLAG))
    )
    if is_restorable:
      logger.info("== ==> Working on : %s" % dbname )
      run_mkdirs(db, mode="remote")
      run_copy_data_to_local(db)
      # lock the processed db 
      run_make_gcs_flag(db, LOCKDB_FLAG)
      run_create_database(db, print_output=True)
      run_restore_to_cloudsql(db, print_output=True)

      run_make_gcs_flag(db, RESTORE_DONE_FLAG)
      # Unlock the processed db 
      run_rm_gcs_flag(db, LOCKDB_FLAG)
      logger.info("<== Finished Processing %s \n" % dbname)
    else:
      logger.info("<== Skipping %s \n" % dbname)



def run():
  parser = argparse.ArgumentParser()
  parser.add_argument("--hostname", help="hostname to restore")
  parser.add_argument("--dbkind", help="hostname to restore")
  args = parser.parse_args()
  
  hostname = args.hostname
  if hostname and (hostname in DATABASES.keys() or hostname in MYSQL_DATABASES.keys()):
    __run(hostname)
  else : 
    logger.error("Please specify a valide database hostname")

if __name__ == "__main__":
    run()
