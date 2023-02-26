from PIL import Image
import numpy as np

from sklearn import datasets, svm, metrics
from sklearn.model_selection import train_test_split
from sklearn.cluster import MiniBatchKMeans

def preprocess_single(org_img_path: str) -> tuple[np.ndarray, np.ndarray]:
    """Load a single image and process it with Pillow (https://pillow.readthedocs.io/en/stable/).
    Args:
        org_img_path: path to an image, e.g., org_img_path = './ILSVRC2012_val_00000094.JPEG'
    Return:
        img_array_1 (np.ndarray): numpy array of the input image
        img_array_2 (np.ndarray): numpy array of the resized image in RGBA mode
    """
    img = Image.open(org_img_path) ### load this image
    # print(img.mode, img.size)      ### get the color mode and size (W, H) of this image
    img_array_1 = np.array(img)      ### transfer the image into numpy array
    # print(img_array_1.shape)         ### shape of the numpy array would be (W, H, C) or (W, H)

    img = img.resize((224, 224))  ### resize
    img.convert('RGBA')           ### change the color mode to 'RGBA'
    # print(img.mode, img.size)     
    img_array_2 = np.array(img)
    # print(img_array_2.shape)
    return img_array_1, img_array_2

# ### Example
# img_array_1, img_array_2 = preprocess_single('./ILSVRC2012_val_00000094.JPEG')

def process_mnist() -> tuple[np.ndarray, np.ndarray]:
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
    digits = datasets.load_digits()

    # flatten the images
    n_samples = len(digits.images)
    data = digits.images.reshape((n_samples, -1))

    # Split data into 60% train and 40% test subsets
    X_train, X_test, y_train, y_test = train_test_split(
        data, digits.target, test_size=0.4, shuffle=False
    )
    # print(type(X_train), X_train.shape, type(y_train), y_train.shape)
    # print(type(X_test), X_test.shape, type(y_test), y_test.shape)

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

# process_mnist()