# SPDX-License-Identifier: Apache-2.0

import importlib.metadata
import importlib.util
import json
import re
import shlex
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
NOTEBOOKS = (
    ROOT / "ai-for-quantum/01_compiling_unitaries_diffusion.ipynb",
    ROOT
    / "ai-for-quantum/solutions/01_compiling_unitaries_using_diffusion_models_Solutions.ipynb",
)
OPENCLIP_PIN = "open_clip_torch==3.3.0"
GENQC_PIN = "genQC==0.2.5"


class DiffusionDependenciesTest(unittest.TestCase):
    def test_ci_pins_compatible_openclip(self):
        install = re.search(
            r"(?m)^    - pip install --quiet --upgrade\n((?:        \S[^\n]*\n)+)",
            (ROOT / ".gitlab-ci.yml").read_text(),
        )
        self.assertIsNotNone(install)
        requirements = shlex.split(install.group(1))
        self.assertIn(GENQC_PIN, requirements)
        self.assertIn(OPENCLIP_PIN, requirements)

    def test_notebook_installers_repair_missing_or_incompatible_packages(self):
        cases = (
            ({"genQC": "0.2.5", "open_clip_torch": "3.3.0"}, False),
            ({"genQC": "0.2.5", "open_clip_torch": "4.2.1"}, True),
            ({"genQC": "0.2.5"}, True),
            ({"genQC": "0.2.4", "open_clip_torch": "3.3.0"}, True),
            ({}, True),
        )
        for path in NOTEBOOKS:
            notebook = json.loads(path.read_text())
            source = next(
                "".join(cell["source"])
                for cell in notebook["cells"]
                if cell["cell_type"] == "code"
                and "pip install" in "".join(cell["source"])
                and GENQC_PIN in "".join(cell["source"])
            )
            source = re.sub(
                r"(?m)^(\s*)!(.*)$",
                lambda match: match[1] + "get_ipython().system(" + repr(match[2]) + ")",
                source,
            )
            for versions, needs_install in cases:
                with self.subTest(notebook=path.name, versions=versions):
                    calls = []

                    def version(name):
                        if name not in versions:
                            raise importlib.metadata.PackageNotFoundError(name)
                        return versions[name]

                    with mock.patch(
                        "importlib.metadata.version", side_effect=version
                    ), mock.patch(
                        "importlib.util.find_spec",
                        return_value=SimpleNamespace() if "genQC" in versions else None,
                    ):
                        exec(
                            compile(source, str(path), "exec"),
                            {"get_ipython": lambda: SimpleNamespace(system=calls.append)},
                        )
                    self.assertEqual(len(calls), int(needs_install))
                    if needs_install:
                        self.assertIn(GENQC_PIN, calls[0])
                        self.assertIn(OPENCLIP_PIN, calls[0])
                        self.assertNotIn("--upgrade", calls[0])

    @unittest.skipUnless(
        all(
            importlib.util.find_spec(name) is not None
            for name in ("torch", "open_clip", "genQC")
        ),
        "Requires the diffusion notebook's ML dependencies",
    )
    def test_genqc_encoder_preserves_batch_and_sequence_dimensions(self):
        import open_clip
        import torch
        from genQC.models.frozen_open_clip import FrozenOpenCLIPEmbedder

        encoder = FrozenOpenCLIPEmbedder.__new__(FrozenOpenCLIPEmbedder)
        torch.nn.Module.__init__(encoder)
        encoder.model = open_clip.CLIP(
            embed_dim=32,
            vision_cfg={"layers": 1, "width": 64, "patch_size": 16, "image_size": 32},
            text_cfg={"context_length": 8, "vocab_size": 32, "width": 32, "heads": 2, "layers": 2},
        )
        encoder.layer_idx = 1
        encoder.device = "cpu"
        encoder.eval()
        tokens = torch.arange(16).reshape(2, 8)

        with torch.inference_mode():
            output = encoder(tokens)
            embedded = encoder.model.token_embedding(tokens)
            embedded = embedded + encoder.model.positional_embedding
            expected = encoder.model.transformer.resblocks[0](
                embedded, attn_mask=encoder.model.attn_mask
            )
            expected = encoder.model.ln_final(expected)

        self.assertEqual(tuple(output.shape), (2, 8, 32))
        self.assertTrue(torch.isfinite(output).all())
        torch.testing.assert_close(output, expected)


if __name__ == "__main__":
    unittest.main()
