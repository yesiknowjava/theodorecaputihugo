cd markdown_generator 
python3 doi.py
cd ..

cd static/files
xelatex -interaction=nonstopmode TheodoreCaputiShortCV.tex
sleep 5
xelatex -interaction=nonstopmode TheodoreCaputiShortCV.tex
sleep 5
xelatex -interaction=nonstopmode TheodoreCaputiShortCV.tex
cd ..
cd ..

hugo

rm public/assets/css/main.scss
cd public
git add .
git commit -m "update site for new papers"
git push

cd ..
git add .
git commit -m "update submodule for new papers"
git push