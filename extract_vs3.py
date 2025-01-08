import argparse
import os

parser = argparse.ArgumentParser(description="Keitai VS3 Structure")
parser.add_argument("input")
parser.add_argument("output")
parser.add_argument(
    "-r",
    "--raw",
    help="Extract raw data instead of files.",
    action=argparse.BooleanOptionalAction,
)
parser.add_argument(
    "-s",
    "--size",
    help="Chunk size (*0x20000).",
    default=1,
    type=int,
)
parser.add_argument(
    "-l",
    "--limit-size",
    help="Use referenced file sizes.",
    action=argparse.BooleanOptionalAction,
)

args = parser.parse_args()

os.makedirs(args.output, exist_ok=True)
blocks_per_chunk = (args.size * 0x20000 - 0x400) // 0x400

with open(args.input, "rb") as file:
    blocks = {}
    conflicts = {}
    data = file.read(args.size * 0x20000)
    addr = 0
    while len(data) > 0:
        match = 0
        search = 0
        if int.from_bytes(data[4:6], "little") == 0xC5A3:
            exid = int.from_bytes(data[10:12], "little")
            if exid != 0xFFFF:
                exid *= blocks_per_chunk
                conflicts[exid] = conflicts.get(exid, 0x10000)
                current = int.from_bytes(data[:2], "little")
                if current < conflicts[exid]:
                    conflicts[exid] = current
                    for i in range(blocks_per_chunk):
                        inner = data[0xC + i * 0x400 : 0x40C + i * 0x400]
                        blty = int.from_bytes(inner[0:2], "little")
                        if blty != 0xFFFF:
                            blocks[blty] = blocks.get(blty, {})
                            blocks[blty][exid] = inner[2:]
                        exid += 1
        data = file.read(args.size * 0x20000)
        addr += args.size * 0x20000

for k, v in blocks.get(0xFC30, {}).items():
    off = 0x12 + 4 * args.size
    maxsize = int.from_bytes(v[2 + args.size * 2 : 6 + args.size * 2], "little")
    out = bytearray()
    extend = True
    while extend:
        while int.from_bytes(v[off : off + args.size * 2], "little") != (
            1 << (args.size << 4)
        ) - 1 and off < len(v):
            block_id = int.from_bytes(v[off : off + args.size * 2], "little")
            c = blocks.get(0xFFF0, {}).get(block_id, b"")
            if c == b"":
                c = blocks.get(0xFFFC, {}).get(block_id, b"")
            if c == b"":
                print("WARNING %d" % block_id)
                c = bytes(0x3FE)
            out += c
            off += args.size * 2
        follow = int.from_bytes(v[: args.size * 2], "little")
        if follow != (1 << (args.size << 4)) - 1:
            v = blocks[0xFCF0][follow]
            off = args.size * 2
        else:
            extend = False
    if out[:3] == b"RFS" and not args.raw:
        out = out[0x30:]
    if int.from_bytes(out[:4], "little") in [3, 5, 7] and not args.raw:
        header = 0x1C08 * out[0xE]
        size = int.from_bytes(out[0x10:0x14], "little")
        fn = out[0x16:0x48].decode("utf-16-le").replace("\x00", "")
        with open(os.path.join(args.output, "%04d_%s" % (k, fn)), "wb") as file:
            file.write(out[0x68 + header : 0x68 + header + size])
    else:
        with open(os.path.join(args.output, "%04d" % k), "wb") as file:
            if args.limit_size:
                file.write(out[:maxsize])
            else:
                file.write(out)
