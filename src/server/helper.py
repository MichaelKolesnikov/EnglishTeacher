import os
import pathlib
import yaml


def load_config():
    conf_path = os.path.join(pathlib.Path(__file__).parent.parent.absolute(), "config.yaml")
    with open(conf_path, 'r') as conf_file:
        config = yaml.load(conf_file, Loader=yaml.FullLoader)
    return config


from1to2 = ''' Согласие начать урок получено. Можно приступать к этапу 2 - написанию outline \n '''

from2to3 = ''' Ученик написал outline, можно переходить к написанию самого эссе - 3 этап.\n   '''

from3to4 = ''' Эссе написано. Можно перейти к этапу финальной оценки - 4 этап \n   '''


