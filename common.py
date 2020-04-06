import os
import subprocess
from conf import *
from loggers import logger

DUMP_DONE_FLAG="DUMP_DONE_FLAG"
RESTORE_DONE_FLAG="RESTORE_DONE_FLAG"
LOCKDB_FLAG="LOCKDB_FLAG"

def run_cmd(bashCommand, print_output=False, env={}):
  # keep system vars
  sysenv = os.environ.copy()
  envs = env.update(sysenv)
  
  logger.debug("cmd: %s" % bashCommand)
  process = subprocess.Popen(bashCommand, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=envs)
  output, error = process.communicate()
  if print_output:
    logger.debug("stdout %s" % output)
  return (output, error, process.returncode)


def databases_to_process(hostname, db_kind="POSTGRES"):
  DBS = DATABASES if (db_kind=="POSTGRES") else MYSQL_DATABASES
  databases_context = []
  for db in DBS.get(hostname, []):
    databases_context.append({
      "database" : db, 
      "local_dir": "%s/%s/%s" % (LOCAL_BASEDIR, hostname, db),
      "remote_dir" : "%s/%s/%s" % (REMOTE_BASEDIR, hostname, db),
      "gcs_dir" : "%s/%s/%s" % (GCS_BASEDIR, hostname, db)
    })
  return databases_context


def run_mkdirs(db, mode="local"):
  dumpdir = db.get("local_dir")
  if mode == "remote":
    dumpdir = db.get("remote_dir")

  mkdir = "mkdir -p {LOCALDUMPDIR}".format(LOCALDUMPDIR=dumpdir)
  return run_cmd(mkdir)


def check_flag(db, flag="DUMP-FINISHED"):
  cmd = "gsutil stat {GCS_BUCKETNAME}/{GCSDIR}/{FLAG}".format(
    GCSDIR=db.get("gcs_dir"),
    GCS_BUCKETNAME=GCS_BUCKETNAME,
    FLAG=flag
  )
  stdout , _ , _ = run_cmd(cmd)
  present = not ("No URLs matched" in stdout)
  logger.debug("Is Flag {flag} present ? : {present}".format(flag=flag, present=present))
  return present


def run_make_gcs_flag(db, flag):
  touch = "touch /tmp/{FLAG}".format(
    LOCALDUMPDIR=db.get("local_dir"),
    FLAG=flag
  )
  cmd = "gsutil -m cp /tmp/{FLAG} {GCS_BUCKETNAME}/{GCSDIR}".format(
    GCSDIR=db.get("gcs_dir"),
    LOCALDUMPDIR=db.get("local_dir"),
    GCS_BUCKETNAME=GCS_BUCKETNAME,
    FLAG=flag
  )
  run_cmd(touch)
  return run_cmd(cmd)


def run_rm_gcs_flag(db, flag):
  cmd = "gsutil rm {GCS_BUCKETNAME}/{GCSDIR}/{FLAG}".format(
    GCSDIR=db.get("gcs_dir"),
    GCS_BUCKETNAME=GCS_BUCKETNAME,
    FLAG=flag
  )
  return run_cmd(cmd)