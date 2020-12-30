import sys
import os
from datetime import datetime
import time
import socket
import argparse

from csv import writer

from scipy.io import mmread
import petsc4py

petsc4py.init()
from petsc4py import PETSc

log_file_name = 'log.csv'
'''
0: DATE
1: TIME
2: HOSTNAME
3: CORE_COUNT
4: RAM (GB)
5: MATRIX_NAME
6: ROWS
7: COLUMNS
8: ENTRIES
9: PROCESS_COUNT
10: KSP_TYPE
11: PRECONDITIONER_TYPE
12: NORM_2
13: ITERATION_COUNT
14: CONVERGENCE_STATUS
15: SOLUTION_TIME
16: RELATIVE_CONVERGENCE_TOLERANCE
17: ABSOLUTE_CONVERGENCE_TOLERANCE
18: DIVERGENCE_TOLERANCE
19: MAXIMUM_NUMBER_OF_ITERATIONS
'''
logged_column_headers = ["DATE", "TIME", "HOSTNAME", "CORE_COUNT", "RAM (GB)", "MATRIX_NAME", "ROWS", "COLUMNS",
                         "ENTRIES", "PROCESS_COUNT", "KSP_TYPE", "PRECONDITIONER_TYPE", "NORM_2", "ITERATION_COUNT",
                         "CONVERGENCE_STATUS", "SOLUTION_TIME", "RELATIVE_CONVERGENCE_TOLERANCE",
                         "ABSOLUTE_CONVERGENCE_TOLERANCE", "DIVERGENCE_TOLERANCE", "MAXIMUM_NUMBER_OF_ITERATIONS"]

def main(args):
    # create PETSc comm
    comm = PETSc.COMM_WORLD
    size = comm.getSize()  # PROCESS_COUNT to be logged
    rank = comm.getRank()
    if 0 == rank:
        computation_data = [None] * len(logged_column_headers)
        computation_data[9] = size

    # Read Matrix
    matrix_name = args['matrix']
    if 0 == rank:
        computation_data[5] = matrix_name.split('.')[0]
    print("Process " + str(rank) + " Reading mtx file...")
    sys.stdout.flush()
    start = time.time()
    matrix = mmread(matrix_name)
    matrix = matrix.tocsr()
    end = time.time()
    print("Process " + str(rank) + " Done with reading file!")
    print("Process " + str(rank) + " Elapsed time: " + str(end - start) + " seconds")
    sys.stdout.flush()
    problem_size = matrix.shape[0]  # problem size to be logged
    if 0 == rank:
        computation_data[6] = matrix.shape[0]
        computation_data[7] = matrix.shape[1]
        computation_data[8] = matrix.nnz
    # create PETSc vectors
    x = PETSc.Vec().create(comm=comm)
    x.setSizes(problem_size)
    x.setFromOptions()

    u = x.duplicate()

    rstart, rend = x.getOwnershipRange()

    # Create PETSc matrix
    start = time.time()
    A = PETSc.Mat().createAIJWithArrays(problem_size, (matrix[rstart:rend, :].indptr, matrix[rstart:rend, :].indices,
                                                       matrix[rstart:rend, :].data), comm=comm)
    A.setUp()
    A.assemblyBegin()
    A.assemblyEnd()
    end = time.time()
    print("Process " + str(rank) + " Done with creating PETSc matrix!")
    print("Process " + str(rank) + " Elapsed time: " + str(end - start) + " seconds")
    sys.stdout.flush()

    # set PETSc vectors
    print("Process " + str(rank) + " Setting PETSc vectors...")
    sys.stdout.flush()
    start = time.time()
    u.set(1.0)
    b = A(u)
    end = time.time()
    print("Process " + str(rank) + " Done with setting PETSc vectors!")
    print("Process " + str(rank) + " Elapsed time: " + str(end - start) + " seconds")
    sys.stdout.flush()

    # create ksp solver and solve
    print("Process " + str(rank) + " Solving...")
    sys.stdout.flush()
    ksp = PETSc.KSP().create(comm=comm)  # Default is GMRES
    ksp.setOperators(A)
    pc = ksp.getPC()
    if args['pctype']:
        pc.setType(args['pctype'])
    else:
        pc.setType('jacobi')
    if 0 == rank:
        computation_data[11] = pc.getType()
    if args['rtol']:
        ksp.setTolerances(rtol=float(args['rtol']))
    if args['atol']:
        ksp.setTolerances(atol=float(args['atol']))
    if args['divtol']:
        ksp.setTolerances(divtol=float(args['divtol']))
    if args['max_it']:
        ksp.setTolerances(max_it=int(args['max_it']))
    ksp.setFromOptions()
    if args['ksptype']:
        ksp.setType(args['ksptype'])
    if 0 == rank:
        computation_data[10] = ksp.getType()
    begin_solution = time.time()
    ksp.solve(b, x)
    end_solution = time.time()
    sys.stdout.flush()
    if 0 == rank:
        computation_data[15] = end_solution - begin_solution

    # check the error
    x = x - u  # x.axpy(-1.0,u)
    norm = x.norm(PETSc.NormType.NORM_2)
    its = ksp.getIterationNumber()
    converged_reason = ksp.getConvergedReason()
    if 0 == rank:
        computation_data[12] = norm
        computation_data[13] = its
        computation_data[14] = converged_reason
        computation_data[16:20] = ksp.getTolerances()

    PETSc.Sys.Print("Norm of error {}, Iterations {}\n".format(norm, its), comm=comm)
    if size == 1:
        PETSc.Sys.Print("- Serial OK", comm=comm)
    else:
        PETSc.Sys.Print("- Parallel OK", comm=comm)
    if 0 == rank:
        now = datetime.now()
        computation_data[0] = now.strftime("%Y-%m-%d")
        computation_data[1] = now.strftime("%H:%M")
        computation_data[2] = socket.gethostname()
        computation_data[3] = os.cpu_count()
        mem_gib = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') / (1024. ** 3)
        computation_data[4] = "%0.2f" % mem_gib
        if not os.path.isfile(log_file_name):
            file_object = open(log_file_name, 'w')
            writer_object = writer(file_object)
            writer_object.writerow(logged_column_headers)
        else:
            file_object = open(log_file_name, 'a')
            writer_object = writer(file_object)
        writer_object.writerow(computation_data)
        file_object.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Sparse Matrix Logger')
    parser.add_argument('-m', '--matrix', help='Matrix file', required=True)
    parser.add_argument('-k', '--ksptype', help='Krylov method Type', required=False)
    parser.add_argument('-p', '--pctype', help='Preconditioner Type', required=False)
    parser.add_argument('-r', '--rtol', help='Relative convergence toleance', required=False)
    parser.add_argument('-a', '--atol', help='Absolute convergence toleance', required=False)
    parser.add_argument('-d', '--divtol', help='Divergence tolerance', required=False)
    parser.add_argument('-i', '--max_it', help='Maximum number of iterations', required=False)
    args = vars(parser.parse_args())
    main(args)
