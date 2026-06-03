#!/bin/sh 
### General options 
### -- specify queue -- 
#BSUB -q hpc
### -- se3-round-cryptanalysis 
#BSUB -J cryptanalysis_f6[1-32]%16
### -- as1 
#BSUB -n 1
#BSUB -R "rusage[mem=512MB]"
#BSUB -W 24:00 
### -- specify that the cores must be on the same host -- 
#BSUB -o Output_%J.out
#BSUB -e Output_%J.err
### -- send notification at start --
#BSUB -B
### -- send notification at completion --
#BSUB -N
### -- send notification at completion -- 
### -- Specify the output and error file. %J is the job-id -- 
### -- -o and -e mean append, -oo and -eo mean overwrite -- 
#BSUB -o Output_%J.out 
#BSUB -e Output_%J.err 

/zhome/2c/f/208660/data/dialga_differential_cryptanalysis/.venv/bin/python /zhome/2c/f/208660/data/dialga_differential_cryptanalysis/Jobs/perm_delta/find_maximum_differentials.py 6 -t 1 -of --job_name $(echo $LSB_JOBINDEX)_job --start $(((LSB_JOBINDEX -1) * 15)) --capacity 15
