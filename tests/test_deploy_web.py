import os
import shutil
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = "dummy"


class DeployWebTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="zonagris-deploy-test-"))
        self.remote = self.tmp / "remote"
        self.bin = self.tmp / "bin"
        self.bin.mkdir()
        self._write_fakes()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write_fakes(self):
        ssh = self.bin / "ssh"
        ssh.write_text(
            "#!/usr/bin/env bash\n"
            'cmd="${!#}"\n'
            'exec bash -c "$cmd"\n',
            encoding="utf-8",
        )
        ssh.chmod(0o755)
        rsync = self.bin / "rsync"
        rsync.write_text(
            "#!/usr/bin/env bash\n"
            "set -e\n"
            'src="${@: -2:1}"\n'
            'dest="${!#}"\n'
            'dest="${dest#*:}"\n'
            'if [ "${FAKE_RSYNC_FAIL:-0}" = "1" ]; then exit 23; fi\n'
            'mkdir -p "$dest"\n'
            'cp -a "$src"/. "$dest"/\n'
            'if [ "${FAKE_RSYNC_OMIT:-}" ]; then rm -f "$dest/$FAKE_RSYNC_OMIT"; fi\n',
            encoding="utf-8",
        )
        rsync.chmod(0o755)

    def _run(self, *args, extra_env=None):
        env = os.environ.copy()
        env.update(
            {
                "PATH": f"{self.bin}:{env['PATH']}",
                "SERVER": SERVER,
                "ZG_DOMAIN": "zonagris.pruebapublica.com",
                "ZG_REMOTE_ROOT": str(self.remote),
                "ZG_ALLOW_CUSTOM_REMOTE_ROOT": "1",
                "TMPDIR": str(self.tmp),
            }
        )
        if extra_env:
            env.update(extra_env)
        return subprocess.run(
            ["bash", "scripts/deploy_web.sh", *args],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

    def _releases(self):
        return sorted((self.remote / "releases").glob("*")) if (self.remote / "releases").exists() else []

    def test_first_deploy_success(self):
        result = self._run("--apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        current = self.remote / "current"
        self.assertTrue(current.is_symlink())
        self.assertTrue((current / "index.html").is_file())
        self.assertEqual(len(self._releases()), 1)

    def test_first_deploy_copy_failure_leaves_no_current(self):
        result = self._run("--apply", extra_env={"FAKE_RSYNC_FAIL": "1"})
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.remote / "current").exists())

    def test_first_deploy_validation_failure_leaves_no_current(self):
        result = self._run("--apply", extra_env={"FAKE_RSYNC_OMIT": "index.html"})
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.remote / "current").exists())

    def test_rollback_initial_removes_current_but_keeps_release(self):
        self.assertEqual(self._run("--apply").returncode, 0)
        release = self._releases()[0]
        result = self._run("--apply", "--rollback")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.remote / "current").exists())
        self.assertTrue(release.is_dir())

    def test_normal_rollback_uses_previous_release(self):
        self.assertEqual(self._run("--apply").returncode, 0)
        first = self._releases()[0]
        time.sleep(1)
        self.assertEqual(self._run("--apply").returncode, 0)
        second = self._releases()[1]
        self.assertNotEqual(first, second)
        result = self._run("--apply", "--rollback")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(Path(os.readlink(self.remote / "current")), first)

    def test_rejects_foreign_remote_root(self):
        result = self._run(
            "--apply",
            extra_env={
                "ZG_REMOTE_ROOT": str(self.tmp / "otro"),
                "ZG_ALLOW_CUSTOM_REMOTE_ROOT": "0",
            },
        )
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.tmp / "otro").exists())
