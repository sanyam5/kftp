import http.server as SimpleHTTPServer
import socketserver
import constants
import os
import daemon

# A derived handler to obscure the contents of the transfers directory.
# It helps us block unauthorised clients from sending download requests and overloading the server unnecessarily.
class ObscuredHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def list_directory(self, path):
       self.send_error(404, "The directory listing has been disabled to prevent overloading of this server by unauthorised clients.")
       return None

def start_if_not_started():
    with daemon.DaemonContext():
        cwd = os.getcwd()
        os.chdir(constants.TMPDIR)
        try:
            PORT = constants.OUTPORT
            Handler = ObscuredHandler 
            httpd = socketserver.TCPServer(("", PORT), Handler)

            print ("serving at port " + str(PORT))
            httpd.serve_forever()
        except Exception as e:
            print("Failed to start server. Error: %s. Is the server already running " %str(e))
        os.chdir(cwd)

if __name__ == "__main__":
    start_if_not_started()
