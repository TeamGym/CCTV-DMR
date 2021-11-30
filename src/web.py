from http.server import BaseHTTPRequestHandler, HTTPServer
import logging as l

import http_handlers.http_handler

# Run http server

def run(db):
    def handler(*args):
        http_handlers.http_handler.MyHTTPHandler(db, *args)
    httpd = HTTPServer(('', 8080), handler)

    l.info('start httpd')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    l.info('stop httpd')
    httpd.server_close()
