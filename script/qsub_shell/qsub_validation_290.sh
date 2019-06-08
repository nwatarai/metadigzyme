#!/bin/bash

DIR=~/metadigzyme/
VALIDATION_DIR="${DIR}/validation"
INPUT_DIR="${VALIDATION_DIR}/input"
OUTPUT_DIR="${VALIDATION_DIR}/output"
ANSWER_DIR="${VALIDATION_DIR}/answer"

MODULE_ENZYME_DIR="${INPUT_DIR}/module_enzyme"
GENE_ENZYME_DIR="${INPUT_DIR}/gene_enzyme"
KFF_DIR="${INPUT_DIR}/kff"
GFF_DIR="${INPUT_DIR}/gff"

ORGANISMS=(`ls ${GFF_DIR} |cut -d '.' -f 1`)
MODULES=(`ls ${MODULE_ENZYME_DIR}`)
index=`expr $SGE_TASK_ID - 1`
m=${MODULES[$index]}

echo "${m}"
mkdir -p ${OUTPUT_DIR}/${m}
for o in ${ORGANISMS[@]}
do
	python ${DIR}/script/python/search_cluster.py \
		-g "${GFF_DIR}/${o}.gff" \
		-ge "${GENE_ENZYME_DIR}/${o}.list" \
		-me "${MODULE_ENZYME_DIR}/${m}" \
		-o "${OUTPUT_DIR}/${m}/${o}" 
	python ${DIR}/script/python/validate_result.py \
		-mg ${ANSWER_DIR}/module_gene.list \
		-d ${OUTPUT_DIR}/${m} -o ${VALIDATION_DIR}/${m}.accuracy
done

