#!/bin/bash

DIR=$(cd $(dirname $0)/../..; pwd)
VALIDATION_DIR="${DIR}/validation"
INPUT_DIR="${VALIDATION_DIR}/input"
OUTPUT_DIR="${VALIDATION_DIR}/output"
ANSWER_DIR="${VALIDATION_DIR}/answer"

MODULE_ENZYME="${INPUT_DIR}/module_enzyme"


##############################################
# DOWNLOAD MODULE ENZYME LIST FOR INPUT DATA #
##############################################

if [ ! -e "${INPUT_DIR}/module.list" ]; then
	wget "http://rest.kegg.jp/list/module" \
		-O "${INPUT_DIR}/module.list"
	rm "${INPUT_DIR}/module_of_pathway.list"
fi

if [ ! -e "${INPUT_DIR}/module_of_pathway.list" ]; then
	MODULES=(`cut -f 1 "${INPUT_DIR}/module.list" | cut -d ':' -f 2 | xargs`)
	for i in ${MODULES[@]}
	do
		RESULT=`wget "http://togows.org/entry/kegg-module/${i}/classes" -O "/dev/stdout"`
		if [ ${RESULT:0:7} = "Pathway" ]; then
	     echo ${i}
	    fi
	done > "${INPUT_DIR}/module_of_pathway.list"
	rm "${INPUT_DIR}/module_ec.list.pathway"
fi

if [ ! -e "${INPUT_DIR}/module_ec.list" ]; then
	wget "http://rest.kegg.jp/link/module/ec" \
		-O "${INPUT_DIR}/module_ec.list"
	rm "${INPUT_DIR}/module_ec.list.pathway"
fi

if [ ! -e "${INPUT_DIR}/module_ec.list.pathway" ]; then
	grep \
		-f "${INPUT_DIR}/module_of_pathway.list"\
		"${INPUT_DIR}/module_ec.list" \
		>  "${INPUT_DIR}/module_ec.list.pathway"
	rm -r "${MODULE_ENZYME}"
fi

if [ ! -e "${MODULE_ENZYME}" ]; then
	mkdir -p "${MODULE_ENZYME}"
	python "${DIR}/script/python/make_module_ec_lists.py" \
		"${INPUT_DIR}/module_ec.list.pathway" \
		-o "${MODULE_ENZYME}"
fi


################################################
# UNARCHIVE KFF AND GENE ENZYME FOR INPUT DATA #
################################################

if [ ! -e "${INPUT_DIR}/kff/zpr.kff" ]; then
	LIST=(`ls ${INPUT_DIR}/kff`)
	for i in ${LIST[@]}
	do
		NAME=`echo ${i} | cut -d '.' -f 1,2`
		gunzip -c "${INPUT_DIR}/kff/${i}" > "${INPUT_DIR}/kff/${NAME}"
	done
fi

if [ ! -e "${INPUT_DIR}/gene_enzyme/zpr.list" ]; then
	LIST=(`ls ${INPUT_DIR}/gene_enzyme`)
	for i in ${LIST[@]}
	do
		NAME=`echo ${i} | cut -d '.' -f 1,2`
		gunzip -c "${INPUT_DIR}/gene_enzyme/${i}" > "${INPUT_DIR}/gene_enzyme/${NAME}"
	done
fi


#############################################
# DOWNLOAD MODULE GENE LIST FOR ANSWER DATA #
#############################################

if [ ! -e "${ANSWER_DIR}/module_gene.list" ]; then
PROKARYOTA=(`wget "http://rest.kegg.jp/list/organism" -O "/dev/stdout" | grep "Prokaryotes" | cut -f 2 | xargs`)
for i in ${PROKARYOTA[@]}
do
	wget "http://rest.kegg.jp/link/${i}/module" \
	-O "/dev/stdout" \
	| cut -f 2 -d '_' \
	| grep -f "${INPUT_DIR}/module_of_pathway.list"
done > "${ANSWER_DIR}/module_gene.list"
fi
