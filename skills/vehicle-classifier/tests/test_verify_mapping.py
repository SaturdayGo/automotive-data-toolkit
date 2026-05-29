import pytest
import json
import tempfile
import os
from verify_mapping import MappingVerifier


def test_verify_valid_mapping():
    verifier = MappingVerifier()
    report = verifier.verify()
    assert report["total"] > 0
    assert report["passed"] > 0
    assert report["pass_rate"] > 0.9


def test_generate_report():
    verifier = MappingVerifier()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        report_path = f.name
    try:
        verifier.generate_report(report_path)
        assert os.path.exists(report_path)
        with open(report_path, "r") as f:
            content = f.read()
        assert "验收报告" in content
    finally:
        os.unlink(report_path)
