#!/usr/bin/env python3
from pathlib import Path
import argparse
import struct


PATCHES = (
    {
        "name": "YTPSettingsBuilder patreonSection -> prefsTable",
        "offset": 0xB9B9D0,
        "expected": bytes.fromhex("5cb45dff"),
        "replacement": bytes.fromhex("307a5dff"),
    },
)


def patch_file(path: Path) -> None:
    data = bytearray(path.read_bytes())

    for patch in PATCHES:
        offset = patch["offset"]
        expected = patch["expected"]
        replacement = patch["replacement"]
        current = bytes(data[offset : offset + len(expected)])

        if current == replacement:
            print(f"{path}: already patched ({patch['name']})")
            continue

        if current != expected:
            raise SystemExit(
                f"{path}: unexpected bytes for {patch['name']} at 0x{offset:x}: "
                f"got {current.hex()}, expected {expected.hex()}"
            )

        data[offset : offset + len(expected)] = replacement
        old_target = offset + struct.unpack("<i", expected)[0]
        new_target = offset + struct.unpack("<i", replacement)[0]
        print(
            f"{path}: patched {patch['name']} "
            f"(0x{old_target:x} -> 0x{new_target:x})"
        )

    path.write_bytes(data)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Patch YTLite.dylib so the Patreon/auth section dispatches to the normal preferences table."
    )
    parser.add_argument("dylib", type=Path, help="Path to YTLite.dylib")
    args = parser.parse_args()

    patch_file(args.dylib)


if __name__ == "__main__":
    main()
