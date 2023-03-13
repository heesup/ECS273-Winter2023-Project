import torch
from PIL import Image
import numpy as np

from sklearn import datasets, svm, metrics
from sklearn.model_selection import train_test_split
from sklearn.cluster import MiniBatchKMeans

import sys, os
root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir,"../"))
from utils import load_dataset, filter_dataset




def process_smart() -> tuple[np.ndarray, np.ndarray]:
    """Load MNIST dataset and do some basic processing
    Example 1: train a SVM model
    Example 2: cluster
    (Ref: https://scikit-learn.org/stable/auto_examples/classification/plot_digits_classification.html).
    Args:
        org_img_path: path to an image, e.g., org_img_path = './ILSVRC2012_val_00000094.JPEG'
    Return:
        img_array_1 (np.ndarray): numpy array of the input image
        img_array_2 (np.ndarray): numpy array of the resized image in RGBA mode
    """
    dataset = load_dataset()
    dataset = filter_dataset(dataset)
    # Shuffle dataset
    # dataset = dataset.sample(frac=1).reset_index(drop=True)
    
    res =  [False for i in range(len(dataset.columns))]
    for i,col in enumerate(dataset.columns):
        # if "normalized" in col:
        # #if "raw" in col:
        #     res[i] = False
        # # Value check
        if 'smart' in col:
            if (dataset[col].min() == 0) & (dataset[col].max() == 0):
                pass
            else:
                res[i] = True
    data = dataset.iloc[:,res]

   
    # Test 
    if 0:
        n_samples = 12000
        data = data[0:n_samples]
        targets = dataset['failure'][0:n_samples]
    else:
        targets = dataset['failure']

    # Split data into 60% train and 40% test subsets
    X_train, X_test, y_train, y_test = train_test_split(
        data, targets, test_size=0.4, shuffle=True
    )
    print(type(X_train), X_train.shape, type(y_train), y_train.shape)
    print(type(X_test), X_test.shape, type(y_test), y_test.shape)

    ### Example 1: train a SVM classifier and evaluate the performance matrices

    # Create a classifier: a support vector classifier
    clf = svm.SVC(gamma=0.001)
    # Learn the digits on the train subset
    clf.fit(X_train, y_train)
    # Predict the value of the digit on the test subset
    predicted = clf.predict(X_test)
    print(
        f"Classification report for classifier {clf}:\n"
        f"{metrics.classification_report(y_test, predicted)}\n"
    )

    ### Example 2: KMeans clustering
    n_digits = len(np.unique(y_train))
    # print(n_digits)
    # Initialize KMeans model
    kmeans = MiniBatchKMeans(n_clusters = n_digits)
    # Fit the model to the training data
    kmeans.fit(X_train)
    labels = kmeans.labels_ 
    # print(np.unique(labels))
    # print(type(X_train), X_train.shape, type(labels), labels.shape) 
    return X_train, labels


if __name__ == "__main__":
    process_smart()