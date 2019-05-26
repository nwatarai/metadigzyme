#!/bin/bash

DIR=$(dirname $0)

wget "http://rest.kegg.jp/list/module" \
	-O "${DIR}/../../data/kegg/module.list"

MODULES=`cut -f 1 "${DIR}/../../data/kegg/module.list" | cut -d ':' -f 2 | xargs`
for i in ${MODULES[@]}
do
	RESULT=`wget "http://togows.org/entry/kegg-module/${i}/classes" -O "/dev/stdout"`
	if [ ${RESULT:0:7} = "Pathway" ]; then
     echo ${i}
    fi
done > "${DIR}/../../data/kegg/module_of_pathway.list"

wget "http://rest.kegg.jp/link/module/ec" \
	-O "${DIR}/../../data/kegg/module_ec.list"

grep \
	-f "${DIR}/../../data/kegg/module_of_pathway.list"\
	"${DIR}/../../data/kegg/module_ec.list" \
	>  "${DIR}/../../data/kegg/module_ec.list.pathway"
