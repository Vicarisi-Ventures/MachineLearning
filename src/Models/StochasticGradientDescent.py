import numpy as np
from sklearn.linear_model import SGDClassifier

def getStochasticGradientDescent(X, y):
    """
    Fits Stochastic Gradient Descent
    """

    model = SGDClassifier(loss="hinge", penalty="l2", max_iter=100)
    model.fit(np.array(X).reshape(-1, 1), y)

    return model