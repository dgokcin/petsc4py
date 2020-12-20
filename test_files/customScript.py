
import scipy.sparse as sparse
from scipy.io import mmread
import petsc4py
petsc4py.init()
from petsc4py import PETSc
import numpy as np

#matrix = mmread("bcsstk01.mtx")
#csr_matrix = sparse.csr_matrix(matrix)
#indices = csr_matrix.indices
#indptr = csr_matrix.indptr
#data = csr_matrix.data
#N = csr_matrix.shape[0]

np_matrix = np.matrix([[1,2,1,4],
              [2,0,4,3],
              [4,2,2,1],
              [-3,1,3,2]])
np_b= np.matrix([[13], [28], [20], [6]])

csr_matrix = sparse.csr_matrix(np_matrix)
indptr = csr_matrix.indptr
indices = csr_matrix.indices
data = csr_matrix.data
csr = (indptr, indices, data)
N = csr_matrix.shape[0]

# Create a PETSc matrix
A = PETSc.Mat().createAIJWithArrays(N, csr)
A.setUp()

A.assemblyBegin()
A.assemblyEnd()

print('Values of PETSc matrix:')
print(A.getValues(range(csr_matrix.shape[0]), range(csr_matrix.shape[1])))

# Create PETSc vectors
x, b = A.createVecs()

for i in range(np_b.shape[0]):
    b.setValue(i, np_b[i, 0])

print('Values of PETSc vector b:')
print(b.getValues(range(np_b.shape[0])))

# create an iterative solver and solve
ksp = PETSc.KSP()
ksp.create(PETSc.COMM_WORLD)
ksp.setOperators(A)
pc = ksp.getPC()
pc.setType('jacobi')
ksp.setTolerances(rtol=1.e-7)
ksp.solve(b, x)

print('The solution is:')
print(x.getValues(range(np_b.shape[0])))
