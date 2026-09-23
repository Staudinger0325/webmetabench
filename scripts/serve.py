#!/usr/bin/env python3
"""Serve one selected built frontend, never the dataset root or annotations."""
import argparse
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class Handler(SimpleHTTPRequestHandler):
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map,
                      '.js': 'application/javascript', '.mjs': 'application/javascript',
                      '.wasm': 'application/wasm', '.glb': 'model/gltf-binary',
                      '.gltf': 'model/gltf+json', '.webp': 'image/webp',
                      '.avif': 'image/avif', '.mp4': 'video/mp4', '.webm': 'video/webm'}

    def list_directory(self, path):
        self.send_error(404)
        return None

    def send_head(self):
        self.byte_range = None
        request_path = unquote(urlsplit(self.path).path)
        if any(p.startswith('.') for p in request_path.split('/') if p) or request_path.endswith('.map'):
            self.send_error(404)
            return None
        base = Path(self.directory).resolve()
        target = Path(self.translate_path(self.path)).resolve()
        if not target.is_relative_to(base):
            self.send_error(403)
            return None
        if not target.exists() and not Path(request_path).suffix:
            self.path = '/index.html'
            target = base / 'index.html'
        requested = self.headers.get('Range')
        if requested and target.is_file():
            match = re.fullmatch(r'bytes=(\d*)-(\d*)', requested.strip())
            size = target.stat().st_size
            if not match or not size or not any(match.groups()):
                self.send_error(416)
                return None
            left, right = match.groups()
            start = int(left) if left else max(0, size - int(right))
            end = min(int(right), size - 1) if left and right else size - 1
            if start > end or start >= size:
                self.send_response(416)
                self.send_header('Content-Range', f'bytes */{size}')
                self.send_header('Content-Length', '0')
                self.end_headers()
                return None
            file = target.open('rb')
            file.seek(start)
            self.byte_range = end - start + 1
            self.send_response(206)
            self.send_header('Content-Type', self.guess_type(str(target)))
            self.send_header('Accept-Ranges', 'bytes')
            self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
            self.send_header('Content-Length', str(self.byte_range))
            self.end_headers()
            return file
        return super().send_head()

    def copyfile(self, source, outputfile):
        if self.byte_range is None:
            return super().copyfile(source, outputfile)
        remaining = self.byte_range
        while remaining:
            block = source.read(min(1024 * 1024, remaining))
            if not block:
                break
            outputfile.write(block)
            remaining -= len(block)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sample', required=True)
    parser.add_argument('--variant', choices=['gold', 'defect'], default='defect')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8080)
    parser.add_argument('--catalogue', type=Path)
    parser.add_argument('--projects-root', type=Path, default=ROOT / 'projects')
    args = parser.parse_args()
    if args.catalogue:
        rows = json.loads(args.catalogue.read_text())['samples']
    else:
        rows = []
        for name in ['single_defect', 'multi_defect']:
            rows.extend(json.loads((ROOT / f'dataset/{name}.json').read_text())['samples'])
    selected = next((r for r in rows if r['sample_id'] == args.sample), None)
    if selected is None:
        parser.error('Unknown sample ID')
    root = args.projects_root.resolve()
    directory = (root / selected['versions'][args.variant]).resolve()
    if not directory.is_relative_to(root) or not (directory / 'index.html').is_file():
        parser.error('Selected static files are missing; download the project first')
    server = ThreadingHTTPServer((args.host, args.port), functools.partial(Handler, directory=str(directory)))
    print(f'Serving {args.sample} ({args.variant}) on http://{args.host}:{args.port}/', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()

