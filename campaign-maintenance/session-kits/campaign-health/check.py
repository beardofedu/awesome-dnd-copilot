#!/usr/bin/env python3
"""Check explicit campaign metadata; never interpret campaign prose."""
import argparse
import datetime as dt
import errno
import json
import os
import re
import stat
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import quote, urlsplit


class InputError(Exception):
    pass


def fail(message):
    raise InputError(message)


def fields(value, expected, where):
    if not isinstance(value, dict) or set(value) != set(expected):
        fail(f"{where}: expected object fields {', '.join(expected)}")


def array(value, where):
    if not isinstance(value, list):
        fail(f"{where}: expected array")
    return value


def identifier(value, where):
    if not isinstance(value, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value):
        fail(f"{where}: expected lowercase kebab-case ID")
    return value


def date(value, where, today):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        fail(f"{where}: expected YYYY-MM-DD date, not a timestamp")
    try:
        result = dt.date.fromisoformat(value)
    except ValueError:
        fail(f"{where}: invalid calendar date")
    if today is not None and result > today:
        fail(f"{where}: date is after the check date")
    return result


def safe_path(root, value, where):
    if (not isinstance(value, str) or not value or value.startswith('/') or
            '\\' in value or any(not re.fullmatch(r"[A-Za-z0-9._ -]+", p) or p in ('.', '..')
                                   for p in value.split('/'))):
        fail(f"{where}: expected a safe repository-relative POSIX path")
    path = root.joinpath(*PurePosixPath(value).parts)
    try:
        path.resolve().relative_to(root)
    except (ValueError, OSError, RuntimeError):
        fail(f"{where}: path escapes repository or has an invalid symlink")
    return path


def checked_ids(items, where):
    seen = set()
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            fail(f"{where}/{i}: expected object")
        ident = identifier(item.get('id'), f"{where}/{i}/id")
        if ident in seen:
            fail(f"{where}/{i}/id: duplicate ID")
        seen.add(ident)
    return seen


def check(root, manifest_path, today, protected_paths=None):
    path = safe_path(root, manifest_path, 'manifest')
    if protected_paths is not None:
        protected_paths.append(path)
    try:
        with path.open(encoding='utf-8') as f:
            data = json.load(f, object_pairs_hook=unique_object)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        fail(f"cannot read valid manifest: {exc}")
    fields(data, ('version', 'thresholds', 'sessions', 'npcs', 'prep'), '/')
    if type(data['version']) is not int or data['version'] != 1:
        fail('/version: expected 1')
    thresholds = data['thresholds']
    fields(thresholds, ('npcReviewDays', 'prepReviewDays'), '/thresholds')
    for key, value in thresholds.items():
        if type(value) is not int or value < 0:
            fail(f"/thresholds/{key}: expected nonnegative integer")
    for key in ('sessions', 'npcs', 'prep'):
        array(data[key], f'/{key}')
        checked_ids(data[key], f'/{key}')
    if not any(data[key] for key in ('sessions', 'npcs', 'prep')):
        fail('manifest must contain at least one session, NPC, or prep item')
    npc_ids = {n['id'] for n in data['npcs']}
    findings = []

    def add(kind, state, pointer, detail, target=None):
        finding = {'id': f'{kind}:{pointer}', 'state': state, 'kind': kind,
                   'source': {'path': manifest_path, 'pointer': pointer}, 'detail': detail}
        if target is not None:
            finding['target'] = target
        findings.append(finding)

    def file_check(value, pointer, missing_kind):
        p = safe_path(root, value, pointer)
        if protected_paths is not None:
            protected_paths.append(p)
        try:
            info = p.stat()
        except OSError as exc:
            if exc.errno in (errno.ENOENT, errno.ENOTDIR):
                add(missing_kind, 'confirmed', pointer, 'Referenced file does not exist or is not a regular file.', value)
                return
            fail(f"{pointer}: cannot inspect path: {exc}")
        if not stat.S_ISREG(info.st_mode):
            add(missing_kind, 'confirmed', pointer, 'Referenced file does not exist or is not a regular file.', value)

    def review(value, pointer, threshold, kind):
        if value is None:
            add('unreviewed-' + kind, 'unknown', pointer, 'No review date supplied; review status is unknown.')
        else:
            age = (today - date(value, pointer, today)).days
            if age > threshold:
                add('stale-' + kind, 'confirmed', pointer,
                    f'Last review was {age} days ago; configured maximum is {threshold} days.')

    for i, npc in enumerate(data['npcs']):
        p = f'/npcs/{i}'
        fields(npc, ('id', 'file', 'reviewedOn'), p)
        file_check(npc['file'], p + '/file', 'missing-npc-file')
        review(npc['reviewedOn'], p + '/reviewedOn', thresholds['npcReviewDays'], 'npc')
    for i, prep in enumerate(data['prep']):
        p = f'/prep/{i}'
        fields(prep, ('id', 'file', 'reviewStatus', 'reviewedOn'), p)
        file_check(prep['file'], p + '/file', 'missing-prep-file')
        status = prep['reviewStatus']
        if status == 'reviewed':
            if prep['reviewedOn'] is None:
                fail(p + '/reviewedOn: reviewed prep requires a date')
            review(prep['reviewedOn'], p + '/reviewedOn', thresholds['prepReviewDays'], 'prep')
        elif status in ('unreviewed', 'unknown'):
            if prep['reviewedOn'] is not None:
                fail(p + '/reviewedOn: must be null unless reviewed')
            add('unreviewed-prep', 'confirmed' if status == 'unreviewed' else 'unknown',
                p + '/reviewStatus', 'Prep is explicitly unreviewed.' if status == 'unreviewed'
                else 'Prep review status is unknown.')
        else:
            fail(p + '/reviewStatus: expected reviewed, unreviewed, or unknown')
    for i, session in enumerate(data['sessions']):
        p = f'/sessions/{i}'
        fields(session, ('id', 'date', 'recap', 'npcRefs', 'fileRefs'), p)
        date(session['date'], p + '/date', today)
        if session['recap'] is None:
            add('recap-not-supplied', 'unknown', p + '/recap', 'No recap path supplied; whether a recap exists is unknown.')
        else:
            file_check(session['recap'], p + '/recap', 'missing-recap')
        for j, ref in enumerate(array(session['npcRefs'], p + '/npcRefs')):
            pointer = f'{p}/npcRefs/{j}'
            identifier(ref, pointer)
            if ref not in npc_ids:
                add('dangling-npc', 'confirmed', pointer, 'NPC ID is not in this manifest.', ref)
        for j, ref in enumerate(array(session['fileRefs'], p + '/fileRefs')):
            file_check(ref, f'{p}/fileRefs/{j}', 'dangling-file')
    findings.sort(key=lambda f: f['id'])
    return {'version': 1, 'asOf': today.isoformat(), 'manifest': manifest_path, 'findings': findings}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            fail(f'duplicate JSON key: {key}')
        result[key] = value
    return result


def render(report, base, root, output):
    lines = ['# Campaign health (DM-only)', '', f"As of: {report['asOf']} (UTC date)",
             'Scope: supplied metadata and referenced local files only. Unknown is not a pass.', '']
    for state in ('confirmed', 'unknown'):
        entries = [f for f in report['findings'] if f['state'] == state]
        lines += [f'## {state.title()} ({len(entries)})', '']
        for f in entries:
            source = f['source']
            source_link = quote(source['path'], safe='/')
            if base:
                link = base + '/' + source_link
            else:
                relative_source = Path(os.path.relpath(root / source['path'], output)).as_posix()
                link = quote(relative_source, safe='/')
            target = f" Target: `{f['target']}`." if 'target' in f else ''
            lines.append(f"- `{f['kind']}`: {f['detail']}{target} Source: [{source['path']}]({link}) `{source['pointer']}`.")
        if not entries:
            lines.append('- None in supplied metadata.')
        lines.append('')
    return '\n'.join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default='.', help='campaign repository root')
    parser.add_argument('--manifest', required=True, help='repository-relative manifest path')
    parser.add_argument('--output-dir', required=True, help='repository-relative report directory')
    parser.add_argument('--today', help='override UTC date (YYYY-MM-DD)')
    parser.add_argument('--source-base-url', default='', help='HTTPS URL for the exact repository revision')
    args = parser.parse_args(argv)
    try:
        root = Path(args.root).resolve(strict=True)
        if not root.is_dir():
            fail('root must be a directory')
        today = date(args.today, '--today', None) if args.today else dt.datetime.now(dt.timezone.utc).date()
        base = args.source_base_url.rstrip('/')
        if base:
            parts = urlsplit(base)
            if parts.scheme != 'https' or not parts.netloc or parts.username or parts.password or parts.query or parts.fragment or any(c in base for c in ' ()<>\n\r'):
                fail('--source-base-url must be a plain HTTPS revision URL without credentials, query, or fragment')
        output = safe_path(root, args.output_dir, '--output-dir')
        protected_paths = []
        report = check(root, args.manifest, today, protected_paths)
        for name in ('report.json', 'summary.md'):
            candidate = safe_path(root, args.output_dir + '/' + name, '--output-dir')
            if candidate.is_symlink():
                fail('output files must not be symlinks')
            for protected in protected_paths:
                if candidate.resolve() == protected.resolve():
                    fail('output must not overwrite manifest or referenced source files')
                try:
                    same_file = candidate.samefile(protected)
                except FileNotFoundError:
                    same_file = False
                except OSError as exc:
                    fail(f'cannot safely inspect output path: {exc}')
                if same_file:
                    fail('output must not overwrite manifest or referenced source files')
        output.mkdir(parents=True, exist_ok=True)
        (output / 'report.json').write_text(json.dumps(report, indent=2, ensure_ascii=True) + '\n', encoding='utf-8')
        (output / 'summary.md').write_text(render(report, base, root, output), encoding='utf-8')
        return 1 if any(f['state'] == 'confirmed' for f in report['findings']) else 0
    except (InputError, OSError, ValueError) as exc:
        print(f'campaign-health: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
