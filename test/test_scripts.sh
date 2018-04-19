#!/bin/bash
# quick test of scripts

err=0
tot=0
p="python ../scripts"
s="samples"
alias rm='/bin/rm'


lp_clean () {  $p/lpod-clean.py $s/bookmark.odt /dev/null  ; }
lp_clean2 () {  $p/lpod-clean.py $s/example.odt /dev/null  ; }
lp_convert ()  {  $p/lpod-convert.py $s/simple_table.ods a.odt && rm a.odt ;}
lp_convert2 () {  $p/lpod-convert.py $s/simple_table.ods a.csv && rm a.csv ;}
lp_convert3 () {  $p/lpod-convert.py $s/example.odt a.txt && rm a.txt ;}
lp_convert4 () {  $p/lpod-convert.py $s/example.odp a.html && rm a.html ;}
lp_diff () {  $p/lpod-diff.py $s/example.odt $s/base_text.odt ;}
lp_folder () {  $p/lpod-folder.py $s/example.odt && rm -r $s/example.odt.folder ;}
lp_high () {  $p/lpod-highlight.py -o a.odt -b $s/example.odt First && rm a.odt ;}
lp_merge () { $p/lpod-merge.py -o a.odt $s/base_text.odt $s/example.odt && rm a.odt ;}
lp_meta () { $p/lpod-meta.py $s/meta.odt ;}
lp_show () { $p/lpod-show.py $s/bookmark.odt ;}
lp_show2 () { $p/lpod-show.py $s/example.odp ;}
lp_style () { $p/lpod-style.py $s/example.odt ;}


tests="
lp_clean
lp_clean2
lp_convert
lp_convert2
lp_convert3
lp_convert4
lp_diff
lp_folder
lp_high
lp_merge
lp_meta
lp_show
lp_show2
lp_style
"


for t in $tests ; do
    let tot++
    echo -en "$t :"
    $t &> /dev/null && echo " passed." || { echo " failed !"; let err++ ; }
    #$t  && echo " passed." || { echo " failed !"; let err++ ; }
    done
echo
echo "------------------------------------------"
echo "total scripts: $tot, failed scripts: $err"
echo "------------------------------------------"
