from os import path
import sys
# Обновляем директорию для импорта модуля
current = path.dirname(path.realpath(__file__))
parent = path.dirname(current)
sys.path.append(parent)
