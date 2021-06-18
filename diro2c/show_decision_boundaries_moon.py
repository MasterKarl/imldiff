import matplotlib.gridspec as gridspec
from mlxtend.plotting import plot_decision_regions
import matplotlib.pyplot as plt
from sklearn.datasets import make_classification
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn import tree
from sklearn.model_selection import train_test_split
import _pickle as cPickle
import numpy as np
import pandas as pd
from sklearn.datasets import make_moons
from sklearn import svm
import copy

import rule_extractor
import diro2c
from data import preprocess_data
from data_generation.neighborhood_generation import neighbor_generator
from data_generation.global_data_generation import global_data_generator
from data_generation.helper import *
import evaluation

from enums.dataset_type import dataset_type
from enums.diff_classifier_method_type import diff_classifier_method_type


def main():

    # X, y = make_classification(n_features=2, n_redundant=0, n_informative=1,
    #                            n_clusters_per_class=1)

    # Create classification sample:
    X1, y1 = make_moons(n_samples=100, random_state=123)
    X1 = X1*100
    y1 = []
    y2 = []

    for x_0 in X1:
        if x_0[0] > 100:
            y_0 = 1
        else:
            y_0 = 0

        if (x_0[0] > -40 and x_0[0] <= 10) or x_0[0] > 60:
            y_1 = 1
        else:
            y_1 = 0

        y1.append(y_0)
        y2.append(y_1)

    y1 = np.asarray(y1)
    y2 = np.asarray(y2)

    # -----------------------------------------------
    # train BB 1:

    # blackbox1 = svm.SVC()
    blackbox1 = DecisionTreeClassifier()
    blackbox1.fit(X1, y1)

    # -----------------------------------------------
    # manipulate and train BB 2:

    # blackbox2 = svm.SVC()
    blackbox2 = DecisionTreeClassifier()
    blackbox2.fit(X1, y2)
    # -------------------------------------------------

    feature1 = []
    feature2 = []
    for x in X1:
        feature1.append(x[0])
        feature2.append(x[1])

    feature1 = np.asarray(feature1)
    feature2 = np.asarray(feature2)

    y1 = y1.astype(str)

    d = {'y': y1, 'x0': feature1, 'x1': feature2}

    df = pd.DataFrame(d)

    dataset = prepare_df(df, 'test', 'y')
    # idx 36: 84,136
    print(X1[45])
    diff_classifiers_info = diro2c.recognize_diff(45, X1, dataset, blackbox1, blackbox2,
                                                  diff_classifier_method_type.binary_diff_classifier, data_generation_function=neighbor_generator.get_genetic_neighborhood)
    # dtc_max_depth=3)

    dc_info = diff_classifiers_info['binary_diff_classifer']
    dc_full = dc_info['dc_full']
    dc_test = dc_info['dc_test']
    evaluation_info = dc_info['evaluation_info']

    X_diff = evaluation_info['X']
    y_diff = evaluation_info['y']

    print(np.unique(y_diff, return_counts=True))

    fig, ax = plt.subplots(1, 3, figsize=(16, 8))

    fig = plot_decision_regions(X=X1, y=y1.astype(
        np.int64), clf=blackbox1, ax=ax[0], legend=2)
    ax[0].set_xlabel('feature 1')
    ax[0].set_ylabel('feature 2')
    # ax[0].set_xlim([-200, 200])
    # ax[0].set_ylim([-200, 200])
    ax[0].set_title('blackbox 1')

    fig = plot_decision_regions(X=X1, y=y2.astype(
        np.int64), clf=blackbox2, ax=ax[1], legend=2)
    ax[1].set_xlabel('feature 1')
    ax[1].set_ylabel('feature 2')
    ax[1].set_title('blackbox 2')

    fig = plot_decision_regions(X=X_diff, y=y_diff.astype(
        np.int64), clf=dc_full, ax=ax[2], legend=2)
    ax[2].set_xlabel('feature 1')
    ax[2].set_ylabel('feature 2')
    ax[2].set_title('binary diff-classifier')
    # handles, labels = ax.get_legend_handles_labels()
    # ax.legend(handles,
    #           ['class a', 'class b', 'class c', 'class d'],
    #           framealpha=0.3, scatterpoints=1)

    plt.show()
    # plt.savefig('images/decision_boundaries_moon.png')

    fn = ['x - feature 1', 'y - feature 2']
    cn = ['negative', 'positive']
    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(4, 4), dpi=300)
    tree.plot_tree(dc_full,
                   feature_names=fn,
                   class_names=cn,
                   filled=True)
    fig.savefig('images/decision_tree_moon.png')

    # tree_to_code(dc_full, dataset['columns'])
    # print_decision_tree(dc_full, dataset['columns'])
    rule_extractor.print_rules_for_binary(
        dc_full, dataset['columns_for_decision_rules'], ['no_diff', 'diff'], 'diff')


if __name__ == "__main__":
    main()
