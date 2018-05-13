#!/usr/bin/python
import os
import os.path
import re
import time
import json
import subprocess

# script to create an ssh tunnel from a public server back to a private (firewalled/NATted) machine; a poor man's VPN, basically

# how it works:
# private machine run this script at regular intervals, which attempts to ssh into public server; if successful, it
# sets up a number of port forwards back to private machine so you can access it from public server

# to use:
# 1) configure the settings below
# 2) set up key-based auth for private machine to log into public server
# 3) set up cron on private machine to run the script at frequent intervals (<= 5 minutes)
# 4) when the tunnel is up, access private machine via:
#      ssh -l PORT youracct@localhost     (from public server)
#      ssh -l PORT youracct@publicserver  (from internet at large, if you made the ssh-forward publicly hittable)

def mk_port_forward(listen_at, local_port, remote_port, public=False):
    pattern = {
        'forward': '-L %(public)s%(local)d:localhost:%(remote)d',
        'reverse': '-R %(public)s%(remote)d:localhost:%(local)d',
    }[listen_at]

    return pattern % {
        'public': '*:' if public else '',
        'local': local_port,
        'remote': remote_port,
    }

def mk_port_forwards(port_forwards):
    return ' '.join(mk_port_forward(*f) for f in port_forwards)

def mk_tunnel_cmd(user, server, remote_ssh_port, forwards, compression=True, keyfile=None):
    options = [
        'BatchMode yes',             # abort if any interactive prompt (e.g., password) shown
        'ExitOnForwardFailure yes',  # abort if port forwards unavailable (usually means tunnel is already up)
        'ServerAliveInterval 60',    # use keep-alive pings to prevent stale sessions
    ]

    return 'ssh %s@%s -p %d -N %s %s %s %s' % (user, server, remote_ssh_port, '-C' if compression else '', '-i %s' % keyfile if keyfile else '',
                                      mk_port_forwards(forwards), ' '.join('-o "%s"' % opt for opt in options))


if __name__ == "__main__":
    # public server as resolvable from private machine
    SERVER = '<ip address/domain name of remote host>'

    # user that private machine will log into public server as
    USER = '<user of remote host>'

    REMOTE_SSH_PORT = <ssh port of remote host>

    # port of the reverse-ssh endpoint
    REMOTE_PORT = <remote host port to port forward to>
    LOCAL_PORT = <local host port to port forward>

    # private keyfile used to log into USER@SERVER. if None, ssh will search in the default places.
    # note that key-based auth is required! password-based auth will not work, as there is no one
    # to type in the password
    KEYFILE = None

    PORT_FORWARDS = [
        ('reverse', LOCAL_PORT, REMOTE_PORT, True), #reverse ssh
        # add additional port forwards here
    ]

    # probably enable for mobile-tethered connections
    USE_COMPRESSION = False

    print("Server: {}\nUser: {}\nRemote SSH port: {}\nRemote port: {}\nLocal port forward: {}\nKeyfile specified: {}".format(SERVER, USER, REMOTE_SSH_PORT,  REMOTE_PORT, LOCAL_PORT, KEYFILE))
    print("\n\nEstablishing port forward...")

    try:
        #os.popen(mk_tunnel_cmd(USER, SERVER, REMOTE_SSH_PORT, PORT_FORWARDS, USE_COMPRESSION, KEYFILE))
        process = subprocess.Popen(mk_tunnel_cmd(USER, SERVER, REMOTE_SSH_PORT, PORT_FORWARDS, USE_COMPRESSION, KEYFILE), shell=True)

        process.wait()
    except KeyboardInterrupt:
        print("Terminating {}".format(__file__))
        os._exit(0)

