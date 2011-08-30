import pyopencl as cl
import numpy
import numpy.linalg as la
import profile

N = 5000000

a = numpy.random.rand(N).astype(numpy.float32)
b = numpy.random.rand(N).astype(numpy.float32)

ctx = cl.create_some_context()
queue = cl.CommandQueue(ctx)

prg = cl.Program(ctx, """
    __kernel void sum(__global const float *a,
    __global const float *b, __global float *c)
    {
      int gid = get_global_id(0);
      c[gid] = a[gid] + b[gid];
      c[gid] *= a[gid];
      c[gid] *= b[gid];
      c[gid] = c[gid] * c[gid];
    }
    """).build()

a_plus_b = numpy.empty_like(a)

def compute():

    mf = cl.mem_flags
    a_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=a)
    b_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=b)
    dest_buf = cl.Buffer(ctx, mf.WRITE_ONLY, b.nbytes)

    prg.sum(queue, a.shape, None, a_buf, b_buf, dest_buf)

    cl.enqueue_copy(queue, a_plus_b, dest_buf)

profile.run('compute()')

print la.norm(a_plus_b - (a+b))

