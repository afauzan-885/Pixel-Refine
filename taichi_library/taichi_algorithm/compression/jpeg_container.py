"""Pure-Python standard-library JFIF marker builder for Taichi scan output."""
from __future__ import annotations

import struct


STANDARD_DHT = bytes.fromhex(
    "0000010501010101010100000000000000000102030405060708090a0b"
    "100002010303020403050504040000017d01020300041105122131410613516107227114328191a1082342b1c11552d1f02433627282090a161718191a25262728292a3435363738393a434445464748494a535455565758595a636465666768696a737475767778797a838485868788898a92939495969798999aa2a3a4a5a6a7a8a9aab2b3b4b5b6b7b8b9bac2c3c4c5c6c7c8c9cad2d3d4d5d6d7d8d9dae1e2e3e4e5e6e7e8e9eaf1f2f3f4f5f6f7f8f9fa"
    "0100030101010101010101010000000000000102030405060708090a0b"
    "1100020102040403040705040400010277000102031104052131061241510761711322328108144291a1b1c109233352f0156272d10a162434e125f11718191a262728292a35363738393a434445464748494a535455565758595a636465666768696a737475767778797a82838485868788898a92939495969798999aa2a3a4a5a6a7a8a9aab2b3b4b5b6b7b8b9bac2c3c4c5c6c7c8c9cad2d3d4d5d6d7d8d9dae2e3e4e5e6e7e8e9eaf2f3f4f5f6f7f8f9fa"
)


def _marker(code: int, payload: bytes = b"") -> bytes:
    if not payload:
        return bytes((0xFF, code))
    return b"\xff" + bytes((code,)) + struct.pack(">H", len(payload) + 2) + payload


def app0_jfif() -> bytes:
    return _marker(0xE0, b"JFIF\x00" + bytes((1, 1, 0)) + struct.pack(">HHBB", 1, 1, 0, 0))


def dqt(table: tuple[int, ...], table_id: int = 0) -> bytes:
    if len(table) != 64 or not 0 <= table_id <= 3:
        raise ValueError("JPEG quantization table must contain 64 values")
    return _marker(0xDB, bytes((table_id,)) + bytes(max(1, min(255, int(x))) for x in table))


def sof0(width: int, height: int, components: int = 3, y_sampling: int = 0x11) -> bytes:
    if not 1 <= width <= 65535 or not 1 <= height <= 65535 or components not in (1, 3):
        raise ValueError("baseline JPEG dimensions/components are unsupported")
    if components == 1:
        payload = bytes((8,)) + struct.pack(">HH", height, width) + bytes((1, 1, 0x11, 0))
        return _marker(0xC0, payload)
    payload = bytes((8,)) + struct.pack(">HH", height, width) + bytes((3,))
    payload += bytes((1, y_sampling, 0, 2, 0x11, 1, 3, 0x11, 1))
    return _marker(0xC0, payload)


def dht(bits: tuple[int, ...], values: tuple[int, ...], table_class: int, table_id: int) -> bytes:
    if len(bits) != 16 or sum(bits) != len(values):
        raise ValueError("invalid JPEG Huffman table")
    if table_class not in (0, 1) or table_id not in (0, 1):
        raise ValueError("invalid JPEG Huffman table id")
    return _marker(0xC4, bytes((table_class << 4) | table_id) + bytes(bits) + bytes(values))


def sos(components: int = 3) -> bytes:
    if components == 1:
        return _marker(0xDA, bytes((1, 1, 0, 0, 63, 0)))
    payload = bytes((3, 1, 0, 2, 0x11, 3, 0x11, 0, 63, 0))
    return _marker(0xDA, payload)


def assemble_jfif(scan_data: bytes, width: int, height: int, luma_q: tuple[int, ...], chroma_q: tuple[int, ...], huffman_tables: bytes, y_sampling: int = 0x11, components: int = 3) -> bytes:
    """Assemble a baseline JFIF stream from Taichi-produced scan bytes."""
    tables = dqt(luma_q, 0) if components == 1 else dqt(luma_q, 0) + dqt(chroma_q, 1)
    return b"\xff\xd8" + app0_jfif() + tables + sof0(width, height, components, y_sampling) + huffman_tables + sos(components) + scan_data + b"\xff\xd9"


def assemble_baseline_jfif(scan_data: bytes, width: int, height: int, luma_q: tuple[int, ...], chroma_q: tuple[int, ...], y_sampling: int = 0x11) -> bytes:
    return assemble_jfif(scan_data, width, height, luma_q, chroma_q, _raw_dht_markers(), y_sampling, 3)


def assemble_grayscale_jfif(scan_data: bytes, width: int, height: int, luma_q: tuple[int, ...]) -> bytes:
    return assemble_jfif(scan_data, width, height, luma_q, luma_q, _raw_dht_markers(), 0x11, 1)


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
