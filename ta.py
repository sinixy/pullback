import numpy as np
from sklearn.cluster import DBSCAN

from common.utils import async_wrap


def ema(previous_ema, current_price, lag):
    k = 2 / (lag + 1)
    return (current_price * k) + (previous_ema * (1 - k))


@async_wrap
def find_spikes(x, y, ema, threshold=0.004):
    # only negative spikes (knives)
    x = np.array(x)
    y = np.array(y)
    y_norm = y / y.max()
    spikes_mask = np.zeros(len(x))
    
    for xe, ye in ema:
        indx = np.where(x.astype(int) == xe)[0]
        relative_spikes_indx = np.where(ye - y_norm[indx] >= threshold)[0]
        absolute_spikes_indx = indx[relative_spikes_indx]
        spikes_mask[absolute_spikes_indx] = 1

    spikes_mask = spikes_mask.astype(bool)
    spikes_x = x[spikes_mask]
    spikes_indx = np.arange(len(x))[spikes_mask]
    spikes_exists = len(spikes_indx) > 0
    if spikes_exists:
        clustering = DBSCAN(eps=0.3, min_samples=2).fit(spikes_x.reshape(-1, 1))
    else:
        return {'spikesIndx': [], 'biggest': 0}
    
    grouped_spikes_indx = []
    for label in set(clustering.labels_):
        if label == -1:
            continue
        indx = np.where(clustering.labels_ == label)[0]
        group = spikes_indx[indx]
        group_min = x[group].min()
        group_max = x[group].max()
        group_extended = np.where((group_min - 0.15 < x) & (x <= group_max))[0]
        grouped_spikes_indx.append(group_extended)

    return {
        'spikesIndx': grouped_spikes_indx,
        'biggest': max([y[s].max() / y[s].min() - 1 for s in grouped_spikes_indx])
    }