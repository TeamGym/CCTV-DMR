from http.server import BaseHTTPRequestHandler, HTTPServer
import logging as l

import http_handlers.root_handler

_handlers = {
    '/': ('GET POST', http_handlers.root_handler.root),
    # '/register': ('POST', self._register),
}

class MyHTTPHandler(BaseHTTPRequestHandler):
    def __init__(self, db, *args, **kwargs):
        self.db = db
        super().__init__(*args, **kwargs)

    def _handle(self, method):
        l.info('%s %s from %s:%s',
               method, self.path, self.client_address[0], self.client_address[1])
        hdl = _handlers.get(self.path)
        if hdl is not None and method in hdl[0]:
            try:
                hdl[1](self)
            except Exception as err:
                l.exception(err)
                self._error(500)
        else:
            self._error(404)

    def error(self, rescode):
        """Show error page with given response code"""
        self.set_response(rescode)
        self.wfile.write('Error: {}'.format(rescode).encode('utf-8'))

    def set_response(self, rescode):
        """Set response code and set default headers"""
        self.send_response(rescode)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

    def do_GET(self):
        self._handle('GET')

    def do_POST(self):
        self._handle('POST')
