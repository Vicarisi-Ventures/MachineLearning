import numpy as np
from sklearn.ensemble import RandomForestClassifier

def getRandomForest(X, y,):
    """
    Fits Random Forest 
    """

    model = RandomForestClassifier(max_depth=2, random_state=0)
    model.fit(X, y)

    return model 
