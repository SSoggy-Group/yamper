import http.server
import json
import urllib.parse
from . import wifi

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Yamper WiFi Setup</title>
    <style>
        body { font-family: sans-serif; background: #f0f0f5; text-align: center; margin: 0; padding: 20px; }
        .container { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); max-width: 400px; margin: auto; }
        h1 { color: #333; }
        select, input, button { width: 100%; margin-top: 10px; padding: 12px; border-radius: 6px; border: 1px solid #ccc; font-size: 16px; box-sizing: border-box; }
        button { background: #007bff; color: white; border: none; font-weight: bold; cursor: pointer; margin-top: 20px; }
        button:active { background: #0056b3; }
        #status { margin-top: 20px; font-weight: bold; color: #d9534f; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Yamper Setup</h1>
        <p>Select your WiFi network to connect Yamper to the internet.</p>
        <form id="setupForm" method="POST" action="/connect">
            <select name="ssid" required>
                <option value="" disabled selected>Loading networks...</option>
                {options}
            </select>
            <input type="password" name="password" placeholder="WiFi Password (optional)" />
            <button type="submit">Connect</button>
        </form>
        <div id="status">{status_msg}</div>
    </div>
</body>
</html>
"""

# Global variable to signal completion
setup_success = False

class PortalHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress logging
        pass

    def do_GET(self):
        global setup_success
        if self.path == '/':
            networks = wifi.scan_networks()
            options = "".join([f'<option value="{n}">{n}</option>' for n in networks])
            if not networks:
                options = '<option value="" disabled>No networks found</option>'
                
            html = HTML_TEMPLATE.format(options=options, status_msg="")
            
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        elif self.path == '/status':
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": setup_success}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        global setup_success
        if self.path == '/connect':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            fields = urllib.parse.parse_qs(post_data)
            
            ssid = fields.get('ssid', [''])[0]
            password = fields.get('password', [''])[0]
            
            # Don't log password!
            print(f"Portal: attempting connection to SSID '{ssid}'")
            
            success = wifi.connect_to_wifi(ssid, password)
            
            if success:
                setup_success = True
                msg = "Connected successfully! Yamper is rebooting into normal mode."
            else:
                msg = "Failed to connect. Please check password and try again."
                
            networks = wifi.scan_networks()
            options = "".join([f'<option value="{n}">{n}</option>' for n in networks])
            html = HTML_TEMPLATE.format(options=options, status_msg=msg)
            
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def run_portal(port, server_class=http.server.HTTPServer, handler_class=PortalHandler):
    global setup_success
    setup_success = False
    server_address = ('', port)
    
    try:
        httpd = server_class(server_address, handler_class)
        print(f"Portal running on port {port}...")
    except OSError as e:
        print(f"Failed to start portal on port {port}: {e}")
        # Try fallback port if 80 is privileged and we are not root (e.g. on Mac mock)
        if port == 80:
            print("Trying fallback port 8080...")
            server_address = ('', 8080)
            httpd = server_class(server_address, handler_class)
            print("Portal running on port 8080...")
        else:
            raise

    httpd.timeout = 1
    while not setup_success:
        httpd.handle_request()
        
    print("Portal: connection success reported, shutting down portal.")
    return True
