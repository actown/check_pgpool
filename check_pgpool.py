import pynagios
from pynagios import Plugin, Response, make_option
import subprocess


class CheckPgpool(Plugin):

    timeout = make_option('--timeout', type='string')
    hostname = make_option('--host', type='string')
    port = make_option('-p', '--port', type='string')
    username = make_option('-u', '--username', type='string')
    password = make_option('-P', '--password', type='string')

    def check(self):
        try:
            nodes = subprocess.check_output(['/usr/sbin/pcp_node_count',
                                            self.options.timeout,
                                            self.options.hostname,
                                            self.options.port,
                                            self.options.username,
                                            self.options.password]).rstrip()
        except:
            return Response(pynagios.UNKNOWN,
                            "Unable to get the node count from pcp.")

        for i in xrange(0, int(nodes)):
            try:
                node_info = subprocess.check_output(['/usr/sbin/pcp_node_info',
                                                    self.options.timeout,
                                                    self.options.hostname,
                                                    self.options.port,
                                                    self.options.username,
                                                    self.options.password,
                                                    '%s' % i])
            except:
                return Response(pynagios.UNKNOWN,
                                "Unable to get the node info from pcp.")

            node_status = node_info.split(" ")

            if node_status[2] == "3":
                try:
                    subprocess.check_output(['/usr/sbin/pcp_attach_node',
                                            self.options.timeout,
                                            self.options.hostname,
                                            self.options.port,
                                            self.options.username,
                                            self.options.password,
                                            '%s' % i])
                except:
                    return Response(pynagios.CRITICAL,
                                    "Tried to reattach but failed!")

                return Response(pynagios.CRITICAL,
                                "Found a downed node and tried to reattach!")
        return Response(pynagios.OK, "All nodes attached.")


if __name__ == "__main__":
    CheckPgpool().check().exit()
