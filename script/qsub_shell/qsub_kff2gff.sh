#!/bin/bash
#$ -S /bin/bash
#$ -cwd
#$ -o ./log.out
#$ -e ./log.err
#$ -l mem_user=4G -l h_vmem=4G -l mem_req=4G


python ${DIR}/script/python/kff2gff.py \
	${IN} \
	-o ${OUT}
