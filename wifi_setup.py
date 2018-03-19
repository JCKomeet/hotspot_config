#!/usr/bin/python3
import http.server
import socketserver
from pathlib import Path
import sys
from urllib.parse import urlparse , parse_qs
import subprocess


index = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <title>Komeet Setup</title>
  </head>
  <body>
    <h1> Hosting access point </h1>
    Setup
    <form>
    <div>
     SSID <input list="SSID" name="SSID">
        <datalist id="SSID">
        ###SSID###
        </datalist>
    </input>
    <div>
    <div>
        Password <input id="pass" name="PASS">
    </div>

    <div>
        <button id="setbtn" name='restart' disabled=true> Set and Restart </button>
    </div>

     </form>

    </body>
    <script> 
        var pass = document.getElementById("pass");
        var setbtn = document.getElementById("setbtn");
        pass.oninput = () => {
            setbtn.disabled = pass.value.length < 8
        }
    </script>
</html>
"""

ssids_out = subprocess.getoutput("iw wlan0 scan | grep SSID | cut -d' ' -f2-")
print(ssids_out)

ssids = map(lambda st: "<option value='" + st +"'>" ,  ssids_out.splitlines() )


index = bytes( index.replace("###SSID###"," ".join(ssids) ) ,"utf8")


class Handler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        query = urlparse(self.path).query
        query_components = parse_qs(query)
        if 'SSID' in query_components and 'PASS' in query_components :
            result = subprocess.getoutput( 'wpa_passphrase ' 
                        + query_components['SSID'][0] 
                        + " " +  query_components['PASS'][0])
            with open("/etc/wpa_supplicant/wpa_supplicant.conf", "a") as wpaconf:
                wpaconf.write(result)
                wpaconf.write('\n')
                print("rebooting")
                subprocess.getoutput("sleep 1 ; sudo reboot")


        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(index)
        return


if __name__ == "__main__":
    httpd = socketserver.TCPServer(('', 81), Handler)
    # terminate with Ctrl-C
    try:
        print('Server listening on port 81...')
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Shutdown")
        httpd.shutdown()
        sys.exit(0)
