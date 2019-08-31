cd ancile/web/vueapp

npm run build

cd ../../../

source .env/bin/activate

python manage.py collectstatic
