from pathlib import Path

p = Path("labs/ch39-perf-platform/test_perf_platform.py")
text = p.read_text(encoding="utf-8")
add = '''

def test_passed_never_goes_negative() -> None:
    report = Report(env="local")
    report.failures.extend(["a: 没有可用的执行器", "b: 没有可用的执行器", "c: 没有可用的执行器"])
    assert report.total == 0
    assert report.passed == 0


def test_load_config_missing_file_raises_config_error(tmp_path) -> None:
    with pytest.raises(ConfigError, match="读不到配置文件"):
        load_config(tmp_path / "nope.yaml")
'''
if "test_passed_never_goes_negative" not in text:
    p.write_text(text.rstrip("\n") + add, encoding="utf-8")
    print("added 2 tests")
else:
    print("already present")
