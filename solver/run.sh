for mtx in *.mtx
do
    for i in 1 2 3 4;
    do
        mpirun -np ${i} python3 parallel_solver.py -m ${mtx} -k cg -p bjacobi -r 1e-07 -a 1e-40 -d 9000 -i 10050
    done
done

