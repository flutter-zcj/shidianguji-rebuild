#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
识典古籍 H5 静态服务（含后端代理）

用途：把 `npm run build:h5` 产物起成本地服务，并把 /api/ancientlib 代理到
RuoYi-FastAPI + module_guji 后端，避免跨域与地址不通的问题。

用法：
    python3 scripts/serve_h5.py --port 8080 --backend http://127.0.0.1:9099
"""

import argparse
import os
import urllib.error
import urllib.request
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

BACKEND = 'http://127.0.0.1:9099'


class GujiHandler(SimpleHTTPRequestHandler):
    """静态文件服务 + 古籍接口反向代理"""

    def do_GET(self):
        if self._proxy():
            return
        super().do_GET()

    def do_POST(self):
        if self._proxy():
            return
        super().do_POST()

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')

    def _proxy(self):
        """把 /api/ancientlib 前缀的请求转发到后端，返回是否已处理"""
        if not self.path.startswith('/api/'):
            return False
        length = int(self.headers.get('Content-Length') or 0)
        body = self.rfile.read(length) if length else None
        req = urllib.request.Request(
            BACKEND + self.path,
            data=body,
            method=self.command,
        )
        for key in ('Content-Type', 'X-User-Id', 'Authorization'):
            value = self.headers.get(key)
            if value:
                req.add_header(key, value)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
                status = resp.status
                content_type = resp.headers.get('Content-Type', 'application/json')
        except urllib.error.HTTPError as err:
            data = err.read()
            status = err.code
            content_type = 'application/json'
        except Exception as err:  # noqa: BLE001
            data = str(err).encode('utf-8')
            status = 502
            content_type = 'text/plain; charset=utf-8'
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(data)))
        self._cors()
        self.end_headers()
        self.wfile.write(data)
        return True


def main():
    global BACKEND
    parser = argparse.ArgumentParser(description='识典古籍 H5 静态服务')
    parser.add_argument('--dir', default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dist', 'build', 'h5'), help='静态产物目录')
    parser.add_argument('--port', type=int, default=8080, help='监听端口')
    parser.add_argument('--backend', default=BACKEND, help='后端地址')
    args = parser.parse_args()

    BACKEND = args.backend.rstrip('/')
    root = os.path.abspath(args.dir)
    handler = partial(GujiHandler, directory=root)
    server = ThreadingHTTPServer(('0.0.0.0', args.port), handler)
    print(f'serving {root} on http://127.0.0.1:{args.port} -> backend {BACKEND}')
    server.serve_forever()


if __name__ == '__main__':
    main()
