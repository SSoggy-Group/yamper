import http.server
import json
import urllib.parse
import html
from . import wifi

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Yamper WiFi Setup</title>
    <style>
        body {{ font-family: sans-serif; background: #f0f0f5; text-align: center; margin: 0; padding: 20px; }}
        .container {{ background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); max-width: 400px; margin: auto; }}
        h1 {{ color: #333; }}
        select, input, button {{ width: 100%; margin-top: 10px; padding: 12px; border-radius: 6px; border: 1px solid #ccc; font-size: 16px; box-sizing: border-box; }}
        button {{ background: #007bff; color: white; border: none; font-weight: bold; cursor: pointer; margin-top: 20px; }}
        button:active {{ background: #0056b3; }}
        #status {{ margin-top: 20px; font-weight: bold; color: #d9534f; }}
        .success-msg {{ color: #5cb85c !important; }}
        .error-msg {{ color: #d9534f !important; }}
        .info-msg {{ color: #5bc0de !important; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Yamper Setup</h1>
        <p>Select your WiFi network to connect Yamper to the internet.</p>
        <form id="setupForm" method="POST" action="/connect">
            <select name="ssid">
                <option value="" disabled selected>Select network...</option>
                {options}
            </select>
            <input type="text" name="manual_ssid" placeholder="Or type hidden SSID" />
            <input type="password" name="password" placeholder="WiFi Password (optional)" />
            <button type="submit">Connect</button>
        </form>
        <div id="status" class="{status_class}">{status_msg}</div>
    </div>
</body>
</html>
"""

# Module-level state
setup_complete = False
chosen_ssid = None
chosen_password = None
current_error_msg = None
cached_networks = []

class PortalHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress logging to keep console clean
        pass

    def do_GET(self):
        global current_error_msg
        if self.path == '/':
            networks = cached_networks
            options = "".join([f'<option value="{html.escape(n)}">{html.escape(n)}</option>' for n in networks])
            if not networks:
                options = '<option value="" disabled>No networks found</option>'
                
            status_msg = current_error_msg if current_error_msg else "Portal ready"
            status_class = "error-msg" if current_error_msg else "info-msg"
            
            html_content = HTML_TEMPLATE.format(options=options, status_msg=status_msg, status_class=status_class)
            
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))
        elif self.path == '/status':
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": setup_complete}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        global setup_complete, chosen_ssid, chosen_password
        if self.path == '/connect':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            fields = urllib.parse.parse_qs(post_data)
            
            ssid = fields.get('ssid', [''])[0]
            manual_ssid = fields.get('manual_ssid', [''])[0]
            password = fields.get('password', [''])[0]
            
            chosen_ssid = manual_ssid if manual_ssid else ssid
            print(f"Portal: user submitted SSID '{chosen_ssid}'")
            
            # Save credentials and exit the handler loop
            chosen_password = password
            setup_complete = True
            
            msg = f"Connecting to '{html.escape(chosen_ssid)}'... The setup hotspot will now close. Please wait to see if Yamper successfully connects."
            options = f'<option value="{html.escape(chosen_ssid)}" selected>{html.escape(chosen_ssid)}</option>'
            html_content = HTML_TEMPLATE.format(options=options, status_msg=msg, status_class="success-msg")
            
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def run_portal(port, error_msg=None, networks=None, server_class=http.server.HTTPServer, handler_class=PortalHandler):
    global setup_complete, chosen_ssid, chosen_password, current_error_msg, cached_networks
    setup_complete = False
    chosen_ssid = None
    chosen_password = None
    current_error_msg = error_msg
    cached_networks = networks or []
    
    server_address = ('', port)
    
    try:
        httpd = server_class(server_address, handler_class)
        print(f"Portal running on port {port}...")
    except OSError as e:
        print(f"Failed to start portal on port {port}: {e}")
        # Try fallback port if 80 is privileged and we are not root
        if port == 80:
            print("Trying fallback port 8080...")
            server_address = ('', 8080)
            httpd = server_class(server_address, handler_class)
            print("Portal running on port 8080...")
        else:
            raise

    httpd.timeout = 1
    while not setup_complete:
        httpd.handle_request()
        
    print("Portal: connection details submitted, shutting down server.")
    return chosen_ssid, chosen_password
