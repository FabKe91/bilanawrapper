import os

def write_submitfile(submitout, jobname, ncores=2, mem='4G', prio=False, queue=None):
    username = os.environ['LOGNAME']
    hostname = os.uname()[1]
    if hostname == "login" or "kaa" in hostname: # bagheera main node host name
        if not prio:
            queue = 'short'
        else:
            queue = 'prio'
        with open(submitout, "w") as sfile:
            print('#!/bin/bash'
                  '\n#SBATCH -A q0heuer'
                  '\n#SBATCH -p {queue}'
                  '\n#SBATCH --output={jobname}.out'
                  '\n#SBATCH --mail-type=fail'
                  '\n#SBATCH --mail-user={username}@wwu.de'
                  '\n#SBATCH --exclude=kaa-[72,73,76,77,78,82,12,13]'
                  '\n#SBATCH --constraint="avx|avx2|fma4"'
                  '\n#SBATCH --time=48:00:00'
                  '\n#SBATCH --ntasks=1'
                  '\n#SBATCH --nodes=1'
                  '\n#SBATCH --cpus-per-task={ncores}'
                  '\n#SBATCH --mem={mem}'
                  '\nexport OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK'\
                  '\nsrun $@'.format(**locals()), file=sfile)

    elif hostname == 'r06m01': # palma main node host name
        if queue is None:
            queue='hims,q0heuer,normal'
        with open(submitout, "w") as sfile:
            print('#!/bin/bash'
                  '\n#SBATCH -A q0heuer'
                  '\n#SBATCH -p {queue}'
                  '\n#SBATCH --output={jobname}.out'
                  '\n#SBATCH --mail-type=fail'
                  '\n#SBATCH --mail-user={username}@wwu.de'
                  '\n#SBATCH --time=48:00:00'
                  '\n#SBATCH --ntasks=1'
                  '\n#SBATCH --nodes=1'
                  '\n#SBATCH --cpus-per-task={ncores}'
                  '\n#SBATCH --mem={mem}'
                  '\nexport OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK'\
                  '\nsrun $@'.format(**locals()), file=sfile)
    else:
        raise ValueError("Hostname not found")
