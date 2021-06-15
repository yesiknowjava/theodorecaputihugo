#!/bin/bash

# set -e

# cd markdown_generator 
# python3 doi.py
# cd ..

cd build
xelatex -interaction=nonstopmode TheodoreCaputiShortCV.tex
sleep 5
xelatex -interaction=nonstopmode TheodoreCaputiShortCV.tex
sleep 5
xelatex -interaction=nonstopmode TheodoreCaputiShortCV.tex
sleep 5
cp TheodoreCaputiShortCV.pdf ../static/files/
cd ..

sleep 5
hugo 

# git rm --cached public
# git submodule add -b master --force  https://github.com/tlcaputi/tlcaputi.github.io.git public

rm public/assets/css/main.scss
cd public
git add .
git commit -m "update site for new papers"
git push

cd ..
git add .
git commit -m "update submodule for new papers"
git push