def get_email_from_netid(netid):
    import subprocess
    import shlex
    bash_command = "curl -F \"netid={0}\" -F \"a=1\" -F \"form_type=advanced\" -k --url https://directory.northwestern.edu/?a=1".format(netid)
    args = shlex.split(bash_command)
    result = subprocess.run(args,stdout=subprocess.PIPE)
    return result.stdout.decode("utf-8").split('class=\"email\" href=\"mailto:')[-1].split('">')[0]
