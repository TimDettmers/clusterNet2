from gpuir import library_interface as lib
import numpy as np
import ctypes as ct

class BatchAllocator(object):
	def __init__(self, X, y, batch_size):
		self.current_batch = 0
		self.epoch = 0
		self.batches = X.shape[0]/batch_size +1
		self.offsize = X.shape[0] - ((self.batches-1)*batch_size)
		self.offsize = self.offsize if self.offsize != 0 else batch_size
		self.pt = lib.funcs.fget_BatchAllocator(
					X.ctypes.data_as(ct.POINTER(ct.c_float)),
					y.ctypes.data_as(ct.POINTER(ct.c_float)),
					int(X.shape[0]), int(X.shape[1]), int(y.shape[1]),
					int(batch_size))
	
		self.offbatchX = array(None, lib.funcs.fgetOffBatchX(self.pt), (self.offsize, X.shape[1]))
		self.offbatchY = array(None, lib.funcs.fgetOffBatchY(self.pt), (self.offsize, y.shape[1]))
		
		self.batchX = array(None, lib.funcs.fgetBatchX(self.pt), (batch_size, X.shape[1]))
		self.batchY = array(None, lib.funcs.fgetBatchY(self.pt), (batch_size, y.shape[1]))
		
	def alloc_next_async(self): lib.funcs.falloc_next_batch(self.pt)
	def replace_current_with_next_batch(self): 
		self.current_batch +=1
		if self.current_batch == self.batches: 			
			self.current_batch = 0
			self.epoch += 1
		lib.funcs.freplace_current_with_next_batch(self.pt)
	
	@property
	def X(self):		
		if self.current_batch == 0 and self.epoch > 0: 
			return self.offbatchX
		else:
			pt =  lib.funcs.fgetBatchX(self.pt)
			self.batchX.pt = pt
			return self.batchX
		
	@property
	def Y(self):		
		if self.current_batch == 0 and self.epoch > 0: 
			return self.offbatchY
		else:
			pt =  lib.funcs.fgetBatchY(self.pt)
			self.batchY.pt = pt
			return self.batchY
	
		
		
		


class array(object):
	def __init__(self, numpy_array=None, pt=None, shape=None):
		if pt is not None: self.pt = pt
		if shape is not None: 
			self.shape = shape
			if self.shape[1] == 1:
				self.shape = (shape[0],)		
		if numpy_array is not None:
			if len(numpy_array.shape) > 2: raise Exception("Array must be one or two dimensional!")
			self.shape = numpy_array.shape
			if len(self.shape) == 1:
				self.pt = lib.funcs.fempty(numpy_array.shape[0], 1)
			else:
				self.pt = lib.funcs.fempty(numpy_array.shape[0], numpy_array.shape[1])
			lib.funcs.fto_gpu(numpy_array.ctypes.data_as(ct.POINTER(ct.c_float)), self.pt)
		
		self.cpu_arr = numpy_array
		


	def tocpu(self):
		if self.cpu_arr is None: self.cpu_arr = np.empty(self.shape, dtype=np.float32)
		lib.funcs.fto_host(self.pt,self.cpu_arr.ctypes.data_as(ct.POINTER(ct.c_float)))
		return self.cpu_arr
	
	@property
	def T(self): return array(None, self.fT(self.pt), self.shape[::-1])

	

	
def ones(shape, dtype=np.float32):
	rows, cols = handle_shape(shape)
	return array(None, lib.funcs.ffill_matrix(rows,cols,ct.c_float(1.0)), shape)

def empty(shape, dtype=np.float32):
	rows, cols = handle_shape(shape)
	return array(None, lib.funcs.fempty(rows,cols), shape)


def setRandomState(seed): lib.funcs.fsetRandomState(lib.pt_clusterNet, seed)
def rand(rows, cols, dtype=np.float32):	return array(None, lib.funcs.frand(lib.pt_clusterNet,rows,cols),(rows, cols))
def randn(rows, cols, dtype=np.float32): return array(None, lib.funcs.frandn(lib.pt_clusterNet,rows,cols),(rows, cols))


def handle_shape(shape):
	if len(shape) == 1: return (shape[0],1)
	elif len(shape) > 2: raise Exception("Array must be one or two dimensional!")
	else: return shape
	
def dot(A,B,out=None):
	if not out: out = empty((A.shape[0],B.shape[1]))
	lib.funcs.fdot(lib.pt_clusterNet, A.pt, B.pt, out.pt)
	return out


def abs(A, out=None):
	if not out: out = empty((A.shape[0],A.shape[1]))
	lib.funcs.ffabs(A.pt, out.pt)
	return out

def log(A, out=None):
	if not out: out = empty((A.shape[0],A.shape[1]))
	lib.funcs.flog(A.pt, out.pt)
	return out

def sqrt(A, out=None):
	if not out: out = empty((A.shape[0],A.shape[1]))
	lib.funcs.fsqrt(A.pt, out.pt)
	return out

def pow(A, power, out=None):
	if not out: out = empty((A.shape[0],A.shape[1]))
	lib.funcs.fpow(A.pt, out.pt, ct.c_float(power))
	return out

def logistic(A, out=None):
	if not out: out = empty((A.shape[0],A.shape[1]))
	lib.funcs.flogistic(A.pt, out.pt)
	return out

def rectified_linear(A, out=None):
	if not out: out = empty((A.shape[0],A.shape[1]))
	lib.funcs.frectified(A.pt, out.pt)
	return out

def logistic_grad(A, out=None):
	if not out: out = empty((A.shape[0],A.shape[1]))
	lib.funcs.flogistic_grad(A.pt, out.pt)
	return out

def rectified_linear_grad(A, out=None):
	if not out: out = empty((A.shape[0],A.shape[1]))
	lib.funcs.frectified_grad(A.pt, out.pt)
	return out

def copy(A, out=None):
	if not out: out = empty((A.shape[0],A.shape[1]))
	lib.funcs.fcopy(A.pt, out.pt)
	return out

def add(A, B, out=None):
	if not out: out = empty((A.shape[0],A.shape[1]))
	lib.funcs.fadd(A.pt, B.pt, out.pt)
	return out

def sub(A, B, out=None):
	if not out: out = empty((A.shape[0],A.shape[1]))
	lib.funcs.fsub(A.pt, B.pt, out.pt)
	return out

def div(A, B, out=None):
	if not out: out = empty((A.shape[0],A.shape[1]))
	lib.funcs.fdiv(A.pt, B.pt, out.pt)
	return out

def mul(A, B, out=None):
	if not out: out = empty((A.shape[0],A.shape[1]))
	lib.funcs.fmul(A.pt, B.pt, out.pt)
	return out

def equal(A, B, out=None):
	if not out: out = empty((A.shape[0],A.shape[1]))
	lib.funcs.feq(A.pt, B.pt, out.pt)
	return out

def less(A, B, out=None):
	if not out: out = empty((A.shape[0],A.shape[1]))
	lib.funcs.flt(A.pt, B.pt, out.pt)
	return out

def greater(A, B, out=None):
	if not out: out = empty((A.shape[0],A.shape[1]))
	lib.funcs.fgt(A.pt, B.pt, out.pt)
	return out

def less_equal(A, B, out=None):
	if not out: out = empty((A.shape[0],A.shape[1]))
	lib.funcs.fle(A.pt, B.pt, out.pt)
	return out

def greater_equal(A, B, out=None):
	if not out: out = empty((A.shape[0],A.shape[1]))
	lib.funcs.fge(A.pt, B.pt, out.pt)
	return out

def not_equal(A, B, out=None):
	if not out: out = empty((A.shape[0],A.shape[1]))
	lib.funcs.fne(A.pt, B.pt, out.pt)
	return out

def squared_difference(A, B, out=None):
	if not out: out = empty((A.shape[0],A.shape[1]))
	lib.funcs.fsquared_diff(A.pt, B.pt, out.pt)
	return out

def vector_add(A, v, out=None):	
	if not out: out = empty((A.shape[0],A.shape[1]))
	lib.funcs.fvadd(A.pt, v.pt, out.pt)
	return out

def create_t_matrix(v, max_value, out=None):		
	if not out: out = empty((v.shape[0],max_value+1))
	lib.funcs.ftmatrix(out.pt, v.pt, out.pt)
	return out

def slice(A, rstart, rend, cstart, cend, out=None):
	if not out: out = empty((rend-rstart,cend-cstart))
	lib.funcs.fslice(A.pt, out.pt, rstart, rend, cstart, cend)
	return out

def softmax(A, out=None):
	if not out: out = empty((A.shape[0],A.shape[1]))
	lib.funcs.fsoftmax(A.pt, out.pt)
	return out

def argmax(A, out=None):
	if not out: out = empty((A.shape[0],1))
	lib.funcs.fargmax(A.pt, out.pt)
	return out

def to_pinned(X):
	pt = lib.funcs.fto_pinned(X.shape[0], X.shape[1],
						X.ctypes.data_as(ct.POINTER(ct.c_float)))
	buffer = np.core.multiarray.int_asbuffer(ct.addressof(pt.contents), 4*X.size)
	return np.frombuffer(buffer, np.float32).reshape(X.shape)

def row_sum(A, out=None):
	if not out: out = empty((A.shape[0],1))
	lib.funcs.frowSum(A.pt, out.pt)
	return out

def row_max(A, out=None):
	if not out: out = empty((A.shape[0],1))
	lib.funcs.frowMax(A.pt, out.pt)
	return out

def max(A): return lib.funcs.ffmax(A.pt)
def sum(A): return lib.funcs.ffsum(A.pt)