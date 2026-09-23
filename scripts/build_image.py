#!/usr/bin/env python3
"""Build one large resource image, or an image restricted to a project/sample."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--all', action='store_true')
    group.add_argument('--project')
    group.add_argument('--sample')
    parser.add_argument('--tag', default='webmetabench-projects:local')
    parser.add_argument('--platform', help='For example linux/amd64; requires Docker support')
    parser.add_argument('--base-image', default='python:3.12-slim-bookworm')
    args = parser.parse_args()
    rows = []
    for name in ['single_defect', 'multi_defect']:
        rows.extend(json.loads((ROOT / f'dataset/{name}.json').read_text())['samples'])
    selected = [r for r in rows if args.all or r['project_id'] == args.project or r['sample_id'] == args.sample]
    if not selected:
        parser.error('No matching samples')
    versions = sorted({v for r in selected for v in r['versions'].values()})
    for version in versions:
        if not (ROOT / 'projects' / version / 'index.html').is_file():
            parser.error(f'Missing project resources: {version}; run download_projects.py first')
    build = ROOT / '.build'
    build.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='image-', dir=build) as temporary:
        temp = Path(temporary)
        catalogue = {'samples': [{k: r[k] for k in ['sample_id', 'project_id', 'versions']} for r in selected]}
        (temp / 'catalogue.json').write_text(json.dumps(catalogue))
        command = ['docker', 'build', '--tag', args.tag, '--build-arg', f'BASE_IMAGE={args.base_image}']
        if args.platform:
            command.extend(['--platform', args.platform])
        command.append('-')
        print(f'Building {args.tag}: {len(selected)} samples, {len(versions)} static variants', flush=True)
        proc = subprocess.Popen(command, stdin=subprocess.PIPE)
        try:
            with tarfile.open(fileobj=proc.stdin, mode='w|', dereference=True) as tar:
                tar.add(ROOT / 'docker/Dockerfile.projects', arcname='Dockerfile')
                tar.add(ROOT / 'scripts/serve.py', arcname='serve.py')
                tar.add(temp / 'catalogue.json', arcname='catalogue.json')
                for version in versions:
                    tar.add(ROOT / 'projects' / version, arcname='projects/' + version)
        except Exception:
            proc.kill()
            proc.wait()
            raise
        finally:
            proc.stdin.close()
        if proc.wait():
            raise SystemExit(proc.returncode)


if __name__ == '__main__':
    main()

