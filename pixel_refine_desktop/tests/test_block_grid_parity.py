"""Parity of block grid geometry after the port to the taichi library.

BlockGrid only computes geometry, so parity is a pure equality check over every
emitted block for representative shapes, block sizes and halos (including
partial edge blocks and asymmetric block sizes).
"""

import pytest

import taichi as ti

legacy_block = pytest.importorskip("taichi.block")


def _fields(spec):
    return (
        spec.index,
        spec.row,
        spec.column,
        spec.y0,
        spec.x0,
        spec.y1,
        spec.x1,
        spec.read_y0,
        spec.read_x0,
        spec.read_y1,
        spec.read_x1,
    )


CASES = [
    ((100, 250), 32, 0),
    ((100, 250), 32, 4),
    ((1080, 1920), 512, 16),
    ((1, 1), 512, 0),
    ((7, 13), (3, 5), 2),
]


@pytest.mark.parametrize(("shape", "size", "halo"), CASES)
def test_block_grid_matches_legacy(shape, size, halo):
    old = [_fields(b) for b in legacy_block.BlockGrid(shape, size=size, halo=halo)]
    new = [_fields(b) for b in ti.BlockGrid(shape, size=size, halo=halo)]
    assert new == old
    assert len(new) == len(legacy_block.BlockGrid(shape, size=size, halo=halo))


def test_normalize_block_size_matches():
    for value in (64, (3, 5), 1):
        assert ti.normalize_block_size(value) == legacy_block.normalize_block_size(value)
    for bad in (0, (0, 4), 2.5):
        with pytest.raises(Exception) as old_err:
            legacy_block.normalize_block_size(bad)
        with pytest.raises(Exception) as new_err:
            ti.normalize_block_size(bad)
        assert type(old_err.value).__name__ == type(new_err.value).__name__


def test_block_spec_helpers_match():
    old = next(iter(legacy_block.BlockGrid((9, 9), size=4)))
    new = next(iter(ti.BlockGrid((9, 9), size=4)))
    assert new.shape == old.shape
    assert new.read_shape == old.read_shape
    assert new.write_slice == old.write_slice
    assert new.core_slice == old.core_slice
    assert new.read_slice == old.read_slice
    assert new.make_id("src", "op", {"k": 1}) == old.make_id("src", "op", {"k": 1})
