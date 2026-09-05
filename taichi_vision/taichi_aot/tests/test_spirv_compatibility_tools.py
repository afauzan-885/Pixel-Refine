from pathlib import Path

from taichi_vision import spirv_compatibility


def test_spirv_tools_accept_explicit_environment_paths(tmp_path, monkeypatch):
    validator = tmp_path / "spirv-val.exe"
    disassembler = tmp_path / "spirv-dis.exe"
    validator.touch()
    disassembler.touch()
    monkeypatch.setenv("SPIRV_VAL", str(validator))
    monkeypatch.setenv("PIXEL_REFINE_SPIRV_DIS", str(disassembler))

    assert Path(spirv_compatibility._tool("spirv-val")) == validator.resolve()
    assert Path(spirv_compatibility._tool("spirv-dis")) == disassembler.resolve()

