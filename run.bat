@echo off
pushd %~dp0

echo Installing requirements...
python\python.exe -m pip install --upgrade pip
python\python.exe -m pip install -r requirements.txt

echo Running main.py...
python\python.exe main.py

popd
echo Script execution finished.
pause