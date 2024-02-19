import os
import django
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
print(f"BASE_DIR: {BASE_DIR}")
os.environ.setdefault("PYTHONPATH", str(BASE_DIR))
# print(os.environ['PYTHONPATH'])

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ds_project.settings")
# print(os.environ['DJANGO_SETTINGS_MODULE'])

django.setup()

from impred.models import NetModels, Labels

def load_json(filename):
    with open(filename, "r", encoding='utf-8') as file:
        data = json.load(file)
    return data

def load_data():
    a_list = {}
    pathname = Path(__file__).resolve().parent
    netmodels = load_json(pathname.joinpath('data/netmodels.json'))
    for netm in netmodels:
        fn = netm.get("name")
        netmod, *_ = NetModels.objects.get_or_create(
                        name = fn,
                        description = netm.get("description"),
                        accuracy = netm.get("accuracy")
                    )
        a_list.update({fn: netmod})

    labels = load_json(pathname.joinpath('data/labels.json'))
    for lbl in labels:
        q1 = lbl.get("name")
        netm = a_list.get(lbl.get("netmodel"))
        exists_label = bool(len(Labels.objects.filter(name=q1).filter(netmodel=netm)))
        if not exists_label:
            label = Labels.objects.create(
                netmodel = netm,
                name = q1,
                predict_id = lbl.get("predict_id")
            )

if __name__ == '__main__':
    load_data()
