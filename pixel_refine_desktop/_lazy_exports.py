"""Small helper for cycle-safe package exports."""

from importlib import import_module


def resolve_lazy_attribute(name, imports, namespace):
    """Import and cache one public package attribute on first access."""
    try:
        module_name, attribute_name = imports[name]
    except KeyError as exc:
        raise AttributeError(
            f"module {namespace.get('__name__', '<module>')!r} has no attribute {name!r}"
        ) from exc

    value = getattr(import_module(module_name), attribute_name)
    namespace[name] = value
    return value


def public_names(namespace, exports):
    """Return normal module names plus declared lazy exports."""
    return sorted(set(namespace) | set(exports))
