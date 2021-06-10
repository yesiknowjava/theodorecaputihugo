cd markdown_generator 
python3 doi.py
cd ..

cd static/files
xelatex -interaction=nonstopmode TheodoreCaputiShortCV.tex
xelatex -interaction=nonstopmode TheodoreCaputiShortCV.tex
cd ..
cd ..

hugo

rm public/assets/css/main.scss
cd public
git add .
git commit -m "update site"
git push

cd ..
git add .
git commit -m "update submodule"
git push