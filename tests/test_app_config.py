from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from omnisource import app_config, config


class AppConfigTests(unittest.TestCase):
    def test_installed_package_uses_bundled_tracks_and_writable_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            package_dir = root / "site-packages" / "omnisource"
            bundled_tracks = package_dir / "tracks"
            bundled_tracks.mkdir(parents=True)
            workspace = root / "workspace"
            workspace.mkdir()

            runtime_root, tracks_dir = config._resolve_runtime_paths(package_dir, cwd=workspace)

            self.assertEqual(runtime_root, workspace)
            self.assertEqual(tracks_dir, bundled_tracks)

    def test_source_checkout_prefers_repository_tracks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source_root = Path(tmp)
            package_dir = source_root / "omnisource"
            package_dir.mkdir()
            source_tracks = source_root / "tracks"
            source_tracks.mkdir()

            runtime_root, tracks_dir = config._resolve_runtime_paths(package_dir)

            self.assertEqual(runtime_root, source_root)
            self.assertEqual(tracks_dir, source_tracks)

    def test_active_tracks_reads_root_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "omnisource.yaml"
            path.write_text("active_tracks:\n  - ai-infra\n  - my-track\n", encoding="utf-8")

            self.assertEqual(app_config.active_tracks(path), ["ai-infra", "my-track"])

    def test_active_tracks_falls_back_when_config_is_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "omnisource.yaml"
            path.write_text("{}\n", encoding="utf-8")

            self.assertEqual(app_config.active_tracks(path), ["research/ai-algorithm", "builder/ai-infra"])

    def test_active_tracks_validates_track_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tracks = root / "tracks"
            tracks.mkdir()
            (tracks / "ai-infra.yaml").write_text("name: ai-infra\n", encoding="utf-8")
            config = root / "omnisource.yaml"
            config.write_text("active_tracks:\n  - ai-infra\n  - missing-track\n", encoding="utf-8")

            with patch.object(app_config, "track_path", side_effect=lambda name: tracks / f"{name}.yaml"):
                with self.assertRaisesRegex(ValueError, "missing-track"):
                    app_config.active_tracks(config, validate=True)


if __name__ == "__main__":
    unittest.main()
