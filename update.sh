#!/bin/bash

read -p 'Commit Message: ' commit

hugo --cleanDestinationDir

rm public/assets/css/main.scss
cd public
git add .
git commit -m "site: $commit"
git push

cd ..
git add .
git commit -m "submodule: $commit"
git push