#!/usr/bin/env python3
"""Fetch individually versioned frontend bundles from this repository's Release."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--all', action='store_true')
    group.add_argument('--project', action='append', default=[])
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'dataset/manifest.json').read_text())
    known = {p['project_id']: p for p in manifest['projects']}
    unknown = set(args.project) - known.keys()
    if unknown:
        parser.error('Unknown projects: ' + ', '.join(sorted(unknown)))
    selected = list(known.values()) if args.all else [known[k] for k in args.project]
    downloads = ROOT / 'downloads'
    projects = ROOT / 'projects'
    downloads.mkdir(exist_ok=True)
    projects.mkdir(exist_ok=True)
    for index, project in enumerate(selected, 1):
        pid = project['project_id']
        expected = project['sha256']
        dest = projects / pid
        marker = dest / '.webmetabench-installed.json'
        if marker.exists() and json.loads(marker.read_text()).get('sha256') == expected:
            print(f'[{index}/{len(selected)}] already installed: {pid}', flush=True)
            continue
        print(f'[{index}/{len(selected)}] downloading: {pid}', flush=True)
        paths = []
        for part in project['assets']:
            name = part['name']
            if Path(name).name != name:
                raise ValueError('Invalid asset name')
            file = downloads / name
            if not file.exists() or digest(file) != part['sha256']:
                partial = downloads / (name + '.partial')
                subprocess.run(['curl', '--fail', '--location', '--retry', '4',
                                '--continue-at', '-', '--output', str(partial), part['url']], check=True)
                if digest(partial) != part['sha256']:
                    partial.unlink()
                    raise RuntimeError(f'Checksum mismatch: {name}; rerun to download again')
                partial.replace(file)
            paths.append(file)
        with tempfile.TemporaryDirectory(prefix='extract-', dir=downloads) as temporary:
            temp = Path(temporary)
            if len(paths) == 1:
                archive = paths[0]
            else:
                archive = temp / 'joined.tar.gz'
                with archive.open('wb') as out:
                    for file in paths:
                        with file.open('rb') as inp:
                            shutil.copyfileobj(inp, out, 8 * 1024 * 1024)
            if digest(archive) != expected:
                raise RuntimeError(f'Bundle checksum mismatch: {pid}')
            extracted = temp / 'unpacked'
            extracted.mkdir()
            with tarfile.open(archive, 'r:gz') as tar:
                for member in tar:
                    path = PurePosixPath(member.name)
                    if path.is_absolute() or '..' in path.parts or not path.parts or path.parts[0] != pid:
                        raise ValueError(f'Unsafe archive path: {member.name}')
                    if not (member.isfile() or member.isdir()):
                        raise ValueError(f'Unsupported archive entry: {member.name}')
                    target = extracted.joinpath(*path.parts)
                    if member.isdir():
                        target.mkdir(parents=True, exist_ok=True)
                    else:
                        target.parent.mkdir(parents=True, exist_ok=True)
                        with tar.extractfile(member) as inp, target.open('wb') as out:
                            shutil.copyfileobj(inp, out)
            new = extracted / pid
            (new / '.webmetabench-installed.json').write_text(json.dumps({'sha256': expected}))
            backup = projects / (pid + '.previous')
            if backup.exists():
                raise RuntimeError(f'Previous interrupted update exists: {backup}; preserve or remove it first')
            if dest.exists():
                dest.rename(backup)
            try:
                new.rename(dest)
            except Exception:
                if backup.exists():
                    backup.rename(dest)
                raise
            if backup.exists():
                shutil.rmtree(backup)
        print(f'[{index}/{len(selected)}] installed: {pid}', flush=True)


if __name__ == '__main__':
    main()

