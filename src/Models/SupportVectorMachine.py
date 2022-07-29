import numpy as np
from sklearn import svm

def getSupportVectorMachine(X, y):
    """
    Fits Support Vector Machine
    """

    model = svm.LinearSVC(random_state = 0, tol = 1e-5)
    model.fit(np.array(X).reshape(-1, 1), y)

    return model