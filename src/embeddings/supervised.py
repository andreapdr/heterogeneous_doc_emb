from data.tsr_function__ import get_supervised_matrix, get_tsr_matrix, information_gain, chi_square
import numpy as np


def zscores(x, axis=0): #scipy.stats.zscores does not avoid division by 0, which can indeed occur
    std = np.clip(np.std(x, ddof=1, axis=axis), 1e-5, None)
    mean = np.mean(x, axis=axis)
    return (x - mean) / std


def supervised_embeddings_tfidf(X,Y):
    tfidf_norm = X.sum(axis=0)
    tfidf_norm[tfidf_norm==0] = 1
    F = (X.T).dot(Y) / tfidf_norm.T
    return F


def supervised_embeddings_ppmi(X,Y):
    Xbin = X>0
    D = X.shape[0]
    Pxy = (Xbin.T).dot(Y)/D
    Px = Xbin.sum(axis=0)/D
    Py = Y.sum(axis=0)/D
    F = np.asarray(Pxy/(Px.T*Py))
    F = np.maximum(F, 1.0)
    F = np.log(F)
    return F


def supervised_embeddings_tsr(X,Y, tsr_function=information_gain, max_documents=25000):
    D = X.shape[0]
    if D>max_documents:
        print(f'sampling {max_documents}')
        random_sample = np.random.permutation(D)[:max_documents]
        X = X[random_sample]
        Y = Y[random_sample]
    cell_matrix = get_supervised_matrix(X, Y)
    F = get_tsr_matrix(cell_matrix, tsr_score_funtion=tsr_function).T
    return F


def get_supervised_embeddings(X, Y, reduction, max_label_space=300, voc=None, lang='None', binary_structural_problems=-1, method='dotn', dozscore=True):
    if max_label_space != 0:
        print('computing supervised embeddings...')
    nC = Y.shape[1]

    if method=='ppmi':
        F = supervised_embeddings_ppmi(X, Y)
    elif method == 'dotn':
        F = supervised_embeddings_tfidf(X, Y)
    elif method == 'ig':
        F = supervised_embeddings_tsr(X, Y, information_gain)
    elif method == 'chi2':
        F = supervised_embeddings_tsr(X, Y, chi_square)

    if dozscore:
        F = zscores(F, axis=0)

    # Dumping F-matrix for further studies
    dump_it = False
    if dump_it:
        with open(f'../dumps/WCE_{lang}.tsv', 'w') as outfile:
            np.savetxt(outfile, F, delimiter='\t')
        with open(f'../dumps/dict_WCE_{lang}.tsv', 'w') as outfile:
            for token in voc.keys():
                outfile.write(token+'\n')

    return F