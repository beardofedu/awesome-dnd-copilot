import datetime as dt
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('campaign_health', HERE / 'check.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class HealthTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.root = Path(self.tmp.name).resolve()
        self.addCleanup(self.tmp.cleanup)
        for name in ('recap.md', 'npc.md', 'prep.md', 'note.md'):
            (self.root / name).write_text('fictional', encoding='utf-8')
        self.data = {
            'version': 1, 'thresholds': {'npcReviewDays': 10, 'prepReviewDays': 3},
            'sessions': [{'id': 'session-1', 'date': '2026-01-01', 'recap': 'recap.md',
                          'npcRefs': ['npc-1'], 'fileRefs': ['note.md']}],
            'npcs': [{'id': 'npc-1', 'file': 'npc.md', 'reviewedOn': '2026-01-10'}],
            'prep': [{'id': 'prep-1', 'file': 'prep.md', 'reviewStatus': 'reviewed',
                      'reviewedOn': '2026-01-17'}],
        }

    def run_check(self, today=dt.date(2026, 1, 20)):
        (self.root / 'manifest.json').write_text(json.dumps(self.data), encoding='utf-8')
        return checker.check(self.root, 'manifest.json', today)

    def test_thresholds_are_strict_and_calendar_based(self):
        self.assertEqual(self.run_check()['findings'], [])  # exactly at each limit
        result = self.run_check(dt.date(2026, 1, 21))
        self.assertEqual({f['kind'] for f in result['findings']}, {'stale-npc', 'stale-prep'})
        self.assertTrue(all(f['state'] == 'confirmed' for f in result['findings']))
        self.data['thresholds']['prepReviewDays'] = 0
        self.data['prep'][0]['reviewedOn'] = '2026-01-20'
        self.assertEqual(self.run_check()['findings'], [])
        self.assertIn('stale-prep', {f['kind'] for f in self.run_check(dt.date(2026, 1, 21))['findings']})

    def test_missing_and_dangling_explicit_references(self):
        self.data['sessions'][0].update(recap='missing.md', npcRefs=['ghost'], fileRefs=['missing-note.md'])
        result = self.run_check()
        self.assertEqual({f['kind'] for f in result['findings']}, {'missing-recap', 'dangling-npc', 'dangling-file'})
        self.assertEqual({f['source']['pointer'] for f in result['findings']},
                         {'/sessions/0/recap', '/sessions/0/npcRefs/0', '/sessions/0/fileRefs/0'})

    def test_unknown_is_not_confirmed_and_unreviewed_is(self):
        self.data['sessions'][0]['recap'] = None
        self.data['npcs'][0]['reviewedOn'] = None
        self.data['prep'][0].update(reviewStatus='unreviewed', reviewedOn=None)
        findings = {f['kind']: f['state'] for f in self.run_check()['findings']}
        self.assertEqual(findings, {'recap-not-supplied': 'unknown', 'unreviewed-npc': 'unknown',
                                    'unreviewed-prep': 'confirmed'})
        self.data['prep'][0]['reviewStatus'] = 'unknown'
        findings = {f['kind']: f['state'] for f in self.run_check()['findings']}
        self.assertEqual(findings['unreviewed-prep'], 'unknown')

    def test_invalid_inputs_fail_instead_of_empty_report(self):
        for mutate in (
            lambda d: d.pop('sessions'),
            lambda d: d['thresholds'].update(npcReviewDays=-1),
            lambda d: d['npcs'][0].update(reviewedOn='2026-01-10T23:00:00-05:00'),
            lambda d: d['npcs'][0].update(reviewedOn='2026-01-21'),
            lambda d: d['prep'][0].update(reviewStatus='reviewed', reviewedOn=None),
            lambda d: d['sessions'][0].update(recap='../outside'),
        ):
            original = json.loads(json.dumps(self.data))
            mutate(self.data)
            with self.assertRaises(checker.InputError):
                self.run_check()
            self.data = original
        (self.root / 'manifest.json').write_text('{"version":1,"version":1}', encoding='utf-8')
        with self.assertRaises(checker.InputError):
            checker.check(self.root, 'manifest.json', dt.date(2026, 1, 20))
        with self.assertRaises(checker.InputError):
            checker.check(self.root, 'absent.json', dt.date(2026, 1, 20))

    def test_symlink_escape_is_rejected(self):
        (self.root / 'escape').symlink_to(self.root.parent, target_is_directory=True)
        self.data['sessions'][0]['fileRefs'] = ['escape/secret.md']
        with self.assertRaises(checker.InputError):
            self.run_check()

    def test_default_date_uses_utc_not_local_offset(self):
        class Clock(dt.datetime):
            @classmethod
            def now(cls, tz=None):
                self.assertEqual(tz, dt.timezone.utc)
                return dt.datetime(2026, 1, 21, 0, 30, tzinfo=dt.timezone.utc)
        self.run_check()
        with patch.object(checker.dt, 'datetime', Clock):
            status = checker.main(['--root', str(self.root), '--manifest', 'manifest.json', '--output-dir', 'out'])
        self.assertEqual(status, 1)
        report = json.loads((self.root / 'out/report.json').read_text(encoding='utf-8'))
        self.assertEqual(report['asOf'], '2026-01-21')

    def test_cli_writes_deterministic_reports_and_returns_failure(self):
        self.data['prep'][0].update(reviewStatus='unreviewed', reviewedOn=None)
        self.run_check()
        args = ['--root', str(self.root), '--manifest', 'manifest.json', '--output-dir', 'out',
                '--today', '2026-01-20', '--source-base-url', 'https://github.com/o/r/blob/abc']
        self.assertEqual(checker.main(args), 1)
        first = (self.root / 'out/report.json').read_bytes()
        summary = (self.root / 'out/summary.md').read_text(encoding='utf-8')
        self.assertIn('https://github.com/o/r/blob/abc/manifest.json', summary)
        self.assertIn('/prep/0/reviewStatus', summary)
        self.assertEqual(checker.main(args), 1)
        self.assertEqual(first, (self.root / 'out/report.json').read_bytes())
        self.assertEqual(checker.main(args[:-4] + ['--today', '2026-01-20']), 1)
        summary = (self.root / 'out/summary.md').read_text(encoding='utf-8')
        self.assertIn('[manifest.json](../manifest.json)', summary)
        self.assertEqual(checker.main(args[:-4] + ['--today', 'bad']), 2)

    def test_cli_missing_input_and_unknown_only(self):
        args = ['--root', str(self.root), '--manifest', 'manifest.json',
                '--output-dir', 'out', '--today', '2026-01-20']
        self.assertEqual(checker.main(args), 2)
        self.assertFalse((self.root / 'out').exists())
        self.data['prep'][0].update(reviewStatus='unknown', reviewedOn=None)
        self.run_check()
        self.assertEqual(checker.main(args), 0)
        report = json.loads((self.root / 'out/report.json').read_text(encoding='utf-8'))
        self.assertEqual(report['findings'][0]['state'], 'unknown')

    def test_output_file_symlink_is_rejected(self):
        self.run_check()
        (self.root / 'out').mkdir()
        (self.root / 'out/report.json').symlink_to(self.root / 'note.md')
        self.assertEqual(checker.main(['--root', str(self.root), '--manifest', 'manifest.json',
                                       '--output-dir', 'out', '--today', '2026-01-20']), 2)
        self.assertEqual((self.root / 'note.md').read_text(encoding='utf-8'), 'fictional')

    def test_output_hardlinks_to_manifest_or_referenced_source_are_rejected(self):
        manifest = self.root / 'manifest.json'
        manifest.write_text(json.dumps(self.data), encoding='utf-8')
        (self.root / 'out').mkdir()
        (self.root / 'out/report.json').hardlink_to(manifest)
        original_manifest = manifest.read_bytes()
        args = ['--root', str(self.root), '--manifest', 'manifest.json',
                '--output-dir', 'out', '--today', '2026-01-20']
        self.assertEqual(checker.main(args), 2)
        self.assertEqual(manifest.read_bytes(), original_manifest)

        (self.root / 'out/report.json').unlink()
        (self.root / 'out/report.json').hardlink_to(self.root / 'note.md')
        self.data['sessions'][0]['fileRefs'] = ['note.md']
        manifest.write_text(json.dumps(self.data), encoding='utf-8')
        original_source = (self.root / 'note.md').read_bytes()
        self.assertEqual(checker.main(args), 2)
        self.assertEqual((self.root / 'note.md').read_bytes(), original_source)

    def test_rerun_with_reference_below_file_reports_dangling_reference(self):
        self.data['sessions'][0]['fileRefs'] = ['note.md/child.md']
        self.run_check()
        args = ['--root', str(self.root), '--manifest', 'manifest.json',
                '--output-dir', 'out', '--today', '2026-01-20']
        self.assertEqual(checker.main(args), 1)
        self.assertEqual(checker.main(args), 1)
        report = json.loads((self.root / 'out/report.json').read_text(encoding='utf-8'))
        self.assertIn('dangling-file', {finding['kind'] for finding in report['findings']})

    def test_output_reports_sharing_hardlink_are_rejected(self):
        self.run_check()
        (self.root / 'out').mkdir()
        shared = self.root / 'shared.dat'
        shared.write_text('shared output target', encoding='utf-8')
        (self.root / 'out/report.json').hardlink_to(shared)
        (self.root / 'out/summary.md').hardlink_to(shared)
        args = ['--root', str(self.root), '--manifest', 'manifest.json',
                '--output-dir', 'out', '--today', '2026-01-20']
        self.assertEqual(checker.main(args), 2)
        self.assertEqual(shared.read_text(encoding='utf-8'), 'shared output target')

    def test_output_path_matching_referenced_source_is_rejected(self):
        self.data['sessions'][0]['fileRefs'] = ['out/report.json']
        (self.root / 'out').mkdir()
        output_file = self.root / 'out/report.json'
        output_file.write_text('campaign source', encoding='utf-8')
        self.run_check()
        self.assertEqual(checker.main(['--root', str(self.root), '--manifest', 'manifest.json',
                                       '--output-dir', 'out', '--today', '2026-01-20']), 2)
        self.assertEqual(output_file.read_text(encoding='utf-8'), 'campaign source')


if __name__ == '__main__':
    unittest.main()
