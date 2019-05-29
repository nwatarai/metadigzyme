#!/bin/bash

DIR=$(dirname $0/../..)
VALIDATION_DIR="${DIR}/data"
INPUT_DIR="${VALIDATION_DIR}/input"
OUTPUT_DIR="${VALIDATION_DIR}/output"
ANSWER_DIR="${VALIDATION_DIR}/answer"

MODULE_QUERY="${INPUT_DIR}/module_query"


######################################
# DOWNLOAD MODULE ENZYME NUMBER LIST #
######################################

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
	rm -r "${MODULE_QUERY}"
fi

if [ ! -e "${MODULE_QUERY}" ]; then
	mkdir -p "${MODULE_QUERY}"
	python "${DIR}/script/python/make_module_ec_lists.py" \
		"${INPUT_DIR}/module_ec.list.pathway" \
		-o "${MODULE_QUERY}"
fi


######################################
# DOWNLOAD MODULE ENZYME NUMBER LIST #
######################################

if [ ! -e "${ANSWER_DIR}/module_gene.list" ]; then
PROKARYOTA=(`wget "http://rest.kegg.jp/list/organism" -O "/dev/stdout" | grep "Prokaryotes" | cut -f 2 | xargs`)
for i in ${PROKARYOTA[@]}
do
	wget "http://rest.kegg.jp/link/${i}/module" \
	-O "/dev/stdout" \
	| cut -f 2 -d '_'
done > "${ANSWER_DIR}/module_gene.list"
fi
