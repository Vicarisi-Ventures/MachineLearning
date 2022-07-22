from sklearn.linear_model import SGDClassifier

def getStochasticGradientDescent():
    """
    
    """


    model = SGDClassifier(loss="hinge", penalty="l2", max_iter=5)
    model.fit()

    return 0