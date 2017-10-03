#!/usr/bin/python

import sys
import pickle
sys.path.append("../tools/")

from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data

### Task 1: Select what features you'll use.
### features_list is a list of strings, each of which is a feature name.
### The first feature must be "poi".
features_list = [
                'poi',
                'salary',
                'bonus',
                'bonus_salary_ratio',
                #'deferral_payments',
                #'deferred_income',
                #'director_fees',
                #'email_address',
                'exercised_stock_options',
                #'expenses',
                #'from_messages',
                #'from_poi_to_this_person',
                'from_poi_to_this_person_ratio',
                #'from_this_person_to_poi',
                'from_this_person_to_poi_ratio',
                #'loan_advances',
                #'long_term_incentive',
                #'other',
                #'restricted_stock',
                #'restricted_stock_deferred',
                'shared_receipt_with_poi',
                #'to_messages',
                #'total_payments',
                'total_stock_value'
                 ] # You will need to use more features

### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)

### Task 2: Remove outliers
data_dict.pop("TOTAL")
data_dict.pop("THE TRAVEL AGENCY IN THE PARK")
data_dict.pop('LOCKHART EUGENE E')


### Task 3: Create new feature(s)
for employee, features in data_dict.iteritems():
    if features['bonus']  == "NaN" or features['salary'] == "NaN":
        features['bonus_salary_ratio'] = "NaN"
    else:
        features['bonus_salary_ratio'] = float(features['bonus'])/float(features['salary'])
    
for employee, features in data_dict.iteritems():
    if features['from_messages']  == "NaN" or features['from_poi_to_this_person'] == "NaN":
        features['from_poi_to_this_person_ratio'] = "NaN"
    else:
        features['from_poi_to_this_person_ratio'] = float(features['from_poi_to_this_person'])/float(features['from_messages'])

for employee, features in data_dict.iteritems():
    if features['to_messages']  == "NaN" or features['from_this_person_to_poi'] == "NaN":
        features['from_this_person_to_poi_ratio'] = "NaN"
    else:
        features['from_this_person_to_poi_ratio'] = float(features['from_this_person_to_poi'])/float(features['to_messages'])

### Impute NaN email features to mean
email_features = [
                  'from_messages',
                  'from_this_person_to_poi',
                  #'from_this_person_to_poi_ratio',
                  'to_messages',
                  'from_poi_to_this_person',
                  #'from_poi_to_this_person_ratio',
                  'shared_receipt_with_poi'
                  ]
# Fill in the NaN email data with the mean grouped by poi/non-poi
from collections import defaultdict
email_feature_poi_sum = defaultdict(lambda:0)
email_feature_poi_count = defaultdict(lambda:0)
email_feature_nonpoi_sum = defaultdict(lambda:0)
email_feature_nonpoi_count = defaultdict(lambda:0)

for employee, features in data_dict.iteritems():
    for value in email_features:
        if features[value] != "NaN" and features['poi'] == True:
            email_feature_poi_sum[value] += features[value]
            email_feature_poi_count[value] += 1
        elif features[value] != "NaN" and features['poi'] == False:
            email_feature_nonpoi_sum[value] += features[value]
            email_feature_nonpoi_count[value] += 1

email_feature_poi_mean = {}
email_feature_nonpoi_mean = {}
for value in email_features:
    email_feature_poi_mean[value] = float(email_feature_poi_sum[value]) / float(email_feature_poi_count[value])
    email_feature_nonpoi_mean[value] = float(email_feature_nonpoi_sum[value]) / float(email_feature_nonpoi_count[value])

for employee, features in data_dict.iteritems():
    for value in email_features:
        if features[value] == "NaN" and features['poi'] == True:
            features[value] = email_feature_poi_mean[value]
        if features[value] == "NaN" and features['poi'] == False:
            features[value] = email_feature_nonpoi_mean[value]
#Fill in the NaN payment and stock values with zero
#financial_features = ['salary',
                      #'bonus',
                      #'bonus_salary_ratio',
                      #]

            
### Store to my_dataset for easy export below.
my_dataset = data_dict

### Extract features and labels from dataset for local testing
data = featureFormat(my_dataset, features_list, sort_keys = True)
labels, features = targetFeatureSplit(data)

### Task 4: Try a varity of classifiers
### Please name your classifier clf for easy export below.
### Note that if you want to do PCA or other multi-stage operations,
### you'll need to use Pipelines. For more info:
### http://scikit-learn.org/stable/modules/pipeline.html

# Pipeline
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.feature_selection import SelectKBest
from sklearn.svm import SVC


estimators = [
              # Preprocessing
              # ('min_max_scaler', MinMaxScaler()),
        
              # Select Features
              ('select_features', SelectKBest()),
              
              # Classifier
              ('dtc', DecisionTreeClassifier())
              # ('svc',SVC())
              ]
pipe = Pipeline(estimators)


# Provided to give you a starting point. Try a variety of classifiers.
#from sklearn.naive_bayes import GaussianNB
#clf = GaussianNB()

### Task 5: Tune your classifier to achieve better than .3 precision and recall 
### using our testing script. Check the tester.py script in the final project
### folder for details on the evaluation method, especially the test_classifier
### function. Because of the small size of the dataset, the script uses
### stratified shuffle split cross validation. For more info: 
### http://scikit-learn.org/stable/modules/generated/sklearn.cross_validation.StratifiedShuffleSplit.html
import numpy as np
from sklearn.cross_validation import train_test_split, StratifiedShuffleSplit
from sklearn.model_selection import GridSearchCV

# Example starting point. Try investigating other evaluation techniques!
features_train, features_test, labels_train, labels_test = \
    train_test_split(features, labels, test_size=0.3, random_state=42)

param_grid = dict(
              select_features__k=[2, 4, 6, 8],
              dtc__criterion = ['gini', 'entropy'],
              dtc__min_samples_split = [2, 4, 6, 8, 10, 20],
              dtc__max_depth = [None, 5, 10, 15, 20],
              dtc__max_features = [None, 'sqrt', 'log2', 'auto']
              #svc__C=[0.1, 1, 10, 100, 1000],
              #svc__kernel=['rbf'],
              #svc__gamma=[0.001, 0.0001]
        ) 
# Cross-validation
sss = StratifiedShuffleSplit(labels_train, 20, test_size=0.5, random_state=0)
# Create grid to fit and predict with grid search
grid = GridSearchCV(pipe, cv=sss, param_grid=param_grid, scoring='f1')
grid.fit(features, labels)
labels_predictions = grid.predict(features_test)

clf = grid.best_estimator_
print "\n", "Best parameters are: ", grid.best_params_, "\n"

# Print features selected and their importances
features_selected = [features_list[i+1] for i in clf.named_steps['select_features'].get_support(indices=True)]
scores = clf.named_steps['select_features'].scores_
importances = clf.named_steps['dtc'].feature_importances_
indices = np.argsort(importances)[::-1]
for i in range(len(features_selected)):
    print "feature no.",i+1,features_selected[indices[i]],importances[indices[i]],scores[indices[i]]


### Task 6: Dump your classifier, dataset, and features_list so anyone can
### check your results. You do not need to change anything below, but make sure
### that the version of poi_id.py that you submit can be run on its own and
### generates the necessary .pkl files for validating your results.

dump_classifier_and_data(clf, my_dataset, features_list)

