def get_email_from_netid(netid):
    import subprocess
    import shlex
    result = subprocess.run(shlex.split("sudo /hpc/pipspace/bin/getemailbynetid {0}".format(netid)), stdout=subprocess.PIPE)
    return result.stdout.decode("utf-8").split("\n")[0]
