import numpy as np
from sklearn import svm

def getSupportVectorMachine(X, y):
    """
    Fits Support Vector Machine
    """

    model = svm.SVC(kernel = 'rbf', random_state = 0, tol = 1e-5)
    model.fit(X, y)

    return model