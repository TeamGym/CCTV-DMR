# path: /

def root(h):
    h.set_response(200)
    h.wfile.write('test response'.encode('utf-8'))
