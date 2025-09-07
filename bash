chmod +x build.sh
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
# build.sh
python -m ensurepip --upgrade
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
