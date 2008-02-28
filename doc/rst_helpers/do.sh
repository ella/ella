#!/bin/bash

cat 0*.txt rst_helpers/z.linebreak.txt > ella.txt
for i in 1*.txt; do cat $i >> ella.txt; cat rst_helpers/z.linebreak.txt >> ella.txt; done
for i in 2*.txt; do cat $i rst_helpers/z.line.txt >> ella.txt; done
for i in 3*.txt; do cat $i rst_helpers/z.line.txt >> ella.txt; done
cat rst_helpers/z.linebreak.txt 9*.txt >> ella.txt

for i in *.txt; do rst2html.py $i > ${i%.txt}.html; done

rst2latex.py ella.txt > ella.latex
pdflatex ella.latex

