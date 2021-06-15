#!/bin/bash

read -p 'Commit Message: ' commit

hugo

rm public/assets/css/main.scss
cd public
git add .
git commit -m "site: $commit"
git push

cd ..
git add .
git commit -m "repo: $commit"
git push