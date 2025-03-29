import os
import sys
import cv2 as cv
from flask import current_app
import numpy as np
import pickle
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from keras_facenet import FaceNet
from mtcnn.mtcnn import MTCNN
from concurrent.futures import ThreadPoolExecutor
import tensorflow as tf
from joblib import Parallel, delayed

# Initialize MTCNN for face detection and FaceNet for embeddings
detector = MTCNN()
embedder = FaceNet()

def extract_face(filename):
    img = cv.imread(filename)
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    faces = detector.detect_faces(img)
    if faces:
        x, y, w, h = faces[0]['box']
        x, y = abs(x), abs(y)
        face = img[y:y+h, x:x+w]
        face_arr = cv.resize(face, (160, 160))
        return face_arr
    return None

def load_faces_from_directory(directory):
    faces = []
    labels = []

    # Define supported image extensions
    valid_extensions = ('.jpg', '.jpeg', '.png', '.heic')

    with ThreadPoolExecutor() as executor:
        # Create list of file paths and corresponding labels
        tasks = [
            (os.path.join(directory, sub_dir, im_name), sub_dir)
            for sub_dir in os.listdir(directory)
            for im_name in os.listdir(os.path.join(directory, sub_dir))
            if im_name.lower().endswith(valid_extensions)  # Filter only valid image files
        ]

        # Use ThreadPoolExecutor to speed up face extraction
        results = executor.map(lambda task: (extract_face(task[0]), task[1]), tasks)

        for face, label in results:
            if face is not None:
                faces.append(face)
                labels.append(label)

    return np.array(faces), np.array(labels)

def batch_get_embeddings(face_images, batch_size=32):
    embeddings = []
    for i in range(0, len(face_images), batch_size):
        batch = face_images[i:i + batch_size]
        batch = np.array([img.astype('float32') for img in batch])
        yhat = embedder.embeddings(batch)
        embeddings.extend(yhat)
    return embeddings

def train_and_save_model(directory):
    # Load faces and labels
    faces, labels = load_faces_from_directory(directory)

    # Get embeddings
    embeddings = np.asarray(batch_get_embeddings(faces))

    # Save embeddings and labels
    # class_id = directory.split('\\')[-1]
    class_id = directory.split('/')[-1]
    npz_save_path = os.path.join(current_app.root_path, 'ML_models', 'npz', f'faces_embeddings_{class_id}.npz')
    os.makedirs(os.path.dirname(npz_save_path), exist_ok=True)
    np.savez_compressed(npz_save_path, embeddings, labels)

    # Encode labels
    encoder = LabelEncoder()
    encoder.fit(labels)
    encoded_labels = encoder.transform(labels)

    # Split data
    X_train, X_test, Y_train, Y_test = train_test_split(embeddings, encoded_labels, test_size=0.2, random_state=42)

    # Train SVM model using parallel processing with joblib
    model = SVC(kernel='linear', probability=True)
    with Parallel(n_jobs=-1) as parallel:
        model.fit(X_train, Y_train)

    # Save the trained model
    svm_save_path = os.path.join(current_app.root_path, 'ML_models', 'svm', f'svm_model_{class_id}.pkl')
    os.makedirs(os.path.dirname(svm_save_path), exist_ok=True)
    with open(svm_save_path, 'wb') as f:
        pickle.dump(model, f)

    # Evaluate model accuracy
    train_accuracy = model.score(X_train, Y_train)
    test_accuracy = model.score(X_test, Y_test)
    print(f"Train Accuracy: {train_accuracy:.2f}")
    print(f"Test Accuracy: {test_accuracy:.2f}")

if __name__ == '__main__':
    directory = sys.argv[1]
    train_and_save_model(directory)
