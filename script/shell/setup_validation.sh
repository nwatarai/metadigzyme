#!/bin/bash

DIR=$(cd $(dirname $0)/../..; pwd)
VALIDATION_DIR="${DIR}/validation"
INPUT_DIR="${VALIDATION_DIR}/input"
OUTPUT_DIR="${VALIDATION_DIR}/output"
ANSWER_DIR="${VALIDATION_DIR}/answer"

MODULE_ENZYME_DIR="${INPUT_DIR}/module_enzyme"
GENE_ENZYME_DIR="${INPUT_DIR}/gene_enzyme"
KFF_DIR="${INPUT_DIR}/kff"
GFF_DIR="${INPUT_DIR}/gff"


##############################################
# DOWNLOAD MODULE ENZYME LIST FOR INPUT DATA #
##############################################

if [ ! -e "${INPUT_DIR}/module.list" ]; then
	wget "http://rest.kegg.jp/list/module" \
		-O "${INPUT_DIR}/module.list"
fi


if [ ! -e "${INPUT_DIR}/module_ec.list" ]; then
	wget "http://rest.kegg.jp/link/module/ec" \
		-O "${INPUT_DIR}/module_ec.list"
	rm "${INPUT_DIR}/module_ec.list.pathway"
fi

grep \
	-f "${VALIDATION_DIR}/module_of_pathway.list"\
	"${INPUT_DIR}/module_ec.list" \
	>  "${INPUT_DIR}/module_ec.list.pathway"

rm -r "${MODULE_ENZYME_DIR}"
mkdir -p "${MODULE_ENZYME_DIR}"
python "${DIR}/script/python/make_module_ec_lists.py" \
	"${INPUT_DIR}/module_ec.list.pathway" \
	-o "${MODULE_ENZYME_DIR}"


################################################
# UNARCHIVE KFF AND GENE ENZYME FOR INPUT DATA #
################################################

if [ ! -e "${KFF_DIR}/zpr.kff" ]; then
	LIST=(`ls ${KFF_DIR}`)
	for i in ${LIST[@]}
	do
		NAME=`echo ${i} | cut -d '.' -f 1,2`
		gunzip -c "${KFF_DIR}/${i}" > "${KFF_DIR}/${NAME}"
	done
	rm -r ${GFF_DIR}
fi

if [ ! -e "${GENE_ENZYME_DIR}/zpr.list" ]; then
	LIST=(`ls ${GENE_ENZYME_DIR}`)
	for i in ${LIST[@]}
	do
		NAME=`echo ${i} | cut -d '.' -f 1,2`
		gunzip -c "${GENE_ENZYME_DIR}/${i}" > "${GENE_ENZYME_DIR}/${NAME}"
	done
fi


######################
# CONVERT KFF TO GFF #
######################

if [ ! -e "${GFF_DIR}" ]; then
	mkdir -p "${GFF_DIR}"
	LIST=(`ls ${KFF_DIR} | grep -v '.gz'`)
	for i in ${LIST[@]}
	do
		NAME=`echo ${i} | cut -d '.' -f 1`
		python ${DIR}/script/python/kff2gff.py \
		    "${KFF_DIR}/${i}" \
		    -o "${GFF_DIR}/${NAME}.gff"
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
	| grep -f "${VALIDATION_DIR}/module_of_pathway.list"
done > "${ANSWER_DIR}/module_gene.list"
fi
