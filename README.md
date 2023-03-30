# py_socket_forward_rec

This script forwards a number of configured local ports
to local or remote socket servers.

Configuration:
Add to the config file pyrec.config lines with
contents as follows:
  "local incoming port" "dest hostname" "dest port"

Start the application at command line with 'python pyrec.py'
and stop the application by keying in <ctrl-c>.

Example: python pyrec.py 8080:127.0.0.1:5555
