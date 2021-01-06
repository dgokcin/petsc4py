while read -r matrix
do
    path=$(echo ${matrix} | awk -F'/' '{print $1"/"$2"/";}')
    name=$(echo ${matrix} | awk -F'/' '{print $3;}')
    tar xvzf ${matrix}.tar.gz -C ${path}

    for np in 4
    #for np in 1 2 4
    do
        for ksp in cg gmres
        do
            for pc in bjacobi
            do
                mpirun -np ${np} python3 parallel_solver.py -m ${matrix} -k ${ksp} -a 1e-5 -p ${pc}
            done
        done
    done
    rm -rf ${path}${name}/
done < $1

