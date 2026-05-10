#!/bin/sh 
### General options 
### -- specify queue -- 
#BSUB -q hpc
### -- se3-round-cryptanalysis 
#BSUB -J 3_round_cryptanalysis
### -- as1 
#BSUB -n 4
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

/zhome/2c/f/208660/data/dialga_differential_cryptanalysis/.venv/bin/python /zhome/2c/f/208660/data/dialga_differential_cryptanalysis/find_maximum_differentials_4_rounds.py
