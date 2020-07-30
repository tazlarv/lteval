import os
import pathlib
import webbrowser

from http.server import HTTPServer, SimpleHTTPRequestHandler


class NoCacheHTTPRequestHandler(SimpleHTTPRequestHandler):
    # Based on: https://stackoverflow.com/a/25708957
    def end_headers(self):
        self.send_my_headers()
        SimpleHTTPRequestHandler.end_headers(self)

    def send_my_headers(self):
        self.send_header(
            "Cache-Control", "no-cache, no-store, must-revalidate"
        )
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")


def display_webpage(server_dir_path: pathlib.Path, port=8000):
    # Change current (shell) directory to the directory of the lteval web
    os.chdir(server_dir_path)

    # Prepare server with disabled caching
    # (serves data from the current directory)
    server = HTTPServer(("localhost", port), SimpleHTTPRequestHandler)

    # Open webpage
    webbrowser.open("http://localhost:" + str(port) + "/")

    try:
        # Start the server - blocking call
        # Cancel via e.g. Ctrl+C (KeyboardInterrupt)
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
