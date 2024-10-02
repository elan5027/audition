from http.server import BaseHTTPRequestHandler, HTTPServer
import os

class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 라우팅 경로 설정
        if self.path == '/':
            self.handle_home()
        elif self.path.startswith('/success'):
            self.handle_success()
        else:
            self.handle_not_found()

    def handle_home(self):
        # index.html 파일을 읽어서 응답
        if os.path.exists('index.html'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('index.html', 'rb') as file:
                self.wfile.write(file.read())
        else:
            self.send_error(404, 'index.html 파일이 존재하지 않습니다.')

    def handle_success(self):
        # success.html 파일을 읽어서 응답
        if os.path.exists('success.html'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('success.html', 'rb') as file:
                self.wfile.write(file.read())
        else:
            self.send_error(404, 'success.html 파일이 존재하지 않습니다.')
    def handle_not_found(self):
        self.send_response(404)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'<html><body><h1>404 Not Found</h1></body></html>')


def run(server_class=HTTPServer, handler_class=MyHTTPRequestHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()


if __name__ == '__main__':
    run()