try:
    from http.server import HTTPServer, BaseHTTPRequestHandler
except ImportError:
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(404)
        self.end_headers()
        self.wfile.write("".encode('utf-8'))

        print("RequestHandler is not implemented yet")

    def do_POST(self):
        self.send_response(404)
        self.end_headers()
        self.wfile.write("".encode('utf-8'))
        print("RequestHandler is not implemented yet")


def server(request_handler, host='', port=80):
    http_server = HTTPServer((host, port), request_handler)
    print("Starting server on %s:%d" % (host, port))
    try:
        http_server.serve_forever()

    except KeyboardInterrupt:
        print("Shutting server down")
        http_server.shutdown()
        return
