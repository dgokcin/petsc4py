import sys
import os
from datetime import datetime
import time
import socket
import argparse
import json

from csv import writer

from scipy.io import mmread
import petsc4py

petsc4py.init()
from petsc4py import PETSc

log_file_name = 'experiment_log.csv'
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
20: BANDWIDTH
21: SPARSITY
22: KIND
23: NUMBER_OF_EXPLICIT_ZEROS
24: NUMBER_OF_STRONGLY_CONNECTED_COMPONENTS
25: NUMBER_DMPERM_BLOCKS
26: STRUCTURAL_FULL_RANK
27: STRUCTURAL_RANK
28: PATTERN_SYMMETRY
29: NUMERIC_SYMMTERY
30: RB_TYPE
31: STRUCTURE
32: CHOLESKY_CANDIDATE
33: POSITIVE_DEFINITE
34: NORM
35: MINIMUM_SINGULAR_VALUE
36: CONDITION_NUMBER
37: SVD_RANK
38: SPRANK_MINUS_RANK
39: NULL_SPACE_DIMENSION
40: FULL_NUMERICAL_LENGTH
41: PROBLEM_2D_OR_3D
'''
logged_column_headers = ["DATE", "TIME", "HOSTNAME", "CORE_COUNT", "RAM (GB)", "MATRIX_NAME", "ROWS", "COLUMNS",
                         "ENTRIES", "PROCESS_COUNT", "KSP_TYPE", "PRECONDITIONER_TYPE", "NORM_2", "ITERATION_COUNT",
                         "CONVERGENCE_STATUS", "SOLUTION_TIME", "RELATIVE_CONVERGENCE_TOLERANCE",
                         "ABSOLUTE_CONVERGENCE_TOLERANCE", "DIVERGENCE_TOLERANCE", "MAXIMUM_NUMBER_OF_ITERATIONS",
                         "BANDWIDTH", "SPARSITY", "KIND", "NUMBER_OF_EXPLICIT_ZEROS",
                         "NUMBER_OF_STRONGLY_CONNECTED_COMPONENTS", "NUMBER_DMPERM_BLOCKS", "STRUCTURAL_FULL_RANK",
                         "STRUCTURAL_RANK", "PATTERN_SYMMETRY", "NUMERIC_SYMMETRY", "RB_TYPE", "STRUCTURE",
                         "CHOLESKY_CANDIDATE", "POSITIVE_DEFINITE", "NORM", "MINIMUM_SINGULAR_VALUE",
                         "CONDITION_NUMBER", "SVD_RANK", "SPRANK_MINUS_RANK", "NULL_SPACE_DIMENSION",
                         "FULL_NUMERICAL_LENGTH", "PROBLEM_2D_OR_3D"]


def main(command_line_arguments):
    # create PETSc comm
    comm = PETSc.COMM_WORLD
    size = comm.getSize()  # PROCESS_COUNT to be logged
    rank = comm.getRank()
    if 0 == rank:
        computation_data = [''] * len(logged_column_headers)
        computation_data[9] = size

    matrix_metadata_file = command_line_arguments['matrix'] + ".json"

    # Read Matrix File
    with open(matrix_metadata_file, 'r') as json_file:
        metadata = json.load(json_file)
    if 0 == rank:
        try:
            computation_data[5] = metadata['name']
        except KeyError:
            print("MISSING METADATA: no name in json file")

    print("Process " + str(rank) + " Reading mtx file...")
    sys.stdout.flush()
    start = time.time()
    if 0 == rank:
        try:
            computation_data[20] = metadata['bandwidth']
        except KeyError:
            print("MISSING METADATA: no bandwidth in json file")
        try:
            computation_data[21] = metadata['sparsity']
        except KeyError:
            print("MISSING METADATA: no sparsity in json file")
        try:
            computation_data[22] = metadata['kind']
        except KeyError:
            print("MISSING METADATA: no kind in json file")
        try:
            computation_data[23] = metadata['num_explicit_zeros']
        except KeyError:
            print("MISSING METADATA: no num_explicit_zeros in json file")
        try:
            computation_data[24] = metadata['num_strongly_connected_components']
        except KeyError:
            print("MISSING METADATA: no num_strongly_connected_components in json file")
        try:
            computation_data[25] = metadata['num_dmperm_blocks']
        except KeyError:
            print("MISSING METADATA: no num_dmperm_blocks in json file")
        try:
            computation_data[26] = metadata['structural_full_rank']
        except KeyError:
            print("MISSING METADATA: no structural_full_rank in json file")
        try:
            computation_data[27] = metadata['structural_rank']
        except KeyError:
            print("MISSING METADATA: no structural_rank in json file")
        try:
            computation_data[28] = metadata['pattern_symmetry']
        except KeyError:
            print("MISSING METADATA: no pattern_symmetry in json file")
        try:
            computation_data[29] = metadata['numeric_symmetry']
        except KeyError:
            print("MISSING METADATA: no numeric_symmetry in json file")
        try:
            computation_data[30] = metadata['rb_type']
        except KeyError:
            print("MISSING METADATA: no rb_type in json file")
        try:
            computation_data[31] = metadata['structure']
        except KeyError:
            print("MISSING METADATA: no structure in json file")
        try:
            computation_data[32] = metadata['cholesky_candidate']
        except KeyError:
            print("MISSING METADATA: no cholesky_candidate in json file")
        try:
            computation_data[33] = metadata['positive_definite']
        except KeyError:
            print("MISSING METADATA: no positive_definite in json file")
        try:
            computation_data[34] = metadata['norm']
        except KeyError:
            print("MISSING METADATA: no norm in json file")
        try:
            computation_data[35] = metadata['min_singular_value']
        except KeyError:
            print("MISSING METADATA: no min_singular_value in json file")
        try:
            computation_data[36] = metadata['condition_number']
        except KeyError:
            print("MISSING METADATA: no condition_number in json file")
        try:
            computation_data[37] = metadata['svd_rank']
        except KeyError:
            print("MISSING METADATA: no svd_rank in json file")
        try:
            computation_data[38] = metadata['sprank_minus_rank']
        except KeyError:
            print("MISSING METADATA: no sprank_minus_rank in json file")
        try:
            computation_data[39] = metadata['null_space_dimension']
        except KeyError:
            print("MISSING METADATA: no null_space_dimension in json file")
        try:
            computation_data[40] = metadata['full_numerical_rank']
        except KeyError:
            print("MISSING METADATA: no full_numerical_rank in json file")
        try:
            computation_data[41] = metadata['problem_2D_or_3D']
        except KeyError:
            print("MISSING METADATA: no problem_2D_or_3D in json file")
    matrix_file = './' + metadata['group'] + '/' + metadata['name'] + '/' + metadata['name'] + '.mtx'
    matrix = mmread(matrix_file)
    matrix = matrix.tocsr()
    end = time.time()
    print("Process " + str(rank) + " Done with reading file!")
    print("Process " + str(rank) + " Elapsed time: " + str(end - start) + " seconds")
    sys.stdout.flush()
    problem_size = matrix.shape[0]  # problem size to be logged
    if 0 == rank:
        computation_data[6] = metadata['num_rows']
        computation_data[7] = metadata['num_cols']
        computation_data[8] = metadata['nonzeros']
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
    if command_line_arguments['pctype']:
        pc.setType(command_line_arguments['pctype'])
    else:
        pc.setType('jacobi')
    if 0 == rank:
        computation_data[11] = pc.getType()
    if command_line_arguments['rtol']:
        ksp.setTolerances(rtol=float(command_line_arguments['rtol']))
    if command_line_arguments['atol']:
        ksp.setTolerances(atol=float(command_line_arguments['atol']))
    if command_line_arguments['divtol']:
        ksp.setTolerances(divtol=float(command_line_arguments['divtol']))
    if command_line_arguments['max_it']:
        ksp.setTolerances(max_it=int(command_line_arguments['max_it']))
    ksp.setFromOptions()
    if command_line_arguments['ksptype']:
        ksp.setType(command_line_arguments['ksptype'])
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
    parser.add_argument('-m', '--matrix', help='Matrix file (JSON)', required=True)
    parser.add_argument('-k', '--ksptype', help='Krylov method Type', required=False)
    parser.add_argument('-p', '--pctype', help='Preconditioner Type', required=False)
    parser.add_argument('-r', '--rtol', help='Relative convergence toleance', required=False)
    parser.add_argument('-a', '--atol', help='Absolute convergence toleance', required=False)
    parser.add_argument('-d', '--divtol', help='Divergence tolerance', required=False)
    parser.add_argument('-i', '--max_it', help='Maximum number of iterations', required=False)
    args = vars(parser.parse_args())
    main(args)
