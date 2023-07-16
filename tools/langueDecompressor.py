import zlib

while True:
    r1 = input()
    F = open(f"tfm-{r1}.gz", "rb")
    F1 = open(f"tfm-{r1}-decompressed.gz", "wb")
    F1.write(zlib.decompress(F.read()))
    F.close()
    F1.close()