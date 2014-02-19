# Usage: ./range.sh pull.tsv 6
FILE=$1
COL=$2

cat $FILE | awk '{print $'$COL'}' | sort -n > out~
date -d @`head -1 out~`
date -d @`tail -1 out~`

rm out~
