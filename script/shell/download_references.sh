#!/bin/bash

DIR=$(dirname $0)
DATA_DIR="${DIR}/../../data"
INPUT_DIR="${DATA_DIR}/input"
ANSWER_DIR="${DATA_DIR}/answer"

mkdir -p ${INPUT_DIR}
mkdir -p ${ANSWER_DIR}


######################################
# DOWNLOAD MODULE ENZYME NUMBER LIST #
######################################

wget "http://rest.kegg.jp/list/module" \
	-O "${INPUT_DIR}/module.list"

MODULES=(`cut -f 1 "${INPUT_DIR}/module.list" | cut -d ':' -f 2 | xargs`)
for i in ${MODULES[@]}
do
	RESULT=`wget "http://togows.org/entry/kegg-module/${i}/classes" -O "/dev/stdout"`
	if [ ${RESULT:0:7} = "Pathway" ]; then
     echo ${i}
    fi
done > "${INPUT_DIR}/module_of_pathway.list"

wget "http://rest.kegg.jp/link/module/ec" \
	-O "${INPUT_DIR}/module_ec.list"

grep \
	-f "${INPUT_DIR}/module_of_pathway.list"\
	"${INPUT_DIR}/module_ec.list" \
	>  "${INPUT_DIR}/module_ec.list.pathway"

rm "${INPUT_DIR}/module.list" \
	"${INPUT_DIR}/module_of_pathway.list" \
	"${INPUT_DIR}/module_ec.list"


######################################
# DOWNLOAD MODULE ENZYME NUMBER LIST #
######################################

PROKARYOTA=(`wget "http://rest.kegg.jp/list/organism" -O "/dev/stdout" | grep "Prokaryotes" | cut -f 2 | xargs`)
for i in ${PROKARYOTA[@]}
do
	wget "http://rest.kegg.jp/link/${i}/module" \
	-O "/dev/stdout" \
	| cut -f 2 -d '_'
done > "${ANSWER_DIR}/module_gene.list"
