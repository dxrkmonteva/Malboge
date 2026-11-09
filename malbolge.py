import sys

MOD = 59049
ENC = "5z]&gqtyfr$(we4{WP)H-Zn,[%\\3dL+Q;>U!pJS72FhOA1CB6v^=I_0/8|jsb9m<.TVac`uY*MK'X~xDl}REokN:#?G\"i@"
assert len(ENC) == 94
OPC = {'j': 40, 'i': 4, '*': 39, 'p': 62, '<': 5, '/': 23, 'v': 81, 'o': 68}

# crazy operation table: CRZ[b_trit][a_trit]
CRZ = [[1, 0, 0], [1, 0, 2], [2, 2, 1]]


def crazy(a, b):
    r, p = 0, 1
    for _ in range(10):
        r += CRZ[b % 3][a % 3] * p
        a //= 3
        b //= 3
        p *= 3
    return r


def rotr(x):
    return x // 3 + (x % 3) * 19683


def load(src):
    mem = [0] * MOD
    n = 0
    for ch in src:
        if ch.isspace():
            continue
        o = ord(ch)
        if not (33 <= o <= 126):
            raise ValueError("bad char")
        if (o + n) % 94 not in (4, 5, 23, 39, 40, 62, 68, 81):
            raise ValueError("invalid instruction at %d" % n)
        mem[n] = o
        n += 1
    for i in range(n, MOD):
        mem[i] = crazy(mem[i - 1], mem[i - 2])
    return mem


def run(src, limit=5_000_000):
    mem = load(src)
    a = c = d = 0
    out = []
    steps = 0
    while steps < limit:
        steps += 1
        if not (33 <= mem[c] <= 126):
            break
        op = (mem[c] + c) % 94
        if op == 40:
            d = mem[d]
        elif op == 4:
            c = mem[d]
        elif op == 39:
            a = mem[d] = rotr(mem[d])
        elif op == 62:
            a = mem[d] = crazy(a, mem[d])
        elif op == 5:
            out.append(chr(a % 256))
        elif op == 23:
            a = 0
        elif op == 81:
            break
        if 33 <= mem[c] <= 126:
            mem[c] = ord(ENC[mem[c] - 33])
        c = (c + 1) % MOD
        d = (d + 1) % MOD
    return "".join(out)


def src_char(op, i):
    """source char that decodes to opcode `op` at position i"""
    return 33 + ((OPC[op] - i - 33) % 94)


def generate(phrase, max_len=20000):
    """Search for a linear (loop-free) program. D stays equal to C, so the data
    cell read by * and p at position i is just the source char s_i itself."""
    prog = []
    A = 0
    i = 0
    for t in phrase:
        t = ord(t)
        frontier = {A: None}
        layers = []
        found = None
        while found is None:
            if i + len(layers) > max_len:
                raise RuntimeError("too long")
            pos = i + len(layers)
            s = src_char('o', pos)  # raw source char value (same for all ops? no: depends on op)
            # source char depends on the op chosen, so compute per op
            nxt = {}
            # check print first
            for a in frontier:
                if a % 256 == t:
                    found = a
                    break
            layers.append(frontier)
            if found is not None:
                break
            for a in frontier:
                # nop
                if a not in nxt:
                    nxt[a] = (a, 'o')
                # rotate: A = rotr(s) where s = src char for '*'
                s_star = src_char('*', pos)
                r = rotr(s_star)
                if r not in nxt:
                    nxt[r] = (a, '*')
                s_p = src_char('p', pos)
                q = crazy(a, s_p)
                if q not in nxt:
                    nxt[q] = (a, 'p')
            # store transitions in layer for backtracking
            layers[-1] = (frontier, nxt)
            frontier = nxt
        # backtrack
        # layers: list of (frontier, nxt) except the last which is plain frontier
        ops = []
        cur = found
        for k in range(len(layers) - 2, -1, -1):
            _, nxt = layers[k]
            prev, op = nxt[cur]
            ops.append(op)
            cur = prev
        ops.reverse()
        for op in ops:
            prog.append(src_char(op, len(prog)))
        prog.append(src_char('<', len(prog)))
        A = found
        i = len(prog)
    prog.append(src_char('v', len(prog)))
    return "".join(chr(x) for x in prog)


if __name__ == "__main__":
    if sys.argv[1] == "run":
        print(repr(run(sys.argv[2])))
    else:
        p = generate(sys.argv[2])
        print(p)
        print(len(p), "chars")
        print("check:", repr(run(p)))
