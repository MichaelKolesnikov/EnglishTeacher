#!/bin/bash

VENV_PATH="/home/gitlab-runner/bica-project/.bica"
BICA_SERVICE_PATH="/etc/systemd/system"

cd /home/gitlab-runner/bica-project

# Проверяем, существует ли виртуальное окружение
rm -rf $VENV_PATH
python3 -m venv .bica  # Создаем новое виртуальное окружение
source "$VENV_PATH/bin/activate"  # Активируем его
pip install -r requirements.txt


# Проверяем, существует ли файл bica.service на сервере
sudo rm $BICA_SERVICE_PATH/bica.service
sudo cp ./bica.service "$BICA_SERVICE_PATH"
sudo systemctl enable bica
sudo systemctl daemon-reload  # Перезагружаем конфигурацию systemd
sudo systemctl restart bica.service  # Перезапускаем сервис

echo "Деплой завершен."

