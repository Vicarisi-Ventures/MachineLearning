from sklearn.ensemble import RandomForestClassifier

def getRandomForest():
    """
    
    """

    model = RandomForestClassifier(max_depth=2, random_state=0)
    model.fit()

    return 0 
