from .models import Images, NetModels, Labels

def get_netmodel_by_name(netmodel_name):
    model = NetModels.objects.get(name=netmodel_name)
    return model


def get_labels(netmodel_id):
    labs = Labels.objects.extra(where=[f'netmodel_id={netmodel_id}']).order_by('predict_id').all()
    alab = []
    for lab in list(labs):
        alab.append(lab.name)
    return alab


def get_labels_str(netmodel_id):
    alab = get_labels(netmodel_id)
    res = ", ".join(alab)
    return res
