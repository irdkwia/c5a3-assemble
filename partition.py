import argparse
import os

parser = argparse.ArgumentParser(description="Keitai C5A3 Partition")
parser.add_argument("input")
parser.add_argument("output")
parser.add_argument(
    "-s",
    "--size",
    help="Chunk size.",
    default=0x20000,
    type=int,
)
parser.add_argument(
    "-x",
    "--truncate-start",
    help="Truncate 0x3F4 bytes at the start of each chunk.",
    action=argparse.BooleanOptionalAction,
)
parser.add_argument(
    "-y",
    "--truncate-end",
    help="Truncate 0x3F4 bytes at the end of each chunk. Doesn't do anything if --truncate-start is activated",
    action=argparse.BooleanOptionalAction,
)

args = parser.parse_args()
os.makedirs(args.output, exist_ok=True)

with open(args.input, "rb") as file:
    blocks = {}
    data = file.read(args.size)
    addr = 0
    while len(data) > 0:
        match = 0
        search = 0
        if int.from_bytes(data[4:6], "little") == 0xC5A3:
            uid = int.from_bytes(data[8:10], "little")
            blocks[uid] = blocks.get(uid, {})
            exid = int.from_bytes(data[10:12], "little")
            if exid != 0xFFFF:
                blocks[uid][exid] = blocks[uid].get(exid, [0x10000, b""])
                current = int.from_bytes(data[:2], "little")
                if current < blocks[uid][exid][0]:
                    blocks[uid][exid][0] = current
                    blocks[uid][exid][1] = data[12:]
                    if args.truncate_start:
                        blocks[uid][exid][1] = blocks[uid][exid][1][0x400 - 12 :]
                    elif args.truncate_end:
                        blocks[uid][exid][1] = blocks[uid][exid][1][: -(0x400 - 12)]
        data = file.read(args.size)
        addr += args.size

for k, v in blocks.items():
    with open(os.path.join(args.output, "partition_%04d" % k), "wb") as file:
        for i in range(max(v) + 1):
            if i in v:
                file.write(v[i][1])
            else:
                print("WARNING! Chunk not found (%d, %d)" % (k, i))
                file.write(
                    bytes(
                        args.size
                        - (0x400 if args.truncate_start or args.truncate_end else 0xC)
                    )
                )
