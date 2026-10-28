"""Synthetic semantic tests for isolated dynamic INT64 candidate kernels."""

import numpy as np
import onnxruntime as ort
from pathlib import Path
import pytest
import taichi as ti

from taichi_vision.taichi_aot.neural_universal.kernels.integer64 import (
    nu_gather_elements_i64_indices_candidate,
    nu_gather_elements_i64_data_i64_indices_candidate,
    nu_gather_i64_indices_i64_candidate,
    nu_topk_last_i64_indices_candidate,
    nu_topk_axis_i64_indices_candidate,
    nu_gather_i64_candidate,
    nu_i64_binary_flat,
    nu_i64_binary_broadcast_candidate,
    nu_i64_binary_scalar_rhs,
    nu_i64_cmp_flat,
    nu_i64_cmp_broadcast_candidate,
    nu_where_i64_broadcast_candidate,
    nu_where_i64_flat,
)
from taichi_vision.taichi_aot.neural_universal.kernels.movement_i64 import (
    nu_concat2_i64_candidate,
    nu_copy_split_axis_i64_candidate,
    nu_slice_axis_i64_candidate,
    nu_transpose_general_i64_candidate,
    nu_nonzero_scatter_serial_i64_candidate,
    nu_nonzero_scatter_serial_i32_i64_candidate,
)
from taichi_vision.taichi_aot.neural_universal.kernels.movement import (
    nu_nonzero_count,
    nu_nonzero_scatter,
)
from taichi_vision.taichi_aot.neural_universal.kernels.norm_candidate import (
    nu_instance_norm_packet4_affine_candidate,
)
from taichi_vision.taichi_aot.neural_universal.kernels.elementwise import nu_cast_i32_i64


@pytest.fixture(scope="module", autouse=True)
def _init_taichi_cpu():
    ti.init(arch=ti.cpu, offline_cache=False)
    yield
    ti.reset()


def _ort_binary(op, a, b, **attrs):
    import onnx
    from onnx import helper, TensorProto

    a = np.asarray(a, dtype=np.int64)
    b = np.asarray(b, dtype=np.int64)
    out = helper.make_tensor_value_info("y", TensorProto.INT64, list(np.broadcast_shapes(a.shape, b.shape)))
    ins = [helper.make_tensor_value_info("a", TensorProto.INT64, list(a.shape)),
           helper.make_tensor_value_info("b", TensorProto.INT64, list(b.shape))]
    node = helper.make_node(op, ["a", "b"], ["y"], **attrs)
    graph = helper.make_graph([node], "int64_test", ins, [out])
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 17)])
    model.ir_version = 9
    session = ort.InferenceSession(model.SerializeToString(), providers=["CPUExecutionProvider"])
    return session.run(None, {"a": a, "b": b})[0]


@pytest.mark.parametrize("op,code", [("Add", 0), ("Sub", 1), ("Mul", 2)])
def test_i64_binary_wrap_matches_ort(op, code):
    info = np.iinfo(np.int64)
    a = np.array([info.max, info.min, -7, 7], np.int64)
    b = np.array([1, 1, 3, -3], np.int64)
    expected = _ort_binary(op, a, b)
    out = np.empty_like(a)
    status = np.zeros(1, np.int32)
    nu_i64_binary_flat(a, b, out, len(a), code, 0, status)
    assert status[0] == 0
    np.testing.assert_array_equal(out, expected)


@pytest.mark.parametrize("fmod", [0, 1])
def test_i64_mod_signed_semantics_and_scalar_rhs_match_ort(fmod):
    a = np.array([-7, -7, 7, 7, 0, -1], np.int64)
    b = np.array([3, -3, 3, -3, -2, 2], np.int64)
    expected = _ort_binary("Mod", a, b, fmod=fmod)
    out = np.empty_like(a)
    status = np.zeros(1, np.int32)
    nu_i64_binary_flat(a, b, out, len(a), 3, fmod, status)
    assert status[0] == 0
    np.testing.assert_array_equal(out, expected)
    scalar_out = np.empty_like(a)
    nu_i64_binary_scalar_rhs(a, b[0:1], scalar_out, len(a), 3, fmod, status)
    np.testing.assert_array_equal(scalar_out, _ort_binary("Mod", a, b[0:1], fmod=fmod))


def test_i64_div_truncates_toward_zero_matches_ort():
    info = np.iinfo(np.int64)
    a = np.array([-7, 7, info.max, -1], np.int64)
    b = np.array([3, -3, 2, 2], np.int64)
    expected = _ort_binary("Div", a, b)
    out, status = np.empty_like(a), np.zeros(1, np.int32)
    nu_i64_binary_flat(a, b, out, len(a), 4, 0, status)
    assert status[0] == 0
    np.testing.assert_array_equal(out, expected)


def test_i64_div_min_over_minus_one_fails_closed_without_undefined_quotient():
    info = np.iinfo(np.int64)
    a, b = np.array([info.min], np.int64), np.array([-1], np.int64)
    out, status = np.empty_like(a), np.zeros(1, np.int32)
    nu_i64_binary_flat(a, b, out, 1, 4, 0, status)
    assert status[0] != 0


def test_i64_broadcast_div_right_aligns_like_onnx_and_ort():
    a = np.arange(1, 7, dtype=np.int64).reshape(2, 3, 1)
    b = np.array([1, 2], np.int64)
    expected = _ort_binary("Div", a, b)
    out = np.empty(expected.size, np.int64)
    status = np.zeros(1, np.int32)
    out_shape = expected.shape
    from taichi_vision.taichi_aot.neural_universal.dtypes import broadcast_strides, pad_to, product
    kwargs = {f"o{i}": v for i, v in enumerate(pad_to(out_shape, 8))}
    kwargs.update({f"a{i}": v for i, v in enumerate(pad_to(broadcast_strides(a.shape, out_shape), 8, 0))})
    kwargs.update({f"b{i}": v for i, v in enumerate(pad_to(broadcast_strides(b.shape, out_shape), 8, 0))})
    nu_i64_binary_broadcast_candidate(
        a.ravel(), b, out, product(out_shape), 4, 0, status, **kwargs,
    )
    assert status[0] == 0
    np.testing.assert_array_equal(out.reshape(out_shape), expected)


def test_i64_div_zero_divisor_sets_explicit_error_status():
    a, b = np.array([1, -2], np.int64), np.array([0, 1], np.int64)
    out, status = np.empty_like(a), np.zeros(1, np.int32)
    nu_i64_binary_flat(a, b, out, 2, 4, 0, status)
    assert status[0] != 0


def test_i64_zero_divisor_sets_explicit_error_status():
    a, b = np.array([4, 9], np.int64), np.array([2, 0], np.int64)
    out, status = np.empty_like(a), np.zeros(1, np.int32)
    nu_i64_binary_flat(a, b, out, 2, 3, 0, status)
    assert status[0] != 0


@pytest.mark.parametrize("largest", [0, 1])
def test_topk_i64_indices_preserves_values_order_and_ort_ties(largest):
    import onnx
    from onnx import helper, TensorProto, numpy_helper
    from taichi_vision.taichi_aot.neural_universal.plan import Plan
    x = np.array([[3, 9, 9, -2, 5, 9], [1, 1, 7, 7, -1, 0]], np.float32)
    k = numpy_helper.from_array(np.array([3], np.int64), "k")
    graph = helper.make_graph(
        [helper.make_node("TopK", ["x", "k"], ["values", "indices"], axis=-1,
                          largest=largest, sorted=1)],
        "topk_i64_indices", [helper.make_tensor_value_info("x", TensorProto.FLOAT, [2, 6])],
        [helper.make_tensor_value_info("values", TensorProto.FLOAT, [2, 3]),
         helper.make_tensor_value_info("indices", TensorProto.INT64, [2, 3])],
        initializer=[k],
    )
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 17)])
    model.ir_version = 9
    plan = Plan.from_model_bytes(model.SerializeToString())
    assert plan.dtypes["indices"] == "i64"
    expected = ort.InferenceSession(model.SerializeToString(), providers=["CPUExecutionProvider"]).run(None, {"x": x})
    values, indices = np.empty((6,), np.float32), np.empty((6,), np.int64)
    taken = np.zeros(6, np.int32)
    nu_topk_last_i64_indices_candidate(x.ravel(), values, indices, taken, 2, 6, 3, largest)
    np.testing.assert_array_equal(values.reshape(2, 3), expected[0])
    np.testing.assert_array_equal(indices.reshape(2, 3), expected[1])


def test_topk_i64_indices_non_last_axis_matches_ort():
    import onnx
    from onnx import helper, TensorProto
    x = np.array([
        [[1, 7, 2], [9, 3, 8], [9, 5, 0], [-2, 4, 6], [5, 1, 3]],
        [[1, 0, 7], [1, 7, 2], [7, 7, 8], [0, 6, -1], [3, 2, 4]],
    ], np.float32)
    k = np.array([2], np.int64)
    graph = helper.make_graph(
        [helper.make_node("TopK", ["x", "k"], ["values", "indices"], axis=1,
                          largest=1, sorted=1)],
        "topk_axis", [helper.make_tensor_value_info("x", TensorProto.FLOAT, [2, 5, 3])],
        [helper.make_tensor_value_info("values", TensorProto.FLOAT, [2, 2, 3]),
         helper.make_tensor_value_info("indices", TensorProto.INT64, [2, 2, 3])],
        initializer=[onnx.numpy_helper.from_array(k, "k")],
    )
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 17)])
    model.ir_version = 9
    expected = ort.InferenceSession(model.SerializeToString(), providers=["CPUExecutionProvider"]).run(None, {"x": x})
    values, indices = np.empty(12, np.float32), np.empty(12, np.int64)
    taken = np.zeros(2 * 3 * 5, np.int32)
    nu_topk_axis_i64_indices_candidate(x.ravel(), values, indices, taken,
                                       outer_size=2, axis_dim=5, inner_size=3,
                                       k=2, largest=1)
    np.testing.assert_array_equal(values.reshape(2, 2, 3), expected[0])
    np.testing.assert_array_equal(indices.reshape(2, 2, 3), expected[1])


def test_i64_equal_broadcast_matches_ort_for_negative_and_large_values():
    import onnx
    from onnx import helper, TensorProto
    from taichi_vision.taichi_aot.neural_universal.dtypes import broadcast_strides, pad_to, product
    a = np.array([-7, 2**60, 9, -1, 4, 2**60], np.int64).reshape(2, 3, 1)
    b = np.array([2**60, -1], np.int64)
    graph = helper.make_graph(
        [helper.make_node("Equal", ["a", "b"], ["eq"])], "equal_i64_broadcast",
        [helper.make_tensor_value_info("a", TensorProto.INT64, [2, 3, 1]),
         helper.make_tensor_value_info("b", TensorProto.INT64, [2])],
        [helper.make_tensor_value_info("eq", TensorProto.BOOL, [2, 3, 2])],
    )
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 17)])
    model.ir_version = 9
    expected = ort.InferenceSession(model.SerializeToString(), providers=["CPUExecutionProvider"]).run(
        None, {"a": a, "b": b}
    )[0]
    shape = expected.shape
    out, status = np.empty(product(shape), np.int32), np.zeros(1, np.int32)
    kwargs = {f"o{i}": v for i, v in enumerate(pad_to(shape, 8))}
    kwargs.update({f"a{i}": v for i, v in enumerate(pad_to(broadcast_strides(a.shape, shape), 8, 0))})
    kwargs.update({f"b{i}": v for i, v in enumerate(pad_to(broadcast_strides(b.shape, shape), 8, 0))})
    nu_i64_cmp_broadcast_candidate(a.ravel(), b, out, out.size, 2, **kwargs)
    np.testing.assert_array_equal(out.reshape(shape).astype(bool), expected)


def test_i64_where_multi_axis_broadcast_matches_ort():
    cond = np.array([[[1]], [[0]]], np.int32)
    x = np.array([[[2**60], [-7], [9]]], np.int64)
    other = np.array([-1], np.int64)
    expected = np.where(cond != 0, x, other)
    shape = expected.shape
    from taichi_vision.taichi_aot.neural_universal.dtypes import broadcast_strides, pad_to, product
    out = np.empty(product(shape), np.int64)
    kwargs = {f"o{i}": v for i, v in enumerate(pad_to(shape, 8))}
    kwargs.update({f"c{i}": v for i, v in enumerate(pad_to(broadcast_strides(cond.shape, shape), 8, 0))})
    kwargs.update({f"x{i}": v for i, v in enumerate(pad_to(broadcast_strides(x.shape, shape), 8, 0))})
    kwargs.update({f"y{i}": v for i, v in enumerate(pad_to(broadcast_strides(other.shape, shape), 8, 0))})
    nu_where_i64_broadcast_candidate(cond.ravel(), x.ravel(), other, out, out.size, **kwargs)
    np.testing.assert_array_equal(out.reshape(shape), expected)


@pytest.mark.parametrize("op,code", [("Less", 0), ("Greater", 1)])
def test_i64_compare_and_where(op, code):
    a = np.array([-(2**60), 4, 9], np.int64)
    b = np.array([4, 9, 2], np.int64)
    cmp = np.empty(3, np.int32)
    nu_i64_cmp_flat(a, b, cmp, 3, code)
    import onnx
    from onnx import helper, TensorProto

    graph = helper.make_graph([helper.make_node(op, ["a", "b"], ["y"])], "cmp",
        [helper.make_tensor_value_info("a", TensorProto.INT64, [3]),
         helper.make_tensor_value_info("b", TensorProto.INT64, [3])],
        [helper.make_tensor_value_info("y", TensorProto.BOOL, [3])])
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 17)])
    model.ir_version = 9
    expected = ort.InferenceSession(model.SerializeToString(), providers=["CPUExecutionProvider"]).run(None, {"a": a, "b": b})[0]
    np.testing.assert_array_equal(cmp, expected.astype(np.int32))
    x, other, selected = a + 100, b + 200, np.empty(3, np.int64)
    nu_where_i64_flat(cmp, x, other, selected, 3)
    np.testing.assert_array_equal(selected, np.where(expected, x, other))


def test_i64_gather_and_float_gather_elements_with_i64_indices():
    data = np.array([10, 20, 30, 40], np.int64)
    indices = np.array([3, 0, -1], np.int32)
    out = np.empty(3, np.int64)
    nu_gather_i64_candidate(data, indices, out, 1, 3, 4, 1)
    np.testing.assert_array_equal(out, np.take(data, indices))

    fdata = np.array([1, 2, 3, 4, 5, 6], np.float32)
    findices = np.array([2, 0, 1], np.int64)
    fout = np.empty(3, np.float32)
    status = np.zeros(1, np.int32)
    nu_gather_elements_i64_indices_candidate(fdata, findices, fout, status, 1, 3, 3, 1)
    assert status[0] == 0
    np.testing.assert_array_equal(fout, np.take(fdata, findices))
    bad = np.array([3, 0, 1], np.int64)
    nu_gather_elements_i64_indices_candidate(fdata, bad, fout, status, 1, 3, 3, 1)
    assert status[0] != 0

    idata2 = np.array([[11, 22, 33], [44, 55, 66]], np.int64)
    iindices2 = np.array([[-1, 0], [1, -2]], np.int64)
    iout2 = np.empty((2, 2), np.int64)
    istatus2 = np.zeros(1, np.int32)
    nu_gather_elements_i64_data_i64_indices_candidate(
        idata2.ravel(), iindices2.ravel(), iout2.ravel(), istatus2,
        outer_size=2, axis_dim_data=3, axis_dim_idx=2, inner_size=1,
    )
    assert istatus2[0] == 0
    np.testing.assert_array_equal(iout2, np.take_along_axis(idata2, iindices2, axis=1))
    nu_gather_elements_i64_data_i64_indices_candidate(
        idata2.ravel(), np.array([3, 0, 1, 2], np.int64), iout2.ravel(), istatus2,
        outer_size=2, axis_dim_data=3, axis_dim_idx=2, inner_size=1,
    )
    assert istatus2[0] != 0

    idata = np.array([101, 202, 303, 404], np.int64)
    iindices = np.array([3, -2, 0], np.int64)
    iout = np.empty(3, np.int64)
    istatus = np.zeros(1, np.int32)
    nu_gather_i64_indices_i64_candidate(
        idata, iindices, iout, istatus, 1, 3, 4, 1,
    )
    assert istatus[0] == 0
    np.testing.assert_array_equal(iout, np.take(idata, iindices))


def test_i64_transpose_slice_concat_split_match_numpy_layout():
    x = np.arange(24, dtype=np.int64).reshape(2, 3, 4)
    transposed = np.empty(24, np.int64)
    # output shape [4, 2, 3], source strides for perm [2,0,1] are [1,12,4].
    nu_transpose_general_i64_candidate(
        x.ravel(), transposed, 24,
        4, 2, 3, 1, 1, 1, 1, 1,
        1, 12, 4, 0, 0, 0, 0, 0,
    )
    np.testing.assert_array_equal(transposed.reshape(4, 2, 3), x.transpose(2, 0, 1))

    src = np.arange(30, dtype=np.int64)
    sliced = np.empty(10, np.int64)
    nu_slice_axis_i64_candidate(src, sliced, 1, 30, 10, 1, 3, 1)
    np.testing.assert_array_equal(sliced, src[1:31:3])

    a, b = np.arange(6, dtype=np.int64), np.arange(10, 16, dtype=np.int64)
    joined = np.empty(12, np.int64)
    nu_concat2_i64_candidate(a, b, joined, 1, 6, 6, 1)
    np.testing.assert_array_equal(joined, np.concatenate([a, b]))
    left, right = np.empty(4, np.int64), np.empty(8, np.int64)
    nu_copy_split_axis_i64_candidate(joined, left, 1, 12, 4, 0, 1)
    nu_copy_split_axis_i64_candidate(joined, right, 1, 12, 8, 4, 1)
    np.testing.assert_array_equal(left, joined[:4])
    np.testing.assert_array_equal(right, joined[4:])


def test_nonzero_i64_materialization_preserves_row_major_order_and_shape():
    x = np.array([[0.0, 4.0, 0.0], [7.0, 0.0, 9.0]], np.float32).ravel()
    counter = np.zeros(1, np.int32)
    out32 = np.empty(12, np.int32)
    nu_nonzero_scatter(x, out32, counter, 6, 6, 2,
                       2, 3, 1, 1, 1, 1, 1, 1)
    count = int(counter[0])
    out64 = np.empty((2, 6), np.int64)
    nu_cast_i32_i64(out32, out64.ravel(), 12)
    actual = out64.reshape(2, 6)[:, :count]
    np.testing.assert_array_equal(actual, np.array([[0, 1, 1], [1, 0, 2]], np.int64))
    serial_counter = np.zeros(1, np.int32)
    serial_out32 = np.zeros(12, np.int64)
    nu_nonzero_scatter_serial_i64_candidate(
        x, serial_out32, serial_counter, 6, 6, 2,
        1, 1, 1, 1, 1, 1, 2, 3,
    )
    assert int(serial_counter[0]) == 3
    np.testing.assert_array_equal(serial_out32.reshape(2, 6)[:, :3],
                                  out32.reshape(2, 6)[:, :3])


def test_nonzero_i32_mask_serial_i64_matches_ort_row_major():
    import onnx
    from onnx import helper, TensorProto
    mask = np.array([[0, -2, 0], [1, 0, 5]], np.int32)
    graph = helper.make_graph(
        [helper.make_node("NonZero", ["mask"], ["coords"])], "nonzero_i32",
        [helper.make_tensor_value_info("mask", TensorProto.INT32, [2, 3])],
        [helper.make_tensor_value_info("coords", TensorProto.INT64, [2, None])],
    )
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 17)])
    model.ir_version = 9
    expected = ort.InferenceSession(model.SerializeToString(), providers=["CPUExecutionProvider"]).run(
        None, {"mask": mask}
    )[0]
    out, counter = np.zeros(12, np.int64), np.zeros(1, np.int32)
    nu_nonzero_scatter_serial_i32_i64_candidate(
        mask.ravel(), out, counter, 6, 6, 2,
        1, 1, 1, 1, 1, 1, 2, 3,
    )
    assert int(counter[0]) == expected.shape[1] == 3
    np.testing.assert_array_equal(out.reshape(2, 6)[:, :3], expected)


def test_candidate_pool_aot_runtime_i64_add_mod_matches_ort():
    import onnx
    from onnx import helper, TensorProto
    from taichi_vision.taichi_aot.neural_universal.runtime import UniversalSession

    inputs = [helper.make_tensor_value_info("a", TensorProto.INT64, [4]),
              helper.make_tensor_value_info("b", TensorProto.INT64, [4])]
    outputs = [helper.make_tensor_value_info("sum", TensorProto.INT64, [4]),
               helper.make_tensor_value_info("rem", TensorProto.INT64, [4])]
    graph = helper.make_graph([
        helper.make_node("Add", ["a", "b"], ["sum"]),
        helper.make_node("Mod", ["a", "b"], ["rem"], fmod=1),
    ], "candidate_runtime", inputs, outputs)
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 17)])
    model.ir_version = 9
    root = Path(__file__).resolve().parents[3]
    pool = root / "taichi_vision/taichi_aot/neural_universal/models/int64_cpu_candidate_v2"
    a = np.array([7, -7, 2**62, -2**62], np.int64)
    b = np.array([3, -3, 2, -2], np.int64)
    feed = {"a": a, "b": b}
    expected = ort.InferenceSession(model.SerializeToString(), providers=["CPUExecutionProvider"]).run(None, feed)
    with UniversalSession(model.SerializeToString(), backend="cpu", pool_dir=pool) as session:
        assert session.int64_candidate
        actual = session.run(None, feed)
        from taichi_vision.taichi_aot.neural_universal.errors import UnsupportedStepError
        with pytest.raises(UnsupportedStepError, match="zero divisor"):
            session.run(None, {"a": a, "b": np.array([3, -3, 0, 2], np.int64)})
    for got, want in zip(actual, expected):
        np.testing.assert_array_equal(got, want)


def test_candidate_pool_aot_runtime_i64_div_matches_ort_and_guards_invalid_cases():
    import onnx
    from onnx import helper, TensorProto
    from taichi_vision.taichi_aot.neural_universal.runtime import UniversalSession
    from taichi_vision.taichi_aot.neural_universal.errors import UnsupportedStepError

    inputs = [helper.make_tensor_value_info("a", TensorProto.INT64, [4]),
              helper.make_tensor_value_info("b", TensorProto.INT64, [4])]
    outputs = [helper.make_tensor_value_info("q", TensorProto.INT64, [4])]
    graph = helper.make_graph([helper.make_node("Div", ["a", "b"], ["q"])],
                              "int64_div_candidate", inputs, outputs)
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 17)])
    model.ir_version = 9
    root = Path(__file__).resolve().parents[3]
    pool = root / "taichi_vision/taichi_aot/neural_universal/models/int64_cpu_candidate_v6"
    a = np.array([-7, 7, np.iinfo(np.int64).max, -1], np.int64)
    b = np.array([3, -3, 2, 2], np.int64)
    expected = ort.InferenceSession(model.SerializeToString(), providers=["CPUExecutionProvider"]).run(
        None, {"a": a, "b": b}
    )
    with UniversalSession(model.SerializeToString(), backend="cpu", pool_dir=pool) as session:
        actual = session.run(None, {"a": a, "b": b})
        np.testing.assert_array_equal(actual[0], expected[0])
        with pytest.raises(UnsupportedStepError, match="division by zero"):
            session.run(None, {"a": a, "b": np.array([3, -3, 0, 2], np.int64)})
        with pytest.raises(UnsupportedStepError, match="signed INT64 division overflow"):
            session.run(None, {
                "a": np.array([np.iinfo(np.int64).min, 1, 2, 3], np.int64),
                "b": np.array([-1, 1, 1, 1], np.int64),
            })


def test_candidate_pool_aot_runtime_i64_broadcast_div_matches_ort():
    import onnx
    from onnx import helper, TensorProto
    from taichi_vision.taichi_aot.neural_universal.runtime import UniversalSession

    inputs = [helper.make_tensor_value_info("a", TensorProto.INT64, [2, 3, 1]),
              helper.make_tensor_value_info("b", TensorProto.INT64, [2])]
    outputs = [helper.make_tensor_value_info("q", TensorProto.INT64, [2, 3, 2])]
    graph = helper.make_graph([helper.make_node("Div", ["a", "b"], ["q"])],
                              "int64_div_broadcast_candidate", inputs, outputs)
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 17)])
    model.ir_version = 9
    root = Path(__file__).resolve().parents[3]
    pool = root / "taichi_vision/taichi_aot/neural_universal/models/int64_cpu_candidate_v7"
    feeds = {"a": np.arange(1, 7, dtype=np.int64).reshape(2, 3, 1),
             "b": np.array([1, 2], np.int64)}
    expected = ort.InferenceSession(model.SerializeToString(), providers=["CPUExecutionProvider"]).run(None, feeds)
    with UniversalSession(model.SerializeToString(), backend="cpu", pool_dir=pool) as session:
        actual = session.run(None, feeds)
    np.testing.assert_array_equal(actual[0], expected[0])


def test_candidate_pool_aot_topk_i64_indices_matches_ort():
    import onnx
    from onnx import helper, TensorProto, numpy_helper
    from taichi_vision.taichi_aot.neural_universal.runtime import UniversalSession
    x = np.array([
        [[1, 7, 2], [9, 3, 8], [9, 5, 0], [-2, 4, 6], [5, 1, 3]],
        [[1, 0, 7], [1, 7, 2], [7, 7, 8], [0, 6, -1], [3, 2, 4]],
    ], np.float32)
    k = numpy_helper.from_array(np.array([3], np.int64), "k")
    graph = helper.make_graph(
        [helper.make_node("TopK", ["x", "k"], ["values", "indices"], axis=1,
                          largest=1, sorted=1)],
        "topk_i64_candidate", [helper.make_tensor_value_info("x", TensorProto.FLOAT, [2, 5, 3])],
        [helper.make_tensor_value_info("values", TensorProto.FLOAT, [2, 2, 3]),
         helper.make_tensor_value_info("indices", TensorProto.INT64, [2, 2, 3])],
        initializer=[k],
    )
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 17)])
    model.ir_version = 9
    feeds = {"x": x}
    expected = ort.InferenceSession(model.SerializeToString(), providers=["CPUExecutionProvider"]).run(None, feeds)
    pool = Path(__file__).resolve().parents[3] / "taichi_vision/taichi_aot/neural_universal/models/int64_cpu_candidate_v10"
    with UniversalSession(model.SerializeToString(), backend="cpu", pool_dir=pool) as session:
        actual = session.run(None, feeds)
    for got, want in zip(actual, expected):
        np.testing.assert_array_equal(got, want)


def test_candidate_pool_aot_i64_equal_broadcast_matches_ort():
    import onnx
    from onnx import helper, TensorProto
    from taichi_vision.taichi_aot.neural_universal.runtime import UniversalSession
    a = np.array([-7, 2**60, 9, -1, 4, 2**60], np.int64).reshape(2, 3, 1)
    b = np.array([2**60, -1], np.int64)
    graph = helper.make_graph(
        [helper.make_node("Equal", ["a", "b"], ["eq"])], "equal_i64_candidate",
        [helper.make_tensor_value_info("a", TensorProto.INT64, [2, 3, 1]),
         helper.make_tensor_value_info("b", TensorProto.INT64, [2])],
        [helper.make_tensor_value_info("eq", TensorProto.BOOL, [2, 3, 2])],
    )
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 17)])
    model.ir_version = 9
    feeds = {"a": a, "b": b}
    expected = ort.InferenceSession(model.SerializeToString(), providers=["CPUExecutionProvider"]).run(None, feeds)
    pool = Path(__file__).resolve().parents[3] / "taichi_vision/taichi_aot/neural_universal/models/int64_cpu_candidate_v12"
    with UniversalSession(model.SerializeToString(), backend="cpu", pool_dir=pool) as session:
        actual = session.run(None, feeds)
    np.testing.assert_array_equal(actual[0], expected[0])


def test_candidate_pool_aot_nonzero_i32_mask_matches_ort():
    import onnx
    from onnx import helper, TensorProto
    from taichi_vision.taichi_aot.neural_universal.runtime import UniversalSession
    mask = np.array([[0, -2, 0], [1, 0, 5]], np.int32)
    graph = helper.make_graph(
        [helper.make_node("NonZero", ["mask"], ["coords"])], "nonzero_i32_candidate",
        [helper.make_tensor_value_info("mask", TensorProto.INT32, [2, 3])],
        [helper.make_tensor_value_info("coords", TensorProto.INT64, [2, None])],
    )
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 17)])
    model.ir_version = 9
    feeds = {"mask": mask}
    expected = ort.InferenceSession(model.SerializeToString(), providers=["CPUExecutionProvider"]).run(None, feeds)
    pool = Path(__file__).resolve().parents[3] / "taichi_vision/taichi_aot/neural_universal/models/int64_cpu_candidate_v13"
    with UniversalSession(model.SerializeToString(), backend="cpu", pool_dir=pool) as session:
        actual = session.run(None, feeds)
    np.testing.assert_array_equal(actual[0], expected[0])


def test_candidate_pool_aot_i64_where_multi_axis_broadcast_matches_ort():
    import onnx
    from onnx import helper, TensorProto
    from taichi_vision.taichi_aot.neural_universal.runtime import UniversalSession
    inputs = [helper.make_tensor_value_info("cond", TensorProto.BOOL, [2, 1, 1]),
              helper.make_tensor_value_info("x", TensorProto.INT64, [1, 3, 1]),
              helper.make_tensor_value_info("other", TensorProto.INT64, [1])]
    output = helper.make_tensor_value_info("y", TensorProto.INT64, [2, 3, 1])
    graph = helper.make_graph([helper.make_node("Where", ["cond", "x", "other"], ["y"])],
                              "where_i64_candidate", inputs, [output])
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 17)])
    model.ir_version = 9
    feeds = {"cond": np.array([[[True]], [[False]]], np.bool_),
             "x": np.array([[[2**60], [-7], [9]]], np.int64),
             "other": np.array([-1], np.int64)}
    expected = ort.InferenceSession(model.SerializeToString(), providers=["CPUExecutionProvider"]).run(None, feeds)
    pool = Path(__file__).resolve().parents[3] / "taichi_vision/taichi_aot/neural_universal/models/int64_cpu_candidate_v15"
    with UniversalSession(model.SerializeToString(), backend="cpu", pool_dir=pool) as session:
        actual = session.run(None, feeds)
    np.testing.assert_array_equal(actual[0], expected[0])


@pytest.mark.parametrize("auto_pad,kernel_hw,strides,dilations", [
    ("SAME_UPPER", (4, 3), (2, 2), (1, 1)),
    ("SAME_LOWER", (4, 3), (2, 2), (1, 1)),
    ("SAME_UPPER", (5, 5), (1, 1), (1, 1)),
])
def test_candidate_conv_same_auto_pad_matches_ort_cpu(
    auto_pad, kernel_hw, strides, dilations,
):
    import onnx
    from onnx import helper, TensorProto, numpy_helper
    from taichi_vision.taichi_aot.neural_universal.runtime import UniversalSession
    rng = np.random.default_rng(20261026)
    x = rng.normal(0, 0.1, (1, 2, 7, 8)).astype(np.float32)
    weight = rng.normal(0, 0.1, (3, 2, kernel_hw[0], kernel_hw[1])).astype(np.float32)
    bias = rng.normal(0, 0.1, (3,)).astype(np.float32)
    initializers = [numpy_helper.from_array(weight, "w"), numpy_helper.from_array(bias, "b")]
    out_h, out_w = (7 + strides[0] - 1) // strides[0], (8 + strides[1] - 1) // strides[1]
    node = helper.make_node("Conv", ["x", "w", "b"], ["y"], auto_pad=auto_pad,
                            strides=list(strides), dilations=list(dilations),
                            kernel_shape=list(kernel_hw))
    graph = helper.make_graph(
        [node], "conv_same_pad",
        [helper.make_tensor_value_info("x", TensorProto.FLOAT, [1, 2, 7, 8])],
        [helper.make_tensor_value_info("y", TensorProto.FLOAT, [1, 3, out_h, out_w])],
        initializer=initializers,
    )
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 17)])
    model.ir_version = 9
    expected = ort.InferenceSession(model.SerializeToString(), providers=["CPUExecutionProvider"]).run(
        None, {"x": x}
    )[0]
    pool = Path(__file__).resolve().parents[3] / "taichi_vision/taichi_aot/neural_universal/models/int64_cpu_candidate_v13"
    with UniversalSession(model.SerializeToString(), backend="cpu", pool_dir=pool) as session:
        actual = session.run(None, {"x": x})[0]
    assert actual.shape == expected.shape == (1, 3, out_h, out_w)
    np.testing.assert_allclose(actual, expected, atol=1e-6, rtol=0)


def test_candidate_average_pool2x2_pair_matches_ort_cpu():
    import onnx
    from onnx import helper, TensorProto
    from taichi_vision.taichi_aot.neural_universal.runtime import UniversalSession
    rng = np.random.default_rng(20261026)
    x = rng.normal(0, 0.1, (1, 2, 7, 8)).astype(np.float32)
    graph = helper.make_graph(
        [helper.make_node("AveragePool", ["x"], ["y"], kernel_shape=[2, 2],
                          strides=[2, 2], pads=[0, 0, 0, 0], count_include_pad=1)],
        "avgpool_pair_candidate",
        [helper.make_tensor_value_info("x", TensorProto.FLOAT, [1, 2, 7, 8])],
        [helper.make_tensor_value_info("y", TensorProto.FLOAT, [1, 2, 3, 4])],
    )
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 17)])
    model.ir_version = 9
    feeds = {"x": x}
    expected = ort.InferenceSession(model.SerializeToString(), providers=["CPUExecutionProvider"]).run(None, feeds)[0]
    pool = Path(__file__).resolve().parents[3] / "taichi_vision/taichi_aot/neural_universal/models/int64_cpu_candidate_v14"
    with UniversalSession(model.SerializeToString(), backend="cpu", pool_dir=pool) as session:
        actual = session.run(None, feeds)[0]
    np.testing.assert_allclose(actual, expected, atol=1e-6, rtol=0)


def test_candidate_pool_aot_i64_movement_paths_match_ort():
    import onnx
    from onnx import helper, TensorProto, numpy_helper
    from taichi_vision.taichi_aot.neural_universal.runtime import UniversalSession

    x_info = helper.make_tensor_value_info("x", TensorProto.INT64, [2, 3])
    idx_info = helper.make_tensor_value_info("idx", TensorProto.INT64, [2])
    f_info = helper.make_tensor_value_info("f", TensorProto.FLOAT, [2, 3])
    eidx_info = helper.make_tensor_value_info("eidx", TensorProto.INT64, [2, 2])
    badidx_info = helper.make_tensor_value_info("badidx", TensorProto.INT64, [2, 2])
    starts = numpy_helper.from_array(np.array([0, 1], np.int64), "starts")
    ends = numpy_helper.from_array(np.array([2, 3], np.int64), "ends")
    axes = numpy_helper.from_array(np.array([0, 1], np.int64), "axes")
    steps = numpy_helper.from_array(np.array([1, 1], np.int64), "steps")
    expand_shape = numpy_helper.from_array(np.array([2, 2, 3], np.int64), "expand_shape")
    split_sizes = numpy_helper.from_array(np.array([3, 3], np.int64), "split_sizes")
    nodes = [
        helper.make_node("Gather", ["x", "idx"], ["gather"], axis=0),
        helper.make_node("GatherElements", ["f", "eidx"], ["gather_elements"], axis=1),
        helper.make_node("GatherElements", ["x", "badidx"], ["gather_elements_i64"], axis=1),
        helper.make_node("Transpose", ["x"], ["transpose"], perm=[1, 0]),
        helper.make_node("Slice", ["x", "starts", "ends", "axes", "steps"], ["slice"]),
        helper.make_node("Concat", ["x", "x"], ["concat"], axis=1),
        helper.make_node("Split", ["concat", "split_sizes"], ["split0", "split1"], axis=1),
        helper.make_node("Expand", ["x", "expand_shape"], ["expand"]),
        helper.make_node("NonZero", ["f"], ["nonzero"]),
    ]
    outputs = [
        helper.make_tensor_value_info("gather", TensorProto.INT64, [2, 3]),
        helper.make_tensor_value_info("gather_elements", TensorProto.FLOAT, [2, 2]),
        helper.make_tensor_value_info("gather_elements_i64", TensorProto.INT64, [2, 2]),
        helper.make_tensor_value_info("transpose", TensorProto.INT64, [3, 2]),
        helper.make_tensor_value_info("slice", TensorProto.INT64, [2, 2]),
        helper.make_tensor_value_info("concat", TensorProto.INT64, [2, 6]),
        helper.make_tensor_value_info("split0", TensorProto.INT64, [2, 3]),
        helper.make_tensor_value_info("split1", TensorProto.INT64, [2, 3]),
        helper.make_tensor_value_info("expand", TensorProto.INT64, [2, 2, 3]),
        helper.make_tensor_value_info("nonzero", TensorProto.INT64, [2, None]),
    ]
    graph = helper.make_graph(nodes, "candidate_movement", [x_info, idx_info, f_info, eidx_info, badidx_info],
                              outputs, initializer=[starts, ends, axes, steps, expand_shape, split_sizes])
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 17)])
    model.ir_version = 9
    x = np.array([[10, 20, 30], [40, 50, 60]], np.int64)
    idx = np.array([1, 0], np.int64)
    f = np.array([[0, 1, 0], [3, 0, 5]], np.float32)
    eidx = np.array([[2, 0], [1, 2]], np.int64)
    feed = {"x": x, "idx": idx, "f": f, "eidx": eidx, "badidx": eidx}
    expected = ort.InferenceSession(model.SerializeToString(), providers=["CPUExecutionProvider"]).run(None, feed)
    pool = Path(__file__).resolve().parents[3] / "taichi_vision/taichi_aot/neural_universal/models/int64_cpu_candidate_v11"
    with UniversalSession(model.SerializeToString(), backend="cpu", pool_dir=pool) as session:
        assert session.int64_candidate
        calls = []
        scatter_raw = []
        scatter_args = []
        original = session.module.run
        def traced(name, *a, **kw):
            calls.append(name)
            result = original(name, *a, **kw)
            if name == "nu_nonzero_scatter_serial_i64_candidate":
                session.engine.sync()
                scatter_raw.append((kw["out"].to_numpy().copy(), kw["counter"].to_numpy().copy()))
                scatter_args.append(dict(kw))
            return result
        session.module.run = traced
        # Probe the AOT graph directly with explicit, distinct I64 output and
        # I32 counter buffers before relying on runtime finalization.
        raw_x = session.upload("__test_nonzero_x", np.ascontiguousarray(f.ravel()))
        raw_out = session.engine.allocate((12,), dtype=np.int64, is_vector=False)
        raw_counter = session.engine.allocate((1,), dtype=np.int32, is_vector=False)
        session.module.run("nu_fill_i32", y=raw_counter, n=1, value=0)
        session.module.run(
            "nu_nonzero_scatter_serial_i64_candidate", x=raw_x, out=raw_out,
            counter=raw_counter, total=6, capacity=6, rank=2,
            d0=1, d1=1, d2=1, d3=1, d4=1, d5=1, d6=2, d7=3,
        )
        session.engine.sync()
        direct_raw = raw_out.to_numpy().copy()
        direct_count = int(raw_counter.to_numpy().ravel()[0])
        assert direct_count == 3
        np.testing.assert_array_equal(
            direct_raw.reshape(2, 6)[:, :direct_count],
            np.array([[0, 1, 1], [1, 0, 2]], np.int64),
        )
        before_runtime_calls = len(calls)
        actual = session.run(None, feed)
        assert "nu_nonzero_scatter_serial_i64_candidate" in calls[before_runtime_calls:]
        runtime_raw = session.buffers["nonzero"].to_numpy().copy()
        runtime_count = int(session._nz["nonzero"][0].to_numpy().ravel()[0])
        assert runtime_count == 3
        assert scatter_args, f"serial graph not observed; calls={calls}"
        runtime_args = scatter_args[-1]
        replay_counter = session.engine.allocate((1,), dtype=np.int32, is_vector=False)
        session.module.run("nu_fill_i32", y=replay_counter, n=1, value=0)
        replay_args = dict(runtime_args)
        replay_args["counter"] = replay_counter
        session.module.run("nu_nonzero_scatter_serial_i64_candidate", **replay_args)
        session.engine.sync()
        replay_raw = runtime_args["out"].to_numpy().copy()
        runtime_meta = {
            key: ((getattr(value, "handle", None), getattr(value, "dtype", None),
                  getattr(value, "shape", None)) if hasattr(value, "to_numpy") else value)
            for key, value in runtime_args.items()
        }
        runtime_x = runtime_args["x"].to_numpy().copy()
        runtime_counter_value = runtime_args["counter"].to_numpy().copy()
        np.testing.assert_array_equal(
            runtime_raw.reshape(2, 6)[:, :runtime_count],
            np.array([[0, 1, 1], [1, 0, 2]], np.int64),
                err_msg=(f"runtime AOT scatter raw={runtime_raw}; replay_raw={replay_raw}; "
                         f"direct_raw={direct_raw}; meta={runtime_meta}; x={runtime_x}; "
                         f"counter={runtime_counter_value}"),
        )
        from taichi_vision.taichi_aot.neural_universal.errors import UnsupportedStepError
        bad_feed = dict(feed)
        bad_feed["badidx"] = np.array([[3, 0], [1, 2]], np.int64)
        with pytest.raises(UnsupportedStepError, match="out-of-range index"):
            session.run(None, bad_feed)
        assert "nu_nonzero_scatter_serial_i64_candidate" in session.pool_graph_names
        assert scatter_raw and int(scatter_raw[0][1][0]) == 3
        assert np.count_nonzero(scatter_raw[0][0]) > 0, (
            f"AOT scatter output stayed zero; output={scatter_raw[0][0]}, counter={scatter_raw[0][1]}"
        )
    assert {"nu_gather_i64_indices_i64_candidate", "nu_gather_elements_i64_indices_candidate",
            "nu_gather_elements_i64_data_i64_indices_candidate",
            "nu_transpose_general_i64_candidate", "nu_slice_axis_i64_candidate",
            "nu_concat2_i64_candidate", "nu_copy_split_axis_i64_candidate",
            "nu_nonzero_scatter_serial_i64_candidate"}.issubset(set(calls))
    for output_name, got, want in zip(
        ["gather", "gather_elements", "gather_elements_i64", "transpose", "slice", "concat",
         "split0", "split1", "expand", "nonzero"], actual, expected,
    ):
        np.testing.assert_array_equal(got, want, err_msg=(
            f"AOT output {output_name}; direct_raw={direct_raw}; count={direct_count}"
            if output_name == "nonzero" else f"AOT output {output_name}"
        ))


def _assert_full_model_candidate_parity(model_path, feeds, *, label):
    from taichi_vision.taichi_aot.neural_universal.runtime import UniversalSession

    model_bytes = Path(model_path).read_bytes()
    oracle = ort.InferenceSession(model_bytes, providers=["CPUExecutionProvider"])
    expected = oracle.run(None, feeds)
    pool = Path(__file__).resolve().parents[3] / "taichi_vision/taichi_aot/neural_universal/models/int64_cpu_candidate_v15"
    with UniversalSession(model_bytes, backend="cpu", pool_dir=pool) as session:
        assert session.int64_candidate
        actual = session.run(None, feeds)
    assert len(actual) == len(expected), f"{label}: output count mismatch"
    max_abs = 0.0
    rmse_values = []
    for index, (got, want) in enumerate(zip(actual, expected)):
        got, want = np.asarray(got), np.asarray(want)
        assert got.shape == want.shape, f"{label} output {index} shape {got.shape} != {want.shape}"
        if got.dtype.kind in "iu" or want.dtype.kind in "iu":
            np.testing.assert_array_equal(got, want, err_msg=f"{label} discrete output {index}")
        else:
            delta = np.abs(got.astype(np.float64) - want.astype(np.float64))
            max_abs = max(max_abs, float(delta.max(initial=0.0)))
            rmse_values.append(float(np.sqrt(np.mean(delta * delta))))
            assert np.isfinite(got).all() == np.isfinite(want).all(), f"{label} finite mask mismatch"
    assert max_abs <= 1e-6, f"{label} max_abs={max_abs}, rmse={rmse_values}"
    print(f"{label} CPU candidate vs ORT: max_abs={max_abs:.9g}, rmse={rmse_values}")


def test_lightglue_full_cpu_int64_candidate_matches_ort():
    root = Path(__file__).resolve().parents[3]
    rng = np.random.default_rng(20261026)
    feeds = {"images": rng.random((2, 3, 512, 512), dtype=np.float32)}
    _assert_full_model_candidate_parity(
        root / "database/Learning_Model/disk_lightglue_pipeline.ort.onnx",
        feeds, label="LightGlue [2,3,512,512] FP32 (pair batch)",
    )


def test_raft_full_cpu_int64_candidate_matches_ort():
    root = Path(__file__).resolve().parents[3]
    rng = np.random.default_rng(20261026)
    feeds = {
        "0": rng.random((1, 3, 360, 480), dtype=np.float32),
        "1": rng.random((1, 3, 360, 480), dtype=np.float32),
    }
    _assert_full_model_candidate_parity(
        root / "database/Learning_Model/optical_flow_estimation_raft_2023aug.onnx",
        feeds, label="RAFT [1,3,360,480] FP32",
    )


def test_lightglue_extractor_topk_integer_prefix_matches_ort():
    import copy
    import onnx
    from taichi_vision.taichi_aot.neural_universal.runtime import UniversalSession

    root = Path(__file__).resolve().parents[3]
    original = onnx.load(str(root / "database/Learning_Model/disk_lightglue_pipeline.ort.onnx"))
    inferred = onnx.shape_inference.infer_shapes(original)
    targets = [
        "/extractor/unet/path_down.1/path_down.1.0/AveragePool_output_0",
        "/extractor/unet/path_down.1/path_down.1.1/path_down.1.1.0/InstanceNormalization_output_0",
        "/extractor/unet/path_down.1/path_down.1.1/path_down.1.1.1/PRelu_output_0",
        "/extractor/unet/path_down.1/path_down.1.1/path_down.1.1.3/Conv_output_0",
    ]
    info = {value.name: value for value in list(inferred.graph.value_info) + list(inferred.graph.output)}
    diagnostic = copy.deepcopy(inferred)
    for name in targets:
        diagnostic.graph.output.append(info[name])
    rng = np.random.default_rng(20261026)
    feeds = {"images": rng.random((2, 3, 512, 512), dtype=np.float32)}
    expected = ort.InferenceSession(diagnostic.SerializeToString(), providers=["CPUExecutionProvider"]).run(
        targets, feeds
    )
    pool = root / "taichi_vision/taichi_aot/neural_universal/models/int64_cpu_candidate_v14"
    with UniversalSession(original.SerializeToString(), backend="cpu", pool_dir=pool) as session:
        actual = session.run(targets, feeds, step_limit=19)
    for name, got, want in zip(targets, actual, expected):
        got, want = np.asarray(got), np.asarray(want)
        if got.dtype.kind in "iu" or want.dtype.kind in "iu":
            np.testing.assert_array_equal(got, want, err_msg=f"LightGlue prefix {name}")
        else:
            np.testing.assert_allclose(got, want, atol=1e-6, rtol=0, err_msg=f"LightGlue prefix {name}")


def test_lightglue_first_same_padded_conv_matches_ort():
    import copy
    import onnx
    from taichi_vision.taichi_aot.neural_universal.runtime import UniversalSession
    root = Path(__file__).resolve().parents[3]
    original = onnx.load(str(root / "database/Learning_Model/disk_lightglue_pipeline.ort.onnx"))
    inferred = onnx.shape_inference.infer_shapes(original)
    target = "/extractor/unet/path_down.0/path_down.0.1/path_down.0.1.3/Conv_output_0"
    info = {value.name: value for value in list(inferred.graph.value_info) + list(inferred.graph.output)}
    diagnostic = copy.deepcopy(inferred)
    diagnostic.graph.output.append(info[target])
    rng = np.random.default_rng(20261026)
    feeds = {"images": rng.random((2, 3, 512, 512), dtype=np.float32)}
    expected = ort.InferenceSession(diagnostic.SerializeToString(), providers=["CPUExecutionProvider"]).run(
        [target], feeds
    )[0]
    pool = root / "taichi_vision/taichi_aot/neural_universal/models/int64_cpu_candidate_v13"
    with UniversalSession(original.SerializeToString(), backend="cpu", pool_dir=pool) as session:
        actual = session.run([target], feeds, step_limit=13)[0]
    assert actual.shape == expected.shape == (2, 16, 512, 512)
    delta = np.abs(actual.astype(np.float64) - expected.astype(np.float64))
    max_abs = float(delta.max(initial=0.0))
    print(f"LightGlue node12 SAME Conv max_abs={max_abs:.9g}, rmse={np.sqrt(np.mean(delta*delta)):.9g}")
    assert max_abs <= 1e-6


def test_lightglue_avgpool_actual_conv_input_order_diagnostic():
    """Compare ONNX AveragePool reduction orders on the real node12 output."""
    import copy
    import onnx
    from taichi_vision.taichi_aot.neural_universal.runtime import UniversalSession
    root = Path(__file__).resolve().parents[3]
    original = onnx.load(str(root / "database/Learning_Model/disk_lightglue_pipeline.ort.onnx"))
    inferred = onnx.shape_inference.infer_shapes(original)
    conv_name = "/extractor/unet/path_down.0/path_down.0.1/path_down.0.1.3/Conv_output_0"
    pool_name = "/extractor/unet/path_down.1/path_down.1.0/AveragePool_output_0"
    info = {value.name: value for value in list(inferred.graph.value_info) + list(inferred.graph.output)}
    diagnostic = copy.deepcopy(inferred)
    diagnostic.graph.output.extend([info[conv_name], info[pool_name]])
    rng = np.random.default_rng(20261026)
    feeds = {"images": rng.random((2, 3, 512, 512), dtype=np.float32)}
    expected_conv, expected_pool = ort.InferenceSession(
        diagnostic.SerializeToString(), providers=["CPUExecutionProvider"]
    ).run([conv_name, pool_name], feeds)
    pool_dir = root / "taichi_vision/taichi_aot/neural_universal/models/int64_cpu_candidate_v14"
    with UniversalSession(original.SerializeToString(), backend="cpu", pool_dir=pool_dir) as session:
        actual_conv, actual_pool = session.run([conv_name, pool_name], feeds, step_limit=14)
    conv_delta = np.abs(actual_conv.astype(np.float64) - expected_conv.astype(np.float64))
    print(f"node12 conv shape={actual_conv.shape}, max_abs={conv_delta.max():.9g}")

    x = np.asarray(actual_conv, dtype=np.float32)
    a, b = x[:, :, 0::2, 0::2], x[:, :, 0::2, 1::2]
    c, d = x[:, :, 1::2, 0::2], x[:, :, 1::2, 1::2]
    seq = np.add(np.add(np.add(a, b, dtype=np.float32), c, dtype=np.float32), d, dtype=np.float32)
    pair = np.add(np.add(a, b, dtype=np.float32), np.add(c, d, dtype=np.float32), dtype=np.float32)
    for label, value in (("seq_div", seq / np.float32(4.0)), ("seq_mul", seq * np.float32(0.25)),
                         ("pair_div", pair / np.float32(4.0)), ("pair_mul", pair * np.float32(0.25))):
        delta = np.abs(value.astype(np.float64) - expected_pool.astype(np.float64))
        print(f"node13 {label} max_abs={delta.max():.9g}, rmse={np.sqrt(np.mean(delta*delta)):.9g}, "
              f"exact={np.array_equal(value, expected_pool)}")
    print(f"runtime pool max_abs={np.max(np.abs(actual_pool.astype(np.float64)-expected_pool)):.9g}")
    assert np.max(np.abs(actual_pool.astype(np.float64) - expected_pool)) <= 1e-6


def test_lightglue_instancenorm_actual_input_numeric_diagnostic():
    import onnx
    from onnx import helper, TensorProto, numpy_helper
    from taichi_vision.taichi_aot.neural_universal.plan import Plan
    from taichi_vision.taichi_aot.neural_universal.runtime import UniversalSession
    root = Path(__file__).resolve().parents[3]
    original = onnx.load(str(root / "database/Learning_Model/disk_lightglue_pipeline.ort.onnx"))
    rng = np.random.default_rng(20261026)
    feeds = {"images": rng.random((2, 3, 512, 512), dtype=np.float32)}
    pool = root / "taichi_vision/taichi_aot/neural_universal/models/int64_cpu_candidate_v14"
    pool_name = "/extractor/unet/path_down.1/path_down.1.0/AveragePool_output_0"
    with UniversalSession(original.SerializeToString(), backend="cpu", pool_dir=pool) as session:
        x = np.asarray(session.run([pool_name], feeds, step_limit=14)[0], dtype=np.float32)
    plan = Plan.from_model_bytes(original.SerializeToString())
    norm_node = plan.nodes[16]
    scale = np.asarray(plan.constants[norm_node.inputs[1]], np.float32)
    bias = np.asarray(plan.constants[norm_node.inputs[2]], np.float32)
    shape = tuple(x.shape)
    simple_graph = helper.make_graph(
        [helper.make_node("InstanceNormalization", ["x", "scale", "bias"], ["y"], epsilon=1e-5)],
        "instancenorm_probe",
        [helper.make_tensor_value_info("x", TensorProto.FLOAT, list(shape))],
        [helper.make_tensor_value_info("y", TensorProto.FLOAT, list(shape))],
        initializer=[numpy_helper.from_array(scale, "scale"), numpy_helper.from_array(bias, "bias")],
    )
    simple = helper.make_model(simple_graph, opset_imports=[helper.make_opsetid("", 17)])
    simple.ir_version = 9
    expected = ort.InferenceSession(simple.SerializeToString(), providers=["CPUExecutionProvider"]).run(None, {"x": x})[0]
    with UniversalSession(simple.SerializeToString(), backend="cpu", pool_dir=pool) as session:
        actual = session.run(None, {"x": x})[0]
    delta = np.abs(actual.astype(np.float64) - expected.astype(np.float64))
    print(f"InstanceNorm candidate max_abs={delta.max():.9g}, rmse={np.sqrt(np.mean(delta*delta)):.9g}")
    print(f"InstanceNorm probe scale={scale[:4]}, bias={bias[:4]}, epsilon={norm_node.attrs.get('epsilon')}")
    flat = x.astype(np.float64).reshape(x.shape[0], x.shape[1], -1)
    yflat = expected.astype(np.float64).reshape(x.shape[0], x.shape[1], -1)
    fitted_slope = np.empty(x.shape[:2], np.float64)
    fitted_intercept = np.empty(x.shape[:2], np.float64)
    for batch in range(x.shape[0]):
        for channel in range(x.shape[1]):
            xv, yv = flat[batch, channel], yflat[batch, channel]
            xc = xv - xv.mean()
            slope = float(np.dot(xc, yv - yv.mean()) / np.dot(xc, xc))
            intercept = float(yv.mean() - slope * xv.mean())
            fitted_slope[batch, channel] = slope
            fitted_intercept[batch, channel] = intercept
            residual = np.max(np.abs(yv - (slope * xv + intercept)))
            if batch == 0 and channel < 4:
                print(f"InstanceNorm ORT affine n={batch} c={channel}: slope={slope:.9g}, "
                      f"intercept={intercept:.9g}, residual={residual:.9g}, "
                      f"mean_eff={-intercept/slope:.9g}")
    slope32 = fitted_slope.astype(np.float32).reshape(x.shape[0], x.shape[1], 1, 1)
    intercept32 = fitted_intercept.astype(np.float32).reshape(x.shape[0], x.shape[1], 1, 1)
    fitted_variants = {
        "fit32_mul_add": x * slope32 + intercept32,
        "fit64_then_cast": (x.astype(np.float64) * fitted_slope[..., None, None]
                            + fitted_intercept[..., None, None]).astype(np.float32),
    }
    for label, result in fitted_variants.items():
        error = np.abs(result.astype(np.float64) - expected.astype(np.float64))
        print(f"InstanceNorm {label} max_abs={error.max():.9g}, rmse={np.sqrt(np.mean(error*error)):.9g}")
    for label, dtype in (("welford-f32", np.float32), ("welford-f64", np.float64),
                         ("moments-f32", np.float32)):
        probe = np.empty_like(expected)
        for batch in range(x.shape[0]):
            for channel in range(x.shape[1]):
                vals = x[batch, channel].ravel().astype(dtype)
                if label.startswith("welford"):
                    mean_value = dtype(0)
                    m2_value = dtype(0)
                    count_value = 0
                    for value in vals:
                        count_value += 1
                        delta_value = value - mean_value
                        mean_value = mean_value + delta_value / dtype(count_value)
                        delta2_value = value - mean_value
                        m2_value = m2_value + delta_value * delta2_value
                    var_value = m2_value / dtype(count_value)
                else:
                    mean_value = np.sum(vals, dtype=dtype) / dtype(vals.size)
                    var_value = np.sum(vals * vals, dtype=dtype) / dtype(vals.size) - mean_value * mean_value
                mean32_value = np.float32(mean_value)
                invstd_value = np.float32(1.0 / np.sqrt(np.float32(var_value) + np.float32(1e-5)))
                probe[batch, channel] = ((x[batch, channel] - mean32_value) * invstd_value
                                         * scale[channel] + bias[channel])
        err = np.abs(probe.astype(np.float64) - expected.astype(np.float64))
        print(f"InstanceNorm {label} max_abs={err.max():.9g}, rmse={np.sqrt(np.mean(err*err)):.9g}")
    eps = np.float32(1e-5)
    for label, stats_dtype, variance_kind in (("f32-centered", np.float32, "centered"),
                                               ("f64-centered", np.float64, "centered"),
                                               ("f64-moment", np.float64, "moment"),
                                               ("f64-unbiased", np.float64, "unbiased")):
        view = flat.astype(stats_dtype)
        mean = view.mean(axis=2, keepdims=True)
        if variance_kind == "centered":
            var = ((view - mean) ** 2).mean(axis=2, keepdims=True)
        else:
            var = (view * view).mean(axis=2, keepdims=True) - mean * mean
            if variance_kind == "unbiased":
                var *= view.shape[2] / (view.shape[2] - 1)
        mean32 = mean.astype(np.float32).reshape(x.shape[:2] + (1, 1))
        inv32 = (1.0 / np.sqrt(var.astype(np.float32) + eps)).astype(np.float32).reshape(x.shape[:2] + (1, 1))
        probe = (((x - mean32) * inv32) * scale.reshape(1, -1, 1, 1) + bias.reshape(1, -1, 1, 1))
        error = np.abs(probe.astype(np.float64) - expected.astype(np.float64))
        print(f"InstanceNorm {label} max_abs={error.max():.9g}, rmse={np.sqrt(np.mean(error*error)):.9g}")
    flat32 = x.reshape(x.shape[0], x.shape[1], -1)
    spatial = flat32.shape[-1]
    inv = np.float32(1.0 / np.float32(spatial))
    for width in (4, 8, 16, 32):
        lanes = np.zeros(flat32.shape[:2] + (width,), np.float32)
        blocks = flat32.reshape(flat32.shape[0], flat32.shape[1], -1, width)
        for block in range(blocks.shape[2]):
            lanes = np.add(lanes, blocks[:, :, block, :], dtype=np.float32)
        lane_mean = lanes.copy()
        while lane_mean.shape[-1] > 1:
            lane_mean = np.add(lane_mean[..., 0::2], lane_mean[..., 1::2], dtype=np.float32)
        mean_lane = (lane_mean[..., 0] * inv).astype(np.float32)[..., None]
        centered = flat32 - mean_lane
        sq_blocks = np.square(centered, dtype=np.float32).reshape(*flat32.shape[:2], -1, width)
        sq_lanes = np.zeros(flat32.shape[:2] + (width,), np.float32)
        for block in range(sq_blocks.shape[2]):
            sq_lanes = np.add(sq_lanes, sq_blocks[:, :, block, :], dtype=np.float32)
        lane_var = sq_lanes.copy()
        while lane_var.shape[-1] > 1:
            lane_var = np.add(lane_var[..., 0::2], lane_var[..., 1::2], dtype=np.float32)
        var = (lane_var[..., 0] * inv).astype(np.float32)[..., None]
        mean4 = mean_lane.reshape(x.shape[0], x.shape[1], 1, 1)
        invstd4 = (1.0 / np.sqrt(var + np.float32(1e-5))).astype(np.float32).reshape(x.shape[0], x.shape[1], 1, 1)
        probe = ((x - mean4) * invstd4) * scale.reshape(1, -1, 1, 1) + bias.reshape(1, -1, 1, 1)
        error = np.abs(probe.astype(np.float64) - expected.astype(np.float64))
        print(f"InstanceNorm simd-lane width={width} max_abs={error.max():.9g}, "
              f"rmse={np.sqrt(np.mean(error*error)):.9g}")
        if width == 8:
            print(f"InstanceNorm simd8 stats mean={mean4[0, :4, 0, 0]}, "
                  f"var={var[0, :4, 0]}, invstd={invstd4[0, :4, 0, 0]}")
            denom = np.sqrt(var + np.float32(1e-5)).astype(np.float32).reshape(x.shape[0], x.shape[1], 1, 1)
            scale4 = scale.reshape(1, -1, 1, 1)
            bias4 = bias.reshape(1, -1, 1, 1)
            delta4 = x - mean4
            formulas = {
                "delta_div": (delta4 / denom) * scale4 + bias4,
                "delta_scale_div": (delta4 * scale4) / denom + bias4,
                "x_inv_minus_mean_inv": (x * invstd4 - mean4 * invstd4) * scale4 + bias4,
                "affine": x * (scale4 / denom) + (bias4 - mean4 * (scale4 / denom)),
            }
            for formula_name, formula_value in formulas.items():
                formula_error = np.abs(formula_value.astype(np.float64) - expected.astype(np.float64))
                print(f"InstanceNorm simd8 {formula_name} max_abs={formula_error.max():.9g}, "
                      f"rmse={np.sqrt(np.mean(formula_error*formula_error)):.9g}")
            mean64 = mean4.astype(np.float64)
            inv64 = invstd4.astype(np.float64)
            fma_variants = {
                "fma_centered": (((x.astype(np.float64) - mean64) * inv64)
                                 * scale4.astype(np.float64) + bias4.astype(np.float64)).astype(np.float32),
                "fma_affine_f32_offset": (x.astype(np.float64) * inv64 * scale4.astype(np.float64)
                                          + (bias4 - mean4 * invstd4).astype(np.float64)).astype(np.float32),
                "fma_affine_f64_offset": (x.astype(np.float64) * inv64 * scale4.astype(np.float64)
                                          + (bias4.astype(np.float64) - mean64 * inv64)
                                          ).astype(np.float32),
            }
            for formula_name, formula_value in fma_variants.items():
                formula_error = np.abs(formula_value.astype(np.float64) - expected.astype(np.float64))
                print(f"InstanceNorm simd8 {formula_name} max_abs={formula_error.max():.9g}, "
                      f"rmse={np.sqrt(np.mean(formula_error*formula_error)):.9g}")
    width = 8
    lanes = np.zeros(flat32.shape[:2] + (width,), np.float32)
    blocks = flat32.reshape(flat32.shape[0], flat32.shape[1], -1, width)
    for block in range(blocks.shape[2]):
        lanes = np.add(lanes, blocks[:, :, block, :], dtype=np.float32)
    mean_seq = lanes[..., 0].copy()
    for lane in range(1, width):
        mean_seq = np.add(mean_seq, lanes[..., lane], dtype=np.float32)
    mean_seq = (mean_seq * inv).astype(np.float32)[..., None]
    centered = flat32 - mean_seq
    sq_blocks = np.square(centered, dtype=np.float32).reshape(*flat32.shape[:2], -1, width)
    sq_lanes = np.zeros(flat32.shape[:2] + (width,), np.float32)
    for block in range(sq_blocks.shape[2]):
        sq_lanes = np.add(sq_lanes, sq_blocks[:, :, block, :], dtype=np.float32)
    var_seq = sq_lanes[..., 0].copy()
    for lane in range(1, width):
        var_seq = np.add(var_seq, sq_lanes[..., lane], dtype=np.float32)
    var_seq = (var_seq * inv).astype(np.float32)[..., None]
    probe = ((x - mean_seq.reshape(x.shape[0], x.shape[1], 1, 1))
             * (1.0 / np.sqrt(var_seq + np.float32(1e-5))).astype(np.float32).reshape(x.shape[0], x.shape[1], 1, 1))
    probe = probe * scale.reshape(1, -1, 1, 1) + bias.reshape(1, -1, 1, 1)
    error = np.abs(probe.astype(np.float64) - expected.astype(np.float64))
    print(f"InstanceNorm simd-lane width=8 sequential horizontal max_abs={error.max():.9g}, "
          f"rmse={np.sqrt(np.mean(error*error)):.9g}")
    width = 8
    blocks = flat32.reshape(flat32.shape[0], flat32.shape[1], -1, width)
    for unroll in (2, 4, 8):
        accum = np.zeros(flat32.shape[:2] + (unroll, width), np.float32)
        for block in range(blocks.shape[2]):
            lane = block % unroll
            accum[:, :, lane, :] = np.add(accum[:, :, lane, :], blocks[:, :, block, :], dtype=np.float32)
        lane_sums = accum[:, :, 0, :].copy()
        for u in range(1, unroll):
            lane_sums = np.add(lane_sums, accum[:, :, u, :], dtype=np.float32)
        for _ in range(3):
            lane_sums = np.add(lane_sums[..., 0::2], lane_sums[..., 1::2], dtype=np.float32)
        mean_u = (lane_sums[..., 0] * inv).astype(np.float32)[..., None]
        centered = flat32 - mean_u
        sq_blocks = np.square(centered, dtype=np.float32).reshape(*flat32.shape[:2], -1, width)
        sq_accum = np.zeros(flat32.shape[:2] + (unroll, width), np.float32)
        for block in range(sq_blocks.shape[2]):
            lane = block % unroll
            sq_accum[:, :, lane, :] = np.add(sq_accum[:, :, lane, :], sq_blocks[:, :, block, :], dtype=np.float32)
        sq_sums = sq_accum[:, :, 0, :].copy()
        for u in range(1, unroll):
            sq_sums = np.add(sq_sums, sq_accum[:, :, u, :], dtype=np.float32)
        for _ in range(3):
            sq_sums = np.add(sq_sums[..., 0::2], sq_sums[..., 1::2], dtype=np.float32)
        var_u = (sq_sums[..., 0] * inv).astype(np.float32)[..., None]
        inv_u = (1.0 / np.sqrt(var_u + np.float32(1e-5))).astype(np.float32)
        probe = ((x - mean_u.reshape(x.shape[0], x.shape[1], 1, 1))
                 * inv_u.reshape(x.shape[0], x.shape[1], 1, 1))
        probe = probe * scale.reshape(1, -1, 1, 1) + bias.reshape(1, -1, 1, 1)
        error = np.abs(probe.astype(np.float64) - expected.astype(np.float64))
        print(f"InstanceNorm simd width=8 unroll={unroll} max_abs={error.max():.9g}, "
              f"rmse={np.sqrt(np.mean(error*error)):.9g}")


def test_plan_rejects_topk_non_fp32_input_explicitly():
    import onnx
    from onnx import helper, TensorProto, numpy_helper
    from taichi_vision.taichi_aot.neural_universal.errors import UnsupportedONNXOperatorError
    from taichi_vision.taichi_aot.neural_universal.plan import Plan

    graph = helper.make_graph(
        [helper.make_node("TopK", ["x", "k"], ["values", "indices"], axis=-1)],
        "topk_i64_reject", [helper.make_tensor_value_info("x", TensorProto.INT64, [1, 4])],
        [helper.make_tensor_value_info("values", TensorProto.INT64, [1, 2]),
         helper.make_tensor_value_info("indices", TensorProto.INT64, [1, 2])],
        initializer=[numpy_helper.from_array(np.array([2], np.int64), "k")],
    )
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 17)])
    model.ir_version = 9
    with pytest.raises(UnsupportedONNXOperatorError, match="TopK input dtype 'i64'.*FP32 only"):
        Plan.from_model_bytes(model.SerializeToString())


def test_plan_rejects_nonzero_i64_input_before_float_graph_binding():
    import onnx
    from onnx import helper, TensorProto
    from taichi_vision.taichi_aot.neural_universal.errors import UnsupportedONNXOperatorError
    from taichi_vision.taichi_aot.neural_universal.plan import Plan

    graph = helper.make_graph(
        [helper.make_node("NonZero", ["x"], ["coords"])], "nonzero_i64_reject",
        [helper.make_tensor_value_info("x", TensorProto.INT64, [2, 3])],
        [helper.make_tensor_value_info("coords", TensorProto.INT64, [2, 3])],
    )
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 17)])
    model.ir_version = 9
    with pytest.raises(UnsupportedONNXOperatorError, match="NonZero input dtype 'i64'.*FP32 and I32/BOOL"):
        Plan.from_model_bytes(model.SerializeToString())


def test_aot_gather_i64_data_i32_indices_promotes_and_checks_bounds():
    import onnx
    from onnx import helper, TensorProto
    from taichi_vision.taichi_aot.neural_universal.errors import UnsupportedStepError
    from taichi_vision.taichi_aot.neural_universal.runtime import UniversalSession

    graph = helper.make_graph(
        [helper.make_node("Gather", ["x", "indices"], ["y"], axis=1)],
        "gather_i64_data_i32_indices",
        [helper.make_tensor_value_info("x", TensorProto.INT64, [3, 4]),
         helper.make_tensor_value_info("indices", TensorProto.INT32, [3])],
        [helper.make_tensor_value_info("y", TensorProto.INT64, [3, 3])],
    )
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 17)])
    model.ir_version = 9
    model_bytes = model.SerializeToString()
    pool = Path(__file__).resolve().parents[3] / "taichi_vision/taichi_aot/neural_universal/models/int64_cpu_candidate_v15"
    x = np.arange(12, dtype=np.int64).reshape(3, 4)
    indices = np.array([2, -1, 0], dtype=np.int32)
    expected = ort.InferenceSession(model_bytes, providers=["CPUExecutionProvider"]).run(
        ["y"], {"x": x, "indices": indices}
    )[0]
    with UniversalSession(model_bytes, backend="cpu", pool_dir=pool) as session:
        assert "nu_gather_i64_indices_i64_candidate" in session.pool_graph_names
        actual = session.run(["y"], {"x": x, "indices": indices})[0]
        np.testing.assert_array_equal(actual, expected)
        bad_indices = np.array([4, 0, -1], dtype=np.int32)
        with pytest.raises(UnsupportedStepError, match="Gather failed closed: out-of-range index"):
            session.run(["y"], {"x": x, "indices": bad_indices})


@pytest.mark.parametrize(
    "start,limit,delta",
    [(2**53 + 1, 2**53 + 11, 3), (2**53 + 9, 2**53 - 1, -3)],
)
def test_range_i64_uses_exact_integer_values_above_float_precision(start, limit, delta):
    import onnx
    from onnx import helper, TensorProto, numpy_helper
    from taichi_vision.taichi_aot.neural_universal.runtime import UniversalSession

    graph = helper.make_graph(
        [helper.make_node("Range", ["start", "limit", "delta"], ["y"])],
        "range_i64_exact",
        [],
        [helper.make_tensor_value_info("y", TensorProto.INT64, [None])],
        initializer=[numpy_helper.from_array(np.array(v, np.int64), name)
                     for name, v in (("start", start), ("limit", limit), ("delta", delta))],
    )
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 17)])
    model.ir_version = 9
    model_bytes = model.SerializeToString()
    expected = ort.InferenceSession(model_bytes, providers=["CPUExecutionProvider"]).run(None, {})[0]
    pool = Path(__file__).resolve().parents[3] / "taichi_vision/taichi_aot/neural_universal/models/int64_cpu_candidate_v15"
    with UniversalSession(model_bytes, backend="cpu", pool_dir=pool) as session:
        actual = session.run(None, {})[0]
    np.testing.assert_array_equal(actual, expected)


def test_range_i64_rejects_unrepresentable_kernel_count_before_allocation():
    import onnx
    from onnx import helper, TensorProto, numpy_helper
    from taichi_vision.taichi_aot.neural_universal.errors import UnsupportedStepError
    from taichi_vision.taichi_aot.neural_universal.runtime import UniversalSession

    graph = helper.make_graph(
        [helper.make_node("Range", ["start", "limit", "delta"], ["y"])],
        "range_i64_count_guard", [],
        [helper.make_tensor_value_info("y", TensorProto.INT64, [None])],
        initializer=[numpy_helper.from_array(np.array(v, np.int64), name)
                     for name, v in (("start", 0), ("limit", 2**31 + 1), ("delta", 1))],
    )
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 17)])
    model.ir_version = 9
    pool = Path(__file__).resolve().parents[3] / "taichi_vision/taichi_aot/neural_universal/models/int64_cpu_candidate_v15"
    with UniversalSession(model.SerializeToString(), backend="cpu", pool_dir=pool) as session:
        with pytest.raises(UnsupportedStepError, match="kernel ABI supports at most"):
            session.run(None, {})


def _make_instancenorm_model(shape, scale, bias, epsilon):
    import onnx
    from onnx import helper, TensorProto, numpy_helper

    graph = helper.make_graph(
        [helper.make_node("InstanceNormalization", ["x", "scale", "bias"], ["y"],
                          epsilon=float(epsilon))],
        "instance_norm_packet4_candidate",
        [helper.make_tensor_value_info("x", TensorProto.FLOAT, list(shape))],
        [helper.make_tensor_value_info("y", TensorProto.FLOAT, list(shape))],
        initializer=[numpy_helper.from_array(np.asarray(scale, np.float32), "scale"),
                     numpy_helper.from_array(np.asarray(bias, np.float32), "bias")],
    )
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 17)])
    model.ir_version = 9
    return model.SerializeToString()


def _assert_instancenorm_packet4_candidate_matches_ort(model_bytes, feeds, label):
    from taichi_vision.taichi_aot.neural_universal.runtime import UniversalSession

    expected = ort.InferenceSession(model_bytes, providers=["CPUExecutionProvider"]).run(None, feeds)[0]
    pool = Path(__file__).resolve().parents[3] / "taichi_vision/taichi_aot/neural_universal/models/int64_cpu_candidate_v18"
    with UniversalSession(model_bytes, backend="cpu", pool_dir=pool) as session:
        assert session.int64_candidate
        assert "nu_instance_norm_packet4_affine_candidate" in session.pool_graph_names
        actual = session.run(None, feeds)[0]
    actual, expected = np.asarray(actual), np.asarray(expected)
    assert actual.shape == expected.shape, f"{label}: {actual.shape} != {expected.shape}"
    delta = np.abs(actual.astype(np.float64) - expected.astype(np.float64))
    max_abs = float(delta.max(initial=0.0))
    rmse = float(np.sqrt(np.mean(delta * delta)))
    print(f"{label}: max_abs={max_abs:.9g}, rmse={rmse:.9g}, exact={np.array_equal(actual, expected)}")
    assert np.isfinite(actual).all() == np.isfinite(expected).all(), f"{label}: finite mask mismatch"
    assert max_abs <= 1e-6, f"{label}: max_abs={max_abs}, rmse={rmse}"


@pytest.mark.parametrize(
    "shape,epsilon",
    [((1, 2, 1, 3), 1e-5), ((1, 3, 1, 7), 1e-3), ((2, 2, 1, 11), 1e-4)],
)
def test_instancenorm_packet4_candidate_jit_tails_and_short_rows(shape, epsilon):
    rng = np.random.default_rng(20261026 + int(np.prod(shape)))
    channels = shape[1]
    x = rng.normal(0.0, 1.0, size=shape).astype(np.float32)
    scale = rng.normal(1.0, 0.25, size=(channels,)).astype(np.float32)
    bias = rng.normal(0.0, 0.25, size=(channels,)).astype(np.float32)
    model_bytes = _make_instancenorm_model(shape, scale, bias, epsilon)
    expected = ort.InferenceSession(model_bytes, providers=["CPUExecutionProvider"]).run(None, {"x": x})[0]
    actual = np.empty_like(x)
    nu_instance_norm_packet4_affine_candidate(
        x.reshape(-1), scale, bias, actual.reshape(-1), shape[0], channels,
        int(np.prod(shape[2:])), np.float32(epsilon), 1, 1,
    )
    delta = np.abs(actual.astype(np.float64) - expected.astype(np.float64))
    max_abs = float(delta.max(initial=0.0))
    rmse = float(np.sqrt(np.mean(delta * delta)))
    print(f"JIT InstanceNorm shape={shape} eps={epsilon}: max_abs={max_abs:.9g}, rmse={rmse:.9g}")
    assert max_abs <= 1e-6, f"JIT short/tail InstanceNorm max_abs={max_abs}, rmse={rmse}"


def test_instancenorm_packet4_candidate_matches_ort_on_actual_lightglue_input():
    import onnx
    from taichi_vision.taichi_aot.neural_universal.plan import Plan
    from taichi_vision.taichi_aot.neural_universal.runtime import UniversalSession

    root = Path(__file__).resolve().parents[3]
    original = onnx.load(str(root / "database/Learning_Model/disk_lightglue_pipeline.ort.onnx"),
                         load_external_data=True)
    plan = Plan.from_model_bytes(original.SerializeToString())
    node = plan.nodes[16]
    rng = np.random.default_rng(20261026)
    feeds = {"images": rng.random((2, 3, 512, 512), dtype=np.float32)}
    pool_v14 = root / "taichi_vision/taichi_aot/neural_universal/models/int64_cpu_candidate_v14"
    input_name = "/extractor/unet/path_down.1/path_down.1.0/AveragePool_output_0"
    with UniversalSession(original.SerializeToString(), backend="cpu", pool_dir=pool_v14) as session:
        x = np.asarray(session.run([input_name], feeds, step_limit=14)[0], dtype=np.float32)

    model_bytes = _make_instancenorm_model(
        x.shape,
        plan.constants[node.inputs[1]],
        plan.constants[node.inputs[2]],
        node.attrs["epsilon"],
    )
    _assert_instancenorm_packet4_candidate_matches_ort(
        model_bytes, {"x": x}, "LightGlue node16 actual input `[2,16,256,256]` FP32",
    )


@pytest.mark.parametrize(
    "shape,epsilon",
    [((2, 3, 3, 5), 1e-5), ((1, 2, 2, 4), 1e-3), ((1, 1, 1, 7), 1e-4)],
)
def test_instancenorm_packet4_candidate_matches_ort_synthetic(shape, epsilon):
    rng = np.random.default_rng(20261026 + int(np.prod(shape)))
    channels = shape[1]
    x = rng.normal(0.0, 1.0, size=shape).astype(np.float32)
    scale = rng.normal(1.0, 0.25, size=(channels,)).astype(np.float32)
    bias = rng.normal(0.0, 0.25, size=(channels,)).astype(np.float32)
    model_bytes = _make_instancenorm_model(shape, scale, bias, epsilon)
    _assert_instancenorm_packet4_candidate_matches_ort(
        model_bytes, {"x": x}, f"synthetic InstanceNorm shape={shape} eps={epsilon}",
    )


def test_v18_candidate_manifest_rejects_identity_and_hash_tampering():
    import copy
    import json
    from taichi_vision.taichi_aot.neural_universal.runtime import _validate_candidate_manifest_v2

    pool = Path(__file__).resolve().parents[3] / "taichi_vision/taichi_aot/neural_universal/models/int64_cpu_candidate_v18"
    tcm = pool / "neural_cpu.tcm"
    manifest = json.loads((pool / "candidate_manifest.json").read_text(encoding="utf-8"))
    assert _validate_candidate_manifest_v2(manifest, tcm)
    for path, value in (
        (("backend",), "vulkan"),
        (("runtime_abi",), int(manifest["runtime_abi"]) + 1),
        (("target_identity", "backend"), "vulkan"),
        (("kernel_sources_sha256",), "0" * 64),
        (("tcm_sha256",), "0" * 64),
        (("compile_options", "fast_math"), True),
    ):
        corrupted = copy.deepcopy(manifest)
        cursor = corrupted
        for key in path[:-1]:
            cursor = cursor[key]
        cursor[path[-1]] = value
        assert not _validate_candidate_manifest_v2(corrupted, tcm), path


def test_v17_candidate_aot_nonzero_bool_mask_matches_ort_row_major():
    import onnx
    from onnx import helper, TensorProto
    from taichi_vision.taichi_aot.neural_universal.runtime import UniversalSession

    mask = np.array([[False, True, False], [True, True, False]], dtype=np.bool_)
    graph = helper.make_graph(
        [helper.make_node("NonZero", ["mask"], ["coords"])],
        "nonzero_bool_candidate_v17",
        [helper.make_tensor_value_info("mask", TensorProto.BOOL, [2, 3])],
        [helper.make_tensor_value_info("coords", TensorProto.INT64, [2, 3])],
    )
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 17)])
    model.ir_version = 9
    model_bytes = model.SerializeToString()
    expected = ort.InferenceSession(model_bytes, providers=["CPUExecutionProvider"]).run(
        None, {"mask": mask}
    )[0]
    pool = Path(__file__).resolve().parents[3] / "taichi_vision/taichi_aot/neural_universal/models/int64_cpu_candidate_v18"
    with UniversalSession(model_bytes, backend="cpu", pool_dir=pool) as session:
        actual = session.run(None, {"mask": mask})[0]
    np.testing.assert_array_equal(actual, expected)
