# -*- coding: utf-8 -*-
from __future__ import print_function
import datetime
import numpy as np
import pandas as pd
import sklearn
from alpha_vantage.timeseries import TimeSeries
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis as QDA
from sklearn.metrics import confusion_matrix
from sklearn.svm import LinearSVC, SVC
def get_vantage_client():
    VANTAGE_API_KEY = 'R4RZ079WZET1M0JB'
    return TimeSeries(key = VANTAGE_API_KEY, output_format = 'pandas')

def create_lagged_series(symbol, start_date, end_date, lags = 5):
    """
    This creates a pandas DataFrame that stores the 
    percentage returns of the adjusted closing value of 
    a stock obtained from Yahoo Finance, along with a 
    number of lagged returns from the prior trading days 
    (lags defaults to 5 days). Trading volume, as well as 
    the Direction from the previous day, are also included.
    """
    vc = get_vantage_client()
    ts, meta = vc.get_daily(symbol, outputsize = 'full')
    ts = ts.rename(columns = {"1. open": "open", "2. high": "high", "3. low": "low", "4. close": "close", "5. volume": "volume"})

    # Create the new lagged DataFrame
    tslag = pd.DataFrame(index = ts.index)
    tslag["Today"] = ts["close"]
    tslag["Volume"] = ts["volume"]

    # Create the shifted lag series of prior trading period close values
    for i in range(0, lags):
        tslag["Lag%s" % str(i+1)] = ts["close"].shift(i+1)

    # Create the returns DataFrame
    tsret = pd.DataFrame(index = tslag.index)
    tsret["Volume"] = tslag["Volume"]
    tsret["Today"] = tslag["Today"].pct_change()*100.0

    # If any of the values of percentage returns equal zero, set them to
    # a small number (stops issues with QDA model in scikit-learn)
    for i,x in enumerate(tsret["Today"]):
        if (abs(x) < 0.0001):
            tsret["Today"][i] = 0.0001

    # Create the lagged percentage returns columns
    for i in range(0, lags):
        tsret["Lag%s" % str(i+1)] = \
        tslag["Lag%s" % str(i+1)].pct_change()*100.0

    # Create the "Direction" column (+1 or -1) indicating an up/down day
    tsret["Direction"] = np.sign(tsret["Today"])
    tsret = tsret[(tsret.index >= start_date) & (tsret.index <= end_date)]
    return tsret

if __name__ == "__main__":
    # Create a lagged series of the S&P500 US stock market index
    snpret = create_lagged_series("SPX", '2001-01-10', '2005-12-31', lags=5)

    # Use the prior two days of returns as predictor 
    # values, with direction as the response
    X = snpret[["Lag1","Lag2"]]
    y = snpret["Direction"]

    # The test data is split into two parts: Before and after 1st Jan 2005.
    start_test = '2005-01-01'

    # Create training and test sets
    X_train = X[X.index < start_test]
    X_test = X[X.index >= start_test]
    y_train = y[y.index < start_test]
    y_test = y[y.index >= start_test]
   
    # Create the (parametrised) models
    print("Hit Rates/Confusion Matrices:\n")
    models = [("LR", LogisticRegression(solver = 'lbfgs')), ("LDA", LDA()), ("QDA", QDA()), ("LSVC", LinearSVC()),
              ("RSVM", SVC(
              	C=1000000.0, cache_size=200, class_weight=None,
                coef0=0.0, degree=3, gamma=0.0001, kernel='rbf',
                max_iter=-1, probability=False, random_state=None,
                shrinking=True, tol=0.001, verbose=False)
              ),
              ("RF", RandomForestClassifier(
              	n_estimators=1000, criterion='gini', 
                max_depth=None, min_samples_split=2, 
                min_samples_leaf=1, max_features='auto', 
                bootstrap=True, oob_score=False, n_jobs=1, 
                random_state=None, verbose=0)
              )]

    # Iterate through the models
    for m in models:
        # Train each of the models on the training set
        m[1].fit(X_train, y_train)
        # Make an array of predictions on the test set
        pred = m[1].predict(X_test)
        # Output the hit-rate and the confusion matrix for each model
        print("%s:\n%0.3f" % (m[0], m[1].score(X_test, y_test)))
        print("%s\n" % confusion_matrix(pred, y_test))
