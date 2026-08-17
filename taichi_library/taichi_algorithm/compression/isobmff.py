"""Strict minimal ISO Base Media File Format helpers for HEIF/AVIF."""
from __future__ import annotations

import struct
from dataclasses import dataclass


def _fourcc(value: str | bytes) -> bytes:
    raw = value.encode("ascii") if isinstance(value, str) else bytes(value)
    if len(raw) != 4:
        raise ValueError("ISO-BMFF box type must be four bytes")
    return raw


def box(box_type: str | bytes, payload: bytes, *, large: bool = False) -> bytes:
    kind = _fourcc(box_type)
    if large or len(payload) + 8 >= 0x100000000:
        return struct.pack(">I4sQ", 1, kind, len(payload) + 16) + payload
    return struct.pack(">I4s", len(payload) + 8, kind) + payload


def full_box(box_type: str | bytes, version: int, flags: int, payload: bytes) -> bytes:
    if not 0 <= version <= 255 or not 0 <= flags <= 0xFFFFFF:
        raise ValueError("invalid FullBox version/flags")
    return box(box_type, bytes((version,)) + flags.to_bytes(3, "big") + payload)


def ftyp(major_brand: str, minor_version: int, compatible: tuple[str, ...]) -> bytes:
    return box("ftyp", _fourcc(major_brand) + struct.pack(">I", minor_version) + b"".join(_fourcc(x) for x in compatible))


def ispe(width: int, height: int) -> bytes:
    if not 1 <= width <= 0xFFFFFFFF or not 1 <= height <= 0xFFFFFFFF:
        raise ValueError("invalid image dimensions")
    return full_box("ispe", 0, 0, struct.pack(">III", 0, width, height))


def pixi(bit_depth: int, channels: int = 3) -> bytes:
    if not 1 <= bit_depth <= 16 or not 1 <= channels <= 4:
        raise ValueError("invalid pixi parameters")
    return full_box("pixi", 0, 0, bytes((channels,)) + bytes((bit_depth,) * channels))


def colr_nclx(primaries: int = 1, transfer: int = 13, matrix: int = 6, full_range: bool = True) -> bytes:
    colour = struct.pack(">4sHHHB", b"nclx", primaries, transfer, matrix, 0x80 if full_range else 0)
    return box("colr", colour)


def pitm(item_id: int = 1) -> bytes:
    return full_box("pitm", 0, 0, struct.pack(">H", item_id))


def infe(item_id: int, item_type: str, name: str = "Pixel Refine image") -> bytes:
    return full_box("infe", 2, 0, struct.pack(">HH4s", item_id, 0, _fourcc(item_type)) + name.encode("utf-8") + b"\x00")


def iinf(item_id: int, item_type: str, name: str = "Pixel Refine image") -> bytes:
    return full_box("iinf", 0, 0, struct.pack(">H", 1) + infe(item_id, item_type, name))


def iloc(item_id: int, extent_offset: int, extent_length: int) -> bytes:
    if not 0 <= extent_offset <= 0xFFFFFFFF or not 0 <= extent_length <= 0xFFFFFFFF:
        raise ValueError("iloc extent exceeds version-0 limits")
    payload = bytes((0x44, 0x00)) + struct.pack(">H", 1)
    payload += struct.pack(">HHHII", item_id, 0, 1, extent_offset, extent_length)
    return full_box("iloc", 0, 0, payload)


def ipco(properties: tuple[bytes, ...]) -> bytes:
    return box("ipco", b"".join(properties))


def ipma(item_id: int, property_indices: tuple[int, ...]) -> bytes:
    if not property_indices or any(not 1 <= index <= 0x7F for index in property_indices):
        raise ValueError("invalid item property association")
    associations = bytes((len(property_indices),)) + bytes(index for index in property_indices)
    payload = struct.pack(">I", 1) + struct.pack(">HB", item_id, len(property_indices)) + associations[1:]
    return full_box("ipma", 0, 0, payload)


def iprp(item_id: int, properties: tuple[bytes, ...]) -> bytes:
    return box("iprp", ipco(properties) + ipma(item_id, tuple(range(1, len(properties) + 1))))


@dataclass(frozen=True)
class Box:
    type: bytes
    offset: int
    size: int
    payload: bytes


def parse_boxes(data: bytes, start: int = 0, end: int | None = None, max_depth: int = 16, max_boxes: int = 4096) -> tuple[Box, ...]:
    if max_depth <= 0:
        raise ValueError("ISO-BMFF nesting limit exceeded")
    if max_boxes <= 0:
        raise ValueError("ISO-BMFF box limit must be positive")
    end = len(data) if end is None else end
    if start < 0 or end < start or end > len(data):
        raise ValueError("invalid ISO-BMFF range")
    boxes: list[Box] = []
    offset = start
    while offset < end:
        if len(boxes) >= max_boxes:
            raise ValueError("ISO-BMFF box limit exceeded")
        if end - offset < 8:
            raise ValueError("truncated ISO-BMFF box header")
        size, kind = struct.unpack(">I4s", data[offset:offset + 8])
        header = 8
        if size == 1:
            if end - offset < 16:
                raise ValueError("truncated large ISO-BMFF box")
            size = struct.unpack(">Q", data[offset + 8:offset + 16])[0]
            header = 16
        elif size == 0:
            size = end - offset
        if size < header or offset + size > end:
            raise ValueError("invalid ISO-BMFF box size")
        boxes.append(Box(kind, offset, size, data[offset + header:offset + size]))
        offset += size
    return tuple(boxes)


def full_box_payload(item: Box) -> tuple[int, int, bytes]:
    if len(item.payload) < 4:
        raise ValueError("truncated FullBox")
    return item.payload[0], int.from_bytes(item.payload[1:4], "big"), item.payload[4:]


__all__ = [
    "Box", "box", "full_box", "ftyp", "ispe", "pixi", "colr_nclx", "pitm",
    "infe", "iinf", "iloc", "ipco", "ipma", "iprp", "parse_boxes", "full_box_payload",
]
