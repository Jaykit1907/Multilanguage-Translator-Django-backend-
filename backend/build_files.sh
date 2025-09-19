echo "BUILD START"
python3.9 -m pip install --upgrade pip
python3.9 -m pip install -r requirements.txt
python3.9 backend/manage.py collectstatic --noinput --clear
echo "BUILD END"
