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