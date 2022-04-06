**Dependencies of project**

These libs are external dependencies of the project, as in the servers we do not have access to download directly, they must be installed as per the command below.

Cases require manual installation of lib-lib, so do this
```bash
python pip-9.0.3-py2.py3-none-any.whl/pip install --no-index psycopg2-2.7.5-cp27-cp27mu-manylinux1_x86_64.whl --find-links=./pypi
```
Below irrelevant items
```bash
pip download pip==9.0.3 --proxy proxyapp.santanderbr.corp:80
pip download Flask==0.12.1 --proxy proxyapp.santanderbr.corp:80
pip download Flask-SQLAlchemy==2.2 --proxy proxyapp.santanderbr.corp:80
pip download psycopg2==2.7.5 --proxy proxyapp.santanderbr.corp:80
pip download elasticsearch==6.3.1 --proxy proxyapp.santanderbr.corp:80
pip download elasticsearch-dsl==6.2.1 --proxy proxyapp.santanderbr.corp:80
```


