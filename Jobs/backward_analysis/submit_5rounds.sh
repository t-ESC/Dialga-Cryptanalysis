#!/bin/sh 
### General options 
### -- specify queue -- 
#BSUB -q hpc
### -- se3-round-cryptanalysis 
#BSUB -J round_cryptanalysis_b5
### -- as1 
#BSUB -n 20
#BSUB -R "rusage[mem=512MB]"
#BSUB -W 72:00 
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

/zhome/2c/f/208660/data/dialga_differential_cryptanalysis/.venv/bin/python /zhome/2c/f/208660/data/dialga_differential_cryptanalysis/Jobs/backward_analysis/find_maximum_differentials_5_rounds_backwards.py
