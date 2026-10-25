# c5a3_assemble
Extract data from keitai dumps with C5A3 FTL

Phones all have different chunk sizes and width, here are listed all options to specify for each model:

- 705p: `-s 1 -w 1`
- 810p: `-s 1 -w 2`
- 820p: `-s 1 -w 2`
- 822p: `-s 1 -w 2`
- 830p: `-s 1 -w 2`
- 831p: `-s 1 -w 2`
- 840p: `-s 2 -w 2`
- 841p: `-s 2 -w 2`
- 002p: `-s 2 -w 2`

## Configuration
Use the `-c` / `--config` option to automatically set the chunk size and block ID width for a supported phone model.

For a list of available configurations, see the help message:
- `python extract_p.py -h`