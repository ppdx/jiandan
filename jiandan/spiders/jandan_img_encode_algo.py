import base64
import hashlib


def md5(s):
    return hashlib.md5(s.encode()).hexdigest()


def f_Z9t5X3ALWh4mAgpORRQOTGQSGoMbGlKG(m, r="", d=0):
    r = md5(r)
    o = md5(r[:16])
    c = o + md5(o + m[:4])
    m = m[4:]
    k = base64.b64decode(m)

    h = list(range(256))
    b = [ord(c[i % len(c)]) for i in h]
    f = 0
    for g in range(256):
        f = (f + h[g] + b[g]) % 256
        h[g], h[f] = h[f], h[g]

    t = ""
    p = 0
    f = 0
    for g in range(len(k)):
        p = (p + 1) % 256
        f = (f + h[p]) % 256
        tmp = h[p]
        h[p] = h[f]
        h[f] = tmp
        t += chr(k[g] ^ (h[(h[p] + h[f]) % 256]))

    return t[26:]


def to_jandan_img_url(img_hash: str):
    return f_Z9t5X3ALWh4mAgpORRQOTGQSGoMbGlKG(
        img_hash,
        "adJPN6WGMi1h01QMPiCGNziZQuEGA0YL")
