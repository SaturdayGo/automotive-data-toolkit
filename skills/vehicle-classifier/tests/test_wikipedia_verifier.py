import pytest
import json
import os
from wikipedia_verifier import WikipediaVerifier


def test_verify_known_chassis_code():
    verifier = WikipediaVerifier()
    result = verifier.verify("宝马", "E90")
    assert result["verified"] == True
    assert "3系" in result["series"]


def test_verify_unknown_chassis_code():
    verifier = WikipediaVerifier()
    result = verifier.verify("宝马", "UNKNOWN123")
    assert result["verified"] == False


def test_get_cached_mapping():
    verifier = WikipediaVerifier()
    result = verifier.get_cached("宝马", "E60")
    assert result is not None
    assert result["series"] == "宝马 5系"
