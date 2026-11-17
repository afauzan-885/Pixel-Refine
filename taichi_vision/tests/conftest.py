"""Register the `slow` marker.

The real-model parity gates take tens of seconds because they load large models.
Marking them lets `-m "not slow"` run the fast suite while keeping the gates
available, and registering the marker keeps the run output free of warnings that
would otherwise hide a real one.
"""


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "slow: runs a full model against ONNX Runtime; tens of seconds",
    )
