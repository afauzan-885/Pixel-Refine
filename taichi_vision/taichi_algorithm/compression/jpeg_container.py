"""Pure-Python standard-library JFIF marker builder for Taichi scan output."""
from __future__ import annotations

import struct
from collections.abc import Mapping

from .jpeg_tables import JPEG_ZIGZAG


STANDARD_DHT = bytes.fromhex(
    "0000010501010101010100000000000000000102030405060708090a0b"
    "100002010303020403050504040000017d01020300041105122131410613516107227114328191a1082342b1c11552d1f02433627282090a161718191a25262728292a3435363738393a434445464748494a535455565758595a636465666768696a737475767778797a838485868788898a92939495969798999aa2a3a4a5a6a7a8a9aab2b3b4b5b6b7b8b9bac2c3c4c5c6c7c8c9cad2d3d4d5d6d7d8d9dae1e2e3e4e5e6e7e8e9eaf1f2f3f4f5f6f7f8f9fa"
    "0100030101010101010101010000000000000102030405060708090a0b"
    "1100020102040403040705040400010277000102031104052131061241510761711322328108144291a1b1c109233352f0156272d10a162434e125f11718191a262728292a35363738393a434445464748494a535455565758595a636465666768696a737475767778797a82838485868788898a92939495969798999aa2a3a4a5a6a7a8a9aab2b3b4b5b6b7b8b9bac2c3c4c5c6c7c8c9cad2d3d4d5d6d7d8d9dae2e3e4e5e6e7e8e9eaf2f3f4f5f6f7f8f9fa"
)

# JPEG marker payloads store quantization values in zig-zag order, while the
# encoder keeps its tables in natural 8x8 order for the DCT kernel.
_JPEG_ZIGZAG = JPEG_ZIGZAG


def _marker(code: int, payload: bytes = b"") -> bytes:
    if not 0 <= int(code) <= 255:
        raise ValueError("JPEG marker code must fit in one byte")
    if len(payload) > 65533:
        raise ValueError("JPEG marker payload exceeds the 64 KiB segment limit")
    return b"\xff" + bytes((code,)) + struct.pack(">H", len(payload) + 2) + payload


def app0_jfif() -> bytes:
    return _marker(0xE0, b"JFIF\x00" + bytes((1, 1, 0)) + struct.pack(">HHBB", 1, 1, 0, 0))


def dqt(table: tuple[int, ...], table_id: int = 0) -> bytes:
    if len(table) != 64 or not 0 <= table_id <= 3:
        raise ValueError("JPEG quantization table must contain 64 values")
    values = bytes(max(1, min(255, int(table[index]))) for index in _JPEG_ZIGZAG)
    return _marker(0xDB, bytes((table_id,)) + values)


def sof0(width: int, height: int, components: int = 3, y_sampling: int = 0x11) -> bytes:
    if not 1 <= width <= 65535 or not 1 <= height <= 65535 or components not in (1, 3):
        raise ValueError("baseline JPEG dimensions/components are unsupported")
    if components == 1:
        if y_sampling != 0x11:
            raise ValueError("grayscale baseline JPEG requires 1x1 sampling")
        payload = bytes((8,)) + struct.pack(">HH", height, width) + bytes((1, 1, 0x11, 0))
        return _marker(0xC0, payload)
    if y_sampling not in (0x11, 0x21, 0x22):
        raise ValueError("unsupported baseline JPEG luma sampling")
    payload = bytes((8,)) + struct.pack(">HH", height, width) + bytes((3,))
    payload += bytes((1, y_sampling, 0, 2, 0x11, 1, 3, 0x11, 1))
    return _marker(0xC0, payload)


def dht(bits: tuple[int, ...], values: tuple[int, ...], table_class: int, table_id: int) -> bytes:
    if len(bits) != 16 or sum(bits) != len(values):
        raise ValueError("invalid JPEG Huffman table")
    if table_class not in (0, 1) or table_id not in (0, 1):
        raise ValueError("invalid JPEG Huffman table id")
    return _marker(0xC4, bytes(((table_class << 4) | table_id,)) + bytes(bits) + bytes(values))


def dri(restart_interval: int) -> bytes:
    """Serialize a JPEG restart interval in MCU units."""

    restart_interval = int(restart_interval)
    if not 1 <= restart_interval <= 65535:
        raise ValueError("JPEG restart interval must be in [1, 65535]")
    return _marker(0xDD, struct.pack(">H", restart_interval))


def sos(components: int = 3) -> bytes:
    if components == 1:
        return _marker(0xDA, bytes((1, 1, 0, 0, 63, 0)))
    # Y uses DC/AC table pair 0; both chroma components use pair 1.
    payload = bytes((3, 1, 0, 2, 0x11, 3, 0x11, 0, 63, 0))
    return _marker(0xDA, payload)


def _metadata_segments(metadata: Mapping | None) -> bytes:
    """Serialize the bounded, interoperable JFIF metadata subset.

    The encoder deliberately keeps metadata policy explicit.  EXIF, XMP,
    ICC, and COM are inserted as marker segments before the frame header; no
    opaque application bytes are accepted because that would make marker
    length and decoder behavior impossible to audit.
    """
    if metadata is None:
        return b""
    if not isinstance(metadata, Mapping):
        raise TypeError("JPEG metadata must be a mapping")
    supported = {"exif", "xmp", "icc", "comment"}
    unknown = set(metadata) - supported
    if unknown:
        raise ValueError(f"unsupported JPEG metadata keys: {sorted(unknown)!r}")

    def metadata_bytes(value, key: str) -> bytes:
        # ``bytes(4)`` silently creates four zero bytes, which is almost
        # certainly a caller error for EXIF/XMP/ICC payloads.  Keep the
        # accepted boundary explicit and consistent across all metadata keys.
        if isinstance(value, (str, int, bool)):
            raise TypeError(f"JPEG metadata field {key!r} must be bytes-like")
        try:
            return bytes(value)
        except (TypeError, ValueError) as exc:
            raise TypeError(f"JPEG metadata field {key!r} must be bytes-like") from exc

    output = bytearray()
    if "exif" in metadata:
        exif = metadata_bytes(metadata["exif"], "exif")
        if not exif.startswith(b"Exif\x00\x00"):
            exif = b"Exif\x00\x00" + exif
        output.extend(_marker(0xE1, exif))
    if "xmp" in metadata:
        xmp = metadata_bytes(metadata["xmp"], "xmp")
        namespace = b"http://ns.adobe.com/xap/1.0/\x00"
        if xmp.startswith(namespace):
            payload = xmp
        else:
            payload = namespace + xmp
        output.extend(_marker(0xE1, payload))
    if "icc" in metadata:
        profile = metadata_bytes(metadata["icc"], "icc")
        # APP2 allows at most 65,533 payload bytes.  Twelve bytes are used by
        # the ICC signature and two by the sequence/count fields.
        chunk_size = 65533 - 14
        chunks = [profile[index:index + chunk_size] for index in range(0, len(profile), chunk_size)] or [b""]
        if len(chunks) > 255:
            raise ValueError("JPEG ICC profile requires more than 255 APP2 segments")
        for index, chunk in enumerate(chunks, 1):
            output.extend(_marker(0xE2, b"ICC_PROFILE\x00" + bytes((index, len(chunks))) + chunk))
    if "comment" in metadata:
        comment = metadata["comment"]
        if isinstance(comment, str):
            comment = comment.encode("utf-8")
        else:
            comment = metadata_bytes(comment, "comment")
        output.extend(_marker(0xFE, bytes(comment)))
    return bytes(output)


def assemble_jfif(
    scan_data: bytes,
    width: int,
    height: int,
    luma_q: tuple[int, ...],
    chroma_q: tuple[int, ...],
    huffman_tables: bytes,
    y_sampling: int = 0x11,
    components: int = 3,
    *,
    metadata: Mapping | None = None,
    restart_interval: int = 0,
) -> bytes:
    """Assemble a baseline JFIF stream from Taichi-produced scan bytes."""
    tables = dqt(luma_q, 0) if components == 1 else dqt(luma_q, 0) + dqt(chroma_q, 1)
    restart = b"" if int(restart_interval) == 0 else dri(restart_interval)
    return b"\xff\xd8" + app0_jfif() + _metadata_segments(metadata) + tables + sof0(width, height, components, y_sampling) + huffman_tables + restart + sos(components) + bytes(scan_data) + b"\xff\xd9"


def assemble_baseline_jfif(
    scan_data: bytes,
    width: int,
    height: int,
    luma_q: tuple[int, ...],
    chroma_q: tuple[int, ...],
    y_sampling: int = 0x11,
    *,
    metadata: Mapping | None = None,
    restart_interval: int = 0,
) -> bytes:
    return assemble_jfif(scan_data, width, height, luma_q, chroma_q, _raw_dht_markers(), y_sampling, 3, metadata=metadata, restart_interval=restart_interval)


def assemble_grayscale_jfif(
    scan_data: bytes,
    width: int,
    height: int,
    luma_q: tuple[int, ...],
    *,
    metadata: Mapping | None = None,
    restart_interval: int = 0,
) -> bytes:
    return assemble_jfif(scan_data, width, height, luma_q, luma_q, _raw_dht_markers(), 0x11, 1, metadata=metadata, restart_interval=restart_interval)


def _raw_dht_markers() -> bytes:
    # Split the four standard table payloads from the canonical concatenation.
    pos = 0
    output = bytearray()
    while pos < len(STANDARD_DHT):
        table_class_id = STANDARD_DHT[pos]
        count = sum(STANDARD_DHT[pos + 1:pos + 17])
        payload = STANDARD_DHT[pos:pos + 17 + count]
        output.extend(_marker(0xC4, payload))
        pos += 17 + count
    return bytes(output)
