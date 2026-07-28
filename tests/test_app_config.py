from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from omnisource import app_config


class AppConfigTests(unittest.TestCase):
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
