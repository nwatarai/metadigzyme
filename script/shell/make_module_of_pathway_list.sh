for i in `seq 874`
do
    N=$(( i + 100000))
    ID=M${N:1}
    RESULT=$(curl http://togows.org/entry/kegg-module/${ID}/classes)
    if [ ${RESULT:0:7} = "Pathway" ]; then
     echo $ID
    fi
done > module_of_pathway.list

curl -o module_ec.list http://rest.kegg.jp/link/module/reaction

grep -f module_of_pathway.list module_ec.list >  module_ec.list.pathway
