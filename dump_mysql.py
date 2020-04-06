#!/usr/bin/env python2
import os
import subprocess
from conf import *
from common import *
from loggers import logger


def run_dump_schema(db):
  cmd = """
    mysqldump \
    --verbose \
    {MYSQLDUMP_EXTRA_ARGS} \
    {DATABASENAME} > {LOCALDUMPDIR}/{DATABASENAME}.schema.sql
  """.format(
    DATABASENAME=db.get("database"),
    LOCALDUMPDIR=db.get("local_dir"),
    MYSQLDUMP_EXTRA_ARGS=MYSQLDUMP_EXTRA_ARGS
  )
  return run_cmd(cmd)


def run_dump_database(db,  print_output=True):
  cmd = """
    mysqldump \
    --verbose \
    {MYSQLDUMP_EXTRA_ARGS} \
    {DATABASENAME} > {LOCALDUMPDIR}/{DATABASENAME}.sql
  """.format(
    DATABASENAME=db.get("database"),
    LOCALDUMPDIR=db.get("local_dir"),
    MYSQLDUMP_EXTRA_ARGS=MYSQLDUMP_EXTRA_ARGS
  )
  return run_cmd(cmd, print_output=True)


def run_upload_gcs(db, print_output=True):
  cmd = """
    gsutil -m \
    cp -r {LOCALDUMPDIR}/* \
    {GCS_BUCKETNAME}/{GCSDIR}/data
  """.format(
      GCSDIR=db.get("gcs_dir"),
      LOCALDUMPDIR=db.get("local_dir"),
      GCS_BUCKETNAME=GCS_BUCKETNAME
  )
  return run_cmd(cmd, print_output=True)


def run():
  hostname = run_cmd("hostname")[0].strip("\n")
  dbs = databases_to_process(hostname, db_kind="MYSQL")

  for db in dbs:
    dbname = db.get("database")
    logger.info("==> Processing %s" % dbname)
    run_mkdirs(db)
    run_dump_schema(db)
    run_dump_database(db, print_output=True)
    run_upload_gcs(db, print_output=True)
    run_make_gcs_flag(db, DUMP_DONE_FLAG)
    logger.info("<== Finished Processing %s" % dbname)


if __name__ == "__main__":
    run()
