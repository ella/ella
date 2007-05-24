
# relativni cesta k nc.
PYTHONPATH="../../../:$PYTHONPATH"

# do adresare, kde zije manage.py
cd "$( dirname $( readlink -f $0 ))"

# pust test
python komments/manage.py test

