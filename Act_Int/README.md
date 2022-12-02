MANUAL DE INSTALACIÓN ACTIVIDAD INTEGRADORA "BOX DELIVERY"
Stephan Guingor Falcon A01029421
Salvador Salgado Normandia A01422874

A continuación se describen los pasos necesarios para ejecutar el modelo

1) Ubicarse dentro de TC2008B.302>Act_Int>flask_server
cd ./flask_server

2) Para instalar las librerias necesarias se tiene dos alternativas, ya sea con pipenv o isntalarlas directamente

"PIPENV"
pip install pipenv 
PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy --system

"Instalación Normal"
pip install mesa
pip install flask

3) Finalmente dentro de la carpeta flask_server se ejecuta el siguiente comando
python app

4) Una vez que se haya inicializado se puede correr el proyecto de Unity
