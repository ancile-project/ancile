cd ancile/web/frontend

npm run build

cd ../../../

source .env/bin/activate

python manage.py collectstatic
