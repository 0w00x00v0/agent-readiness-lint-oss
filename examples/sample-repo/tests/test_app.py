"""Tests for the fictional widget-service."""

from src.app import greet


def test_greet():
    assert greet("widget") == "Hello, widget!"
