#!/usr/bin/env python3
"""Download built resources or source snapshots, without content-hash checks."""
import argparse
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    select = parser.add_mutually_exclusive_group(required=True)
    select.add_argument('--all', action='store_true')
    select.add_argument('--project', action='append', default=[])
    parser.add_argument('--kind', choices=['static', 'sources', 'both'], default='static')
    args = parser.parse_args()
    records = json.loads((ROOT / 'dataset/provenance.json').read_text())['projects']
    known = {p['project_id']: p for p in records}
    unknown = set(args.project) - known.keys()
    if unknown:
        parser.error('Unknown projects: ' + ', '.join(sorted(unknown)))
    selected = records if args.all else [known[k] for k in args.project]
    kinds = ['static', 'sources'] if args.kind == 'both' else [args.kind]
    jobs = [(p, kind) for p in selected for kind in kinds]
    for index, (project, kind) in enumerate(jobs, 1):
        bundle = project['downloads'][kind]
        pid = project['project_id']
        destination = ROOT / ('projects' if kind == 'static' else 'sources')
        destination.mkdir(exist_ok=True)
        dest = destination / pid
        marker = dest / '.webmetabench-installed.json'
        revision = bundle['release']
        if marker.exists() and json.loads(marker.read_text()).get('release') == revision:
            print(f'[{index}/{len(jobs)}] already installed: {pid} ({kind})', flush=True)
            continue
        cache = ROOT / 'downloads' / revision
        cache.mkdir(parents=True, exist_ok=True)
        files = []
        for asset in bundle['assets']:
            name = asset['name']
            if Path(name).name != name:
                raise ValueError('Invalid asset name')
            file = cache / name
            if not file.exists() or file.stat().st_size != asset['size_bytes']:
                partial = cache / (name + '.partial')
                if partial.exists() and partial.stat().st_size > asset['size_bytes']:
                    partial.unlink()
                if not partial.exists() or partial.stat().st_size < asset['size_bytes']:
                    subprocess.run(['curl', '--fail', '--location', '--retry', '4',
                                    '--continue-at', '-', '--output', str(partial), asset['url']], check=True)
                if partial.stat().st_size != asset['size_bytes']:
                    raise RuntimeError(f'Incomplete download: {name}; rerun to resume')
                partial.replace(file)
            files.append(file)
        with tempfile.TemporaryDirectory(prefix='extract-', dir=destination) as temporary:
            temp = Path(temporary)
            archive = files[0]
            if len(files) > 1:
                archive = temp / 'joined.tar.gz'
                with archive.open('wb') as out:
                    for file in files:
                        with file.open('rb') as inp:
                            shutil.copyfileobj(inp, out, 8 * 1024 * 1024)
            unpacked = temp / 'unpacked'
            unpacked.mkdir()
            with tarfile.open(archive, 'r:gz') as tar:
                for member in tar:
                    rel = PurePosixPath(member.name)
                    if rel.is_absolute() or '..' in rel.parts or not rel.parts or rel.parts[0] != pid:
                        raise ValueError(f'Unsafe archive path: {member.name}')
                    if not (member.isfile() or member.isdir()):
                        raise ValueError(f'Unsupported archive entry: {member.name}')
                    target = unpacked.joinpath(*rel.parts)
                    if member.isdir():
                        target.mkdir(parents=True, exist_ok=True)
                    else:
                        target.parent.mkdir(parents=True, exist_ok=True)
                        with tar.extractfile(member) as inp, target.open('wb') as out:
                            shutil.copyfileobj(inp, out)
                        target.chmod(0o755 if member.mode & 0o111 else 0o644)
            new = unpacked / pid
            (new / '.webmetabench-installed.json').write_text(json.dumps({'release': revision, 'kind': kind}))
            backup = destination / (pid + '.previous')
            if backup.exists():
                raise RuntimeError(f'Interrupted update exists: {backup}; preserve or remove it first')
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
        print(f'[{index}/{len(jobs)}] installed: {pid} ({kind})', flush=True)


if __name__ == '__main__':
    main()
