import cluster_net as gpu
import nose
import numpy as np
import numpy.testing as t
import time
from scipy.spatial.distance import cdist
from cluster_net import NeuralNetwork
import time



def setup():
    pass

def teardown():
    pass

def test_cpu():  
    A = np.ones((5,7))
    B = gpu.ones((5,7))
    C = B.tocpu()
    t.assert_array_equal(A, C, "To GPU does not work!")  
    
    A = np.float32(np.random.rand(5,7))
    B = gpu.array(A)
    C = B.tocpu()
    t.assert_array_equal(A, C, "To GPU does not work!")  
   
def test_togpu():
    A = np.float32(np.random.rand(17,83))
    B = gpu.array(A)
    C = B.tocpu()
    t.assert_array_almost_equal(A,C,4,"array.tocpu not equal to init array!")   
    
    
def test_dot():
    A1 = np.float32(np.random.rand(2,4))
    A2 = np.float32(np.random.rand(4,2))
    B1 = gpu.array(A1)
    B2 = gpu.array(A2)
    B3 = gpu.dot(B1,B2)
    C = B3.tocpu()
    
    t.assert_array_almost_equal(np.dot(A1,A2),C,4,"array.tocpu not equal to init array!")     
    

def test_Transpose():
    A = np.float32(np.random.rand(17,83))    
    B = gpu.array(A.T)
    C = B.tocpu()    
    t.assert_array_equal(A.T,C,"Transpose error!")   
    
    A = np.float32(np.random.rand(100,1))    
    B = gpu.array(A.T)
    C = B.tocpu()    
    t.assert_array_equal(A.T,C,"Transpose error!")  
    
    A = np.float32(np.random.rand(1,100))    
    B = gpu.array(A.T)
    C = B.tocpu()    
    t.assert_array_equal(A.T,C,"Transpose error!")        
    

def test_rand():
    A = gpu.rand(100,100)
    B = A.tocpu()
    assert np.mean(B) > 0.45 and np.mean(B) < 0.55
    assert np.var(B) > 0.08 and np.var(B) < 0.085
    
    gpu.setRandomState(1234)
    A1 = gpu.rand(1000,1000)
    gpu.setRandomState(1234)
    A2 = gpu.rand(1000,1000)
    B1 = A1.tocpu()
    B2 = A2.tocpu()
    
    t.assert_array_equal(B1, B2, "Seed not working!")
    
  
def test_randn():
    A = gpu.randn(100,100)
    B = A.tocpu()
    assert np.mean(B) > -0.05 and np.mean(B) < 0.05
    assert np.var(B) > 0.95 and np.var(B) < 1.05
    
    gpu.setRandomState(1234)
    A1 = gpu.randn(1000,1000)
    gpu.setRandomState(1234)
    A2 = gpu.randn(1000,1000)
    B1 = A1.tocpu()
    B2 = A2.tocpu()
    
    t.assert_array_equal(B1, B2, "Seed not working!")  
     
def test_elementwise():
    A1 = np.float32(np.random.randn(100,100))
    A2 = np.float32(np.random.randn(100,100))    
    B1 = gpu.array(A1)
    B2 = gpu.array(A2)
    
    t.assert_almost_equal(gpu.abs(B1).tocpu(), np.abs(A1), 3, "Abs not working")
    t.assert_almost_equal(gpu.log(B1).tocpu(), np.log(A1), 3, "Log not working")
    t.assert_almost_equal(gpu.sqrt(B1).tocpu(), np.sqrt(A1), 3, "Sqrt not working")
    t.assert_almost_equal(gpu.pow(B1,2.0).tocpu(), np.power(A1,2.0), 3, "Pow not working")
    t.assert_almost_equal(gpu.logistic(B1).tocpu(), 1.0/(1.0+np.exp(A1)), 3, "Logistic not working")
    t.assert_almost_equal(gpu.logistic_grad(B1).tocpu(), A1*(A1-1.0), 3, "Logistic grad not working")
    t.assert_almost_equal(gpu.rectified_linear(B1).tocpu(), A1*(A1>0), 3, "Rectified not working")
    t.assert_almost_equal(gpu.rectified_linear_grad(B1).tocpu(), (A1>0), 3, "Rectified grad not working")
    
    t.assert_almost_equal(gpu.add(B1,B2).tocpu(), A1+A2, 3, "Add not working")
    t.assert_almost_equal(gpu.sub(B1,B2).tocpu(), A1-A2, 3, "Sub not working")
    t.assert_almost_equal(gpu.mul(B1,B2).tocpu(), A1*A2, 3, "Mul not working")
    t.assert_almost_equal(gpu.div(B1,B2).tocpu(), A1/A2, 3, "Div not working")
    
    t.assert_almost_equal(gpu.equal(B1,B2).tocpu(), np.equal(A1,A2), 3, "Equal not working")
    t.assert_almost_equal(gpu.less(B1,B2).tocpu(), np.less(A1,A2), 3, "Less not working")
    t.assert_almost_equal(gpu.greater(B1,B2).tocpu(), np.greater(A1,A2), 3, "Greater not working")
    t.assert_almost_equal(gpu.greater_equal(B1,B2).tocpu(), np.greater_equal(A1,A2), 3, "Greater equal not working")
    t.assert_almost_equal(gpu.less_equal(B1,B2).tocpu(), np.less_equal(A1,A2), 3, "Less equal not working")
    t.assert_almost_equal(gpu.not_equal(B1,B2).tocpu(), np.not_equal(A1,A2), 3, "Not equal not working")
    t.assert_almost_equal(gpu.squared_difference(B1,B2).tocpu(), (A1-A2)**2, 3, "Squared difference not working")
    
    t.assert_almost_equal(gpu.copy(B1).tocpu(), A1.copy(), 3, "Squared difference not working")


    
def test_vectorwise(): 
    def create_t_matrix(y, classes):        
        t = np.zeros((y.shape[0], classes+1))
        for i in range(y.shape[0]):
            t[np.int32(i), np.int32(y[i])] = 1.0
           
        return t
    
    A = np.float32(np.random.randn(100,100))
    v = np.float32(np.random.randn(100,1))    
    
    labels = np.float32(np.random.randint(0,10,100))
    B = gpu.array(A)
    V = gpu.array(v)
    Y = gpu.array(labels)
    
    t.assert_almost_equal(gpu.vector_add(B, V).tocpu(), A+v, 3, "Vec add not working")
    t.assert_almost_equal(gpu.create_t_matrix(Y, 9).tocpu(), create_t_matrix(labels,9), 3, "Tmatrix not working")

def slice_test():
    A = np.float32(np.random.randn(100,100))
    B = gpu.array(A)
    C = gpu.slice(B,17,83,7,23).tocpu()
    print A
    
    t.assert_almost_equal(C, A[17:83,7:23], 3, "Slicing not working")
    
    
def softmax_test():   
    def softmax(X):
        '''numerically stable softmax function
        '''
        max_row_values = np.matrix(np.max(X,axis=1)).T
        result = np.exp(X - max_row_values)
        sums = np.matrix(np.sum(result,axis=1))        
        return result/sums
    
    A = np.float32(np.random.randn(17,83))
    B = gpu.array(A)
    C = gpu.softmax(B).tocpu()
    
    t.assert_almost_equal(C, softmax(A), 3, "Softmax not working")
    
def argmax_test():       
    A = np.float32(np.random.randn(123,83))
    B = gpu.array(A)
    C = gpu.argmax(B).tocpu()
    
    t.assert_almost_equal(C, np.argmax(A,1), 3, "Softmax not working")
    
    
def test_to_pinned():
    A = np.float32(np.random.rand(10,10))
    B = gpu.to_pinned(A)
    
    t.assert_almost_equal(A,B , 3, "Pinned not working")
    

    
def test_batch_allocator():
    X = np.float32(np.random.rand(1000,17))
    Y = np.float32(np.random.rand(1000,13))
    batch_size = 128
        
    alloc = gpu.BatchAllocator(X,Y,batch_size)  
    
    
    alloc.alloc_next_async()   
    for i in range(3):  
        for i in range(0,1000,batch_size):
            batchX = X[i:i+batch_size]
            batchY = Y[i:i+batch_size]
            
            if batchX.shape[0] != batch_size:
                batchX = np.vstack([batchX, np.zeros((batch_size-batchX.shape[0],batchX.shape[1]),dtype=np.float32)])
                batchY = np.vstack([batchY, np.zeros((batch_size-batchY.shape[0],batchY.shape[1]),dtype=np.float32)])
                    
            alloc.replace_current_with_next_batch()
            t.assert_almost_equal(alloc.X.tocpu(),batchX , 3, "Batch allocator not working")  
            t.assert_almost_equal(alloc.Y.tocpu(),batchY , 3, "Batch allocator not working")        
            alloc.alloc_next_async()   
          
    
def test_row_reductions():
    A = np.float32(np.random.randn(100,100))
    B = gpu.array(A)
    
    C = gpu.row_sum(B).tocpu()    
    t.assert_almost_equal(C, np.sum(A,1), 3, "Rowsum not working")
    
    C = gpu.row_max(B).tocpu()    
    t.assert_almost_equal(C, np.max(A,1), 3, "Rowmax not working")
    
def test_matrix_reductions():
    A = np.float32(np.random.randn(100,100))
    B = gpu.array(A)
    
    C = gpu.sum(B)    
    t.assert_almost_equal(C, np.sum(A), 2, "Sum not working")
    C = gpu.max(B)    
    t.assert_almost_equal(C, np.max(A), 3, "Max not working")


    
def test_timer():
    t = gpu.Timer()
    A = gpu.rand(100,100)
    B = gpu.rand(100,100)
    C = gpu.rand(100,100)
    time = 0
    
    t.tick()
    for i in range(10):
        gpu.dot(A,B,C)    
    time = t.tock()
    print time
    assert time > 0
    
    time = 0
    t.tick("Timer test")
    gpu.dot(A,B,C)    
    time = t.tock("Timer test")
    assert time > 0
    
    accumulative_time = 0
    for i in range(100):
        t.tick('cumulative')
        gpu.dot(A,B,C)
        t.tick('cumulative')
    accumulative_time = t.tock('cumulative')
    
    assert accumulative_time > 5*time
    
def test_free():
    #needs at least 3GB ram
    dim = 1
    for i in range(14):
        dim*=2
        print dim
        A = gpu.rand(dim,dim)
        B = gpu.rand(dim,dim)
        C = gpu.rand(dim,dim)
        gpu.dot(A,B,C)
        del A, B, C
         

        
def test_euclidean_distance():
    x = np.float32(np.random.rand(100,10))
    
    t.assert_equal(x.T,np.transpose(x))
    rows = x.shape[1]
    dim = x.shape[0]
    X = gpu.array(x)
    x = x.T
    vec = gpu.empty((dim,1))
    buffer = gpu.empty((dim,rows))
    bufferT = gpu.empty((rows,dim))
    distances = gpu.empty((rows,1))
    
    dist = cdist(x,x,'euclidean')
    for i in range(X.shape[1]):
        gpu.slice(X, 0, dim, i, i+1, vec)
                        
        gpu.vector_sub(X, vec, buffer)
                
        gpu.pow(buffer, 2.0, buffer)
        
        gpu.transpose(buffer, bufferT)
        gpu.row_sum(bufferT, distances)
        
        gpu.sqrt(distances, distances)
        
        t.assert_allclose(np.sqrt(np.sum((x-x[i])**2,1)), distances.tocpu(), rtol=0.01) 
        t.assert_allclose(np.sqrt(np.sum((x-x[i])**2,1)), dist[i], rtol=0.01) 
    
    
def test_get_closest_index():
    X = np.float32(np.random.rand(10,100))
    results_gpu = gpu.get_closest_index(X,5)
    
    dist = cdist(X,X,'euclidean')
    results = []
    for i in range(10):
        results.append(np.argsort(dist[i,:])[::-1][0:5])
        
    
    
    
    t.assert_equal(np.array(results), results_gpu)
    
    
def test_neural_net():
    X = np.float32(np.load('train_small_X.npy'))
    y = np.float32(np.load('train_small_y.npy'))  
    t0 = time.time()
    X = np.float32(np.load('/home/tim/data/mnist/train_X.npy'))
    y = np.float32(np.load('/home/tim/data/mnist/train_y.npy')) 
    net = NeuralNetwork(X, y)
    
    net.fit()
    print time.time()-t0
    #assert False