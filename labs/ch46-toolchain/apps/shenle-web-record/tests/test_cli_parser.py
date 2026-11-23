import pytest

from shenle_web_record.cli import build_parser, main


def test_record_with_url():
    p = build_parser()
    args = p.parse_args(["record", "https://example.com"])
    assert args.command == "record"
    assert args.url == "https://example.com"
    assert args.output == "."


def test_record_with_output():
    p = build_parser()
    args = p.parse_args(["record", "https://x.com", "-o", "/tmp/foo"])
    assert args.output == "/tmp/foo"


def test_record_without_url_exits(capsys):
    with pytest.raises(SystemExit):
        main(["record"])