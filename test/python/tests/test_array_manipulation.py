import util


class test_flatten:
    def init(self):
        for cmd, shape in util.gen_random_arrays("R", 4, min_ndim=2, dtype="np.float32"):
            cmd = "R = bh.random.RandomState(42); a = %s; " % cmd
            yield cmd

    def test_flatten(self, cmd):
        cmd += "res = bh.flatten(a)"
        return cmd

    def test_flatten_self(self, cmd):
        cmd += "res = a.flatten()"
        return cmd

    def test_ravel(self, cmd):
        cmd += "res = a.ravel()"
        return cmd


class test_diagonal:
    def init(self):
        for cmd, shape in util.gen_random_arrays("R", 4, min_ndim=2, dtype="np.float32"):
            cmd = "R = bh.random.RandomState(42); a = %s; " % cmd
            for offset in range(-min(shape)+1, min(shape)):
                yield (cmd, offset)

    def test_diagonal(self, (cmd, offset)):
        cmd += "res = M.diagonal(a, offset=%d)" % offset
        return cmd


class test_diagonal_axis:
    def init(self):
        for cmd, shape in util.gen_random_arrays("R", 4, min_ndim=2, dtype="np.float32"):
            cmd = "R = bh.random.RandomState(42); a = %s; " % cmd
            for offset in range(-min(shape) + 1, min(shape)):
                for axis1 in range(len(shape)):
                    for axis2 in range(len(shape)):
                        if axis1 == axis2:
                            continue
                        yield (cmd, offset, axis1, axis2)

    def test_diagonal(self, (cmd, offset, axis1, axis2)):
        cmd += "res = M.diagonal(a, offset=%d, axis1=%d, axis2=%d)" % (offset, axis1, axis2)
        return cmd


class test_transpose:
    def init(self):
        for cmd, shape in util.gen_random_arrays("R", 4, min_ndim=2, dtype="np.float32"):
            cmd = "R = bh.random.RandomState(42); a = %s; " % cmd
            yield cmd

    def test_transpose(self, cmd):
        cmd += "res = bh.transpose(a)"
        return cmd

    def test_doubletranspose(self, cmd):
        cmd += "res = a.T + a.T"
        return cmd


class test_overlapping:
    def init(self):
        cmd = "R = bh.random.RandomState(42); res = R.random(100, np.float32, bohrium=BH); "
        yield cmd

    def test_identity(self, cmd):
        cmd += "res[1:] = res[:-1]"
        return cmd

    def test_add(self, cmd):
        cmd_np = cmd + "t = np.add(res[:-1], 42); res[1:] = t"
        cmd_bh = cmd + "bh.add(res[:-1], 42, res[1:])"
        return cmd_np, cmd_bh

