#!/bin/sh 
### General options 
### -- specify queue -- 
#BSUB -q hpc
### -- se3-round-cryptanalysis 
#BSUB -J round_cryptanalysis_f3[0,20,40,60,80,100,120,140,160,180,200,220,240,260,280,300,320,340,360,380,400,420,440,460]%4
### -- as1 
#BSUB -n 16
#BSUB -R "rusage[mem=512MB]"
#BSUB -W 6:00 
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

/zhome/2c/f/208660/data/dialga_differential_cryptanalysis/.venv/bin/python /zhome/2c/f/208660/data/dialga_differential_cryptanalysis/Jobs/perm_delta/find_maximum_differentials.py 3 -t 16 -p --job_name $(echo $LSB_JOBINDEX)_job --start $LSB_JOBINDEX --capacity 20
