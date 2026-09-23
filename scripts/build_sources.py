#!/usr/bin/env python3
"""Build selected source snapshots and export their frontend artifacts."""
import argparse
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
OMIT = {'.git', 'node_modules', '__pycache__', '.webmetabench-installed.json'}


def ignore(directory, names):
    return [n for n in names if n in OMIT or n == '.env' or n.startswith('.env.')]


def beneath(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f'Path escapes root: {relative}')
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    select = parser.add_mutually_exclusive_group(required=True)
    select.add_argument('--all', action='store_true')
    select.add_argument('--project')
    select.add_argument('--sample')
    parser.add_argument('--variant', choices=['gold', 'defect', 'both'], default='defect')
    parser.add_argument('--skip-install', action='store_true')
    parser.add_argument('--replace', action='store_true', help='Replace the selected existing artifacts after a successful build')
    args = parser.parse_args()
    samples = []
    for kind in ['single_defect', 'multi_defect']:
        samples.extend(json.loads((ROOT / f'dataset/{kind}.json').read_text())['samples'])
    selected = [r for r in samples if args.all or r['project_id'] == args.project or r['sample_id'] == args.sample]
    if not selected:
        parser.error('No matching samples')
    recipes = json.loads((ROOT / 'dataset/build_recipes.json').read_text())['variants']
    variants = ['gold', 'defect'] if args.variant == 'both' else [args.variant]
    jobs = {}
    for row in selected:
        for variant in variants:
            jobs[row['versions'][variant]] = row['source_versions'][variant]
    log_dir = ROOT / 'outputs/build_logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    environment = {**os.environ, 'CI': '1', 'HUSKY': '0', 'PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD': '1'}
    environment.setdefault('NODE_OPTIONS', '--max-old-space-size=8192')
    for index, (output_version, source_version) in enumerate(jobs.items(), 1):
        source = beneath(ROOT / 'sources', source_version)
        recipe = recipes[source_version]
        if not source.is_dir():
            parser.error(f'Missing sources: {source_version}; download them with --kind sources')
        dest = beneath(ROOT / 'projects', output_version)
        if dest.exists() and not args.replace:
            parser.error(f'Artifacts already exist: {output_version}; pass --replace to overwrite this variant')
        log_path = log_dir / (output_version.replace('/', '__') + '.log')
        print(f'[{index}/{len(jobs)}] building {source_version}', flush=True)
        with log_path.open('w') as log:
            for phase in ['install', 'build']:
                if phase == 'install' and args.skip_install:
                    continue
                for step in recipe[phase]:
                    cwd = beneath(source, step.get('cwd', '.'))
                    env = {**environment, **recipe.get('env', {}), **step.get('env', {})}
                    line = f'$ (cd {step.get("cwd", ".")} && {shlex.join(step["command"])})'
                    print(line, flush=True)
                    log.write(line + '\n')
                    log.flush()
                    proc = subprocess.Popen(step['command'], cwd=cwd, env=env, stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT, text=True, errors='replace')
                    for line in proc.stdout:
                        print(line, end='', flush=True)
                        log.write(line)
                    if proc.wait():
                        raise SystemExit(f'{phase} failed for {source_version}; log: {log_path}')
        dest.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='build-', dir=dest.parent) as temporary:
            assembled = Path(temporary) / 'artifact'
            assembled.mkdir()
            for rule in recipe['copy']:
                src = beneath(source, rule['from'])
                target = beneath(assembled, rule['to'])
                if src.is_dir():
                    shutil.copytree(src, target, dirs_exist_ok=True, ignore=ignore)
                elif src.is_file():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, target)
                else:
                    raise RuntimeError(f'Build output is missing: {src}')
            if not (assembled / 'index.html').is_file():
                raise RuntimeError(f'No index.html in generated artifact: {source_version}')
            backup = dest.with_name(dest.name + '.previous')
            if backup.exists():
                raise RuntimeError(f'Existing backup must be handled first: {backup}')
            if dest.exists():
                dest.rename(backup)
            try:
                assembled.rename(dest)
            except Exception:
                if backup.exists():
                    backup.rename(dest)
                raise
            if backup.exists():
                shutil.rmtree(backup)
        print(f'[{index}/{len(jobs)}] built: {output_version}; log: {log_path}', flush=True)


if __name__ == '__main__':
    main()
