# -*- coding: utf-8 -*-
"""Data_Augmentation.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1JZ4YsETgWSVZ-01pPNDW7kKCQu9Gy1Ye
"""

import numpy as np
import pandas as pd
import csv 
import scipy
import tensorflow as tf
import cv2
import matplotlib.pyplot as plt
import os
import torch.nn as nn
import torch
import torch.nn.functional as F
import torch.optim as optim
import torchvision.transforms as transforms
import torchvision
import itertools
 
from scipy import ndimage
from skimage.io import imread, imshow 
from PIL import Image  
from keras.preprocessing.image import ImageDataGenerator
from torch.utils.data import DataLoader
from tqdm.notebook import tqdm
from sklearn.metrics import confusion_matrix , classification_report

def read_image(name): 
  img = imread(name)
  img = img.reshape((-1, 1090, 1600, 3))
  return img

def flip(image, n_new_img):
  new_Images = []
  # ImageDataGenerator flipping
  datagen = ImageDataGenerator(horizontal_flip=True, vertical_flip=True)

  # iterator
  aug_iter = datagen.flow(image, batch_size=1)
  # generate batch of images
  for i in range(n_new_img):
    image = next(aug_iter)[0].astype('uint8')
    new_Images.append(image)
  return new_Images

def Rotation(image, n_new_img, rotating_factor):
  new_Images = []
  # ImageDataGenerator rotation
  datagen = ImageDataGenerator(rotation_range=rotating_factor, fill_mode='nearest')

  # iterator
  aug_iter = datagen.flow(image, batch_size=1)

  # generate batch of images
  for i in range(n_new_img):
    image = next(aug_iter)[0].astype('uint8')
    new_Images.append(image)
  return new_Images

def Scale(image, zoom_factor, n_new_img):
  new_Images = []
  # ImageDataGenerator zooming
  datagen = ImageDataGenerator(zoom_range=zoom_factor)

  # iterator
  aug_iter = datagen.flow(image, batch_size=1)
  # generate batch of images
  for i in range(n_new_img):
    image = next(aug_iter)[0].astype('uint8')
    new_Images.append(image)
  return new_Images

def Brightness(image, _brightness_range, n_new_img):
  new_Images = []
  # ImageDataGenerator brightness
  datagen = ImageDataGenerator(brightness_range=_brightness_range)

  # iterator
  aug_iter = datagen.flow(image, batch_size=1)

  for i in range(n_new_img):
    image = next(aug_iter)[0].astype('uint8')
    new_Images.append(image)
  return new_Images

def plot_image(images, n_images):
  # generate samples and plot
  fig, ax = plt.subplots(nrows=1, ncols=n_images, figsize=(15,15))
  for i in range(n_images):
    ax[i].imshow(images[i])
    ax[i].axis('off')

image = read_image('test.jpg')

images = Rotation(image, n_new_img=3, rotating_factor=30)
plot_image(images, n_images=3)

images = flip(image, n_new_img=3)
plot_image(images, n_images=3)

images = Scale(image, zoom_factor=0.3, n_new_img=3)
plot_image(images, n_images=3)

images = Brightness(image, _brightness_range=[0.4,1.5], n_new_img=3)
plot_image(images, n_images=3)

"""# Part #3: Cifar10

Importing Dataset
"""

!wget https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz

!tar -xvf cifar-10-python.tar.gz

def unpickle(file):
    import pickle
    with open(file, 'rb') as fo:
        dict = pickle.load(fo, encoding='bytes')
    return dict

metadata = unpickle('cifar-10-batches-py/batches.meta')[b'label_names']

index2label = {
    index: label.decode('ascii') for index, label in enumerate(metadata)
}
index2label

data = unpickle('cifar-10-batches-py/data_batch_1')
print(data.keys())

test = unpickle('cifar-10-batches-py/test_batch')
print(test.keys())

data_array = data[b'data']
data_array = np.reshape(data_array, (10000, 3, 1024))

test_array = test[b'data']
test_array = np.reshape(test_array, (10000, 3, 1024))

data_labels = data[b'labels']
data_labels = np.array(data_labels)

test_labels = test[b'labels']
test_labels = np.array(test_labels)

data_array_agg = np.array([])
data_labels_agg = np.array([])
base_path = 'cifar-10-batches-py'
file_names = os.listdir(base_path)
for file_name in file_names:
    if file_name.startswith('data_batch'):

        data = unpickle(os.path.join(base_path, file_name))
        data_array = data[b'data']
        data_array = np.reshape(data_array, (10000, 3, 1024))
        data_labels = data[b'labels']
        data_labels = np.array(data_labels)
        if data_array_agg.shape == (0, ):
            data_array_agg = data_array
            data_labels_agg = data_labels
        else: 
            data_array_agg = np.append(data_array_agg, data_array, axis=0)
            data_labels_agg = np.append(data_labels_agg, data_labels, axis=0)
data_array_agg = data_array_agg.reshape((-1, 3, 32, 32))

data_array_agg.shape, data_labels_agg.shape

test_array_agg = np.array([])
test_labels_agg = np.array([])
base_path = 'cifar-10-batches-py'
file_names = os.listdir(base_path)
for file_name in file_names:
    if file_name.startswith('test_batch'):

        test = unpickle(os.path.join(base_path, file_name))
        test_array = test[b'data']
        test_array = np.reshape(test_array, (10000, 3, 1024))
        test_labels = test[b'labels']
        test_labels = np.array(test_labels)
        if test_array_agg.shape == (0, ):
            test_array_agg = test_array
            test_labels_agg = test_labels
        else: 
            test_array_agg = np.append(test_array_agg, test_array, axis=0)
            test_labels_agg = np.append(test_labels_agg, test_labels, axis=0)
test_array_agg = test_array_agg.reshape((-1, 3, 32, 32))

test_data = unpickle(os.path.join(base_path, 'test_batch'))
test_data_array = test_data[b'data']
test_data_array = np.reshape(test_data_array, (10000, 3, 1024))
test_data_labels = test_data[b'labels']
test_data_labels = np.array(test_data_labels)
test_data_array = test_data_array.reshape((-1, 3, 32, 32))

test_data_array.shape, test_data_labels.shape

"""### Converting the numpy arrays to the torch Data"""

def to_dataloader(data_array_agg, data_labels_agg, batch_size, normalizer=255.0):
    target = torch.tensor(data_labels_agg)
    data_array_agg = data_array_agg / normalizer
    data = torch.tensor(data_array_agg.astype(np.float32))

    data_tensor = torch.utils.data.TensorDataset(data, target)
    data_loader = DataLoader(data_tensor, shuffle=True, batch_size=batch_size)
    return data_loader

train_data_loader = to_dataloader(reduced_data_array_agg, reduced_data_labels_agg, batch_size=128)
test_data_loader = to_dataloader(test_array_agg, test_labels_agg, batch_size=128)

for data_array, target in train_data_loader:
    print('the shape of the data array: {}'.format(data_array.shape))
    print('the shape of the target array: {}'.format(target.shape))
    break

"""### Building the Model"""

# model with 3 convolutional hidden layers
class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.base = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=3, stride=1, padding=1, bias=False),
            nn.Conv2d(16, 16, kernel_size=3, stride=1, padding=1, bias=False),
            nn.BatchNorm2d(16),
            nn.ReLU(True)
        )

        self.layer1 = nn.Sequential(
            nn.Conv2d(16, 16, kernel_size=3, stride=1, padding=1, bias=False),
            nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1, bias=False),
            nn.BatchNorm2d(32),
            nn.ReLU(True)
        )

        self.layer2 = nn.Sequential(
            nn.Conv2d(32, 32, kernel_size=3, stride=1, padding=1, bias=False),
            nn.Conv2d(32, 16, kernel_size=3, stride=1, padding=1, bias=False),
            nn.BatchNorm2d(16),
            nn.ReLU(True)
        )

        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(16 * 4 * 4, 512)
        self.fc2 = nn.Linear(512, 128)
        self.fc3 = nn.Linear(128, 64)
        self.fc4 = nn.Linear(64, 32)
        self.fc5 = nn.Linear(32, 10)

    def forward(self, x):
        out = self.pool(self.base(x))
        out = self.pool(self.layer1(out))
        out = self.pool(self.layer2(out))

        out = out.reshape((out.size(0), -1))
        out = F.relu(self.fc1(out))
        out = F.relu(self.fc2(out))
        out = F.relu(self.fc3(out))
        out = F.relu(self.fc4(out))
        out = self.fc5(out)
        return out

"""### Utility Functions for Training and Evaluating the Model and also Visualization"""

def plot_train_test_acc(train_acc, test_acc):
    fig = plt.figure(figsize=(10, 6))
    plt.plot(train_acc, color='salmon', label='train accuracy', marker='o', linewidth=1)
    plt.annotate(str(np.round(train_acc[-1], 1)) + '%', (len(train_acc) - .8, train_acc[-1]), color='salmon')
    plt.plot(test_acc, color='skyblue', label='test accuracy', marker='o', linewidth=1)
    plt.annotate(str(np.round(test_acc[-1], 1)) + '%', (len(test_acc) - .8, test_acc[-1]), color='skyblue')
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.legend()

def check_accuracy(model, loader):
    correct = 0
    total = 0
    model.eval()
    outputs_agg = np.array([])
    targets_agg = np.array([])
    with torch.no_grad():
        for images, labels in loader:
            
            outputs = model(images)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            outputs_agg = np.append(outputs_agg, predicted.numpy())
            targets_agg = np.append(targets_agg, labels.numpy())
    model.train()
    acc = (100 * correct / total)
    return acc, outputs_agg, targets_agg

def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    plt.figure(figsize = (5,5))
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes)
    plt.yticks(tick_marks, classes)
    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, cm[i, j],
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")
    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')

"""### Training the Network"""

def train(model, criterion, optimizer, trainloader, testloader, n_epochs):
    train_epochs_acc = []
    test_epochs_acc = []
    for epoch in tqdm(range(n_epochs), leave=False):
        
        for inputs, labels in tqdm(trainloader, leave=False):
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

        train_acc, _, _ = check_accuracy(model, trainloader)
        test_acc, pred_test, target_test = check_accuracy(model, testloader)

        train_epochs_acc.append(train_acc)
        test_epochs_acc.append(test_acc)

    
    return train_epochs_acc, test_epochs_acc, pred_test, target_test

"""### Reduce dogs and cats classes"""

# ctas = 3 and dogs = 5
indices_to_select = np.array([], dtype=np.int64)
for index in index2label.keys():
    if index == 3 or index == 5:
      indices = np.where(data_labels_agg == index)[0]
      samples = np.random.choice(indices, 500, replace=False)
      indices_to_select = np.append(indices_to_select, samples, axis=0)
    else:
      indices = np.where(data_labels_agg == index)[0]
      samples = np.random.choice(indices, 5000, replace=False)
      indices_to_select = np.append(indices_to_select, samples, axis=0)

reduced_data_array_agg = data_array_agg[indices_to_select]
reduced_data_labels_agg = data_labels_agg[indices_to_select]

reduced_data_array_agg.shape, reduced_data_labels_agg.shape

reduced_train_data_loader = to_dataloader(reduced_data_array_agg, reduced_data_labels_agg, batch_size=128)

n_epochs = 10

net = Net()

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(net.parameters(), lr=0.001)
train_acc, test_acc, pred_test, target_test = train(net, criterion, optimizer, reduced_train_data_loader, test_data_loader, n_epochs)

plot_train_test_acc(train_acc, test_acc)

classes = ('plane', 'car', 'bird', 'cat',
           'deer', 'dog', 'frog', 'horse', 'ship', 'truck')

# Confusion Matrix
class_names=classes
confusion_mtx = confusion_matrix(target_test, pred_test)
print("confusion matrix=\n",confusion_mtx)

plot_confusion_matrix(confusion_mtx, class_names)

"""### Using Data Augmentation in order to increase the dog and cat classes dataset"""

def data_augmentation(image):
  images = np.array([])
  images = Rotation(image, n_new_img=3, rotating_factor=20)
  images1 = flip(image, n_new_img=2)
  images = np.append(images, images1, axis=0)
  images2 = Scale(image, zoom_factor=0.3, n_new_img=2)
  images = np.append(images, images2, axis=0)
  images3 = Brightness(image, _brightness_range=[0.4,1.5], n_new_img=2)
  images = np.append(images, images3, axis=0)
  return images

data_augmentation(image)

# testing
images1 = image.reshape(1, 3, 1090, 1600)
images = data_augmentation(image)
# plot_image(images, n_images=8)

image.shape

dogs = np.array([5]*9)
cats = np.array([3]*9)

count_dog = 0
count_cat = 0

for i in range(len(reduced_data_labels_agg)):
  if index2label[reduced_data_labels_agg[i]] == 'dog':
    count_dog += 1
  elif index2label[reduced_data_labels_agg[i]] == 'cat':
    count_cat += 1  
print(count_dog, count_cat)

reduced_data_array_agg.shape

n_dog = 0
n_cat = 0
data_array_agg_fixed = np.array([])
data_labels_agg_fixed = np.array([])

for i in range(len(reduced_data_labels_agg)):
  image = reduced_data_array_agg[i].reshape(1, 32, 32, 3)
  if data_array_agg_fixed.shape == (0, ):
    data_labels_agg_fixed = reduced_data_labels_agg[i]
    data_array_agg_fixed = reduced_data_array_agg[i]
    
  else:
    data_array_agg_fixed = np.append(data_array_agg_fixed, reduced_data_array_agg[i], axis=0)
    data_labels_agg_fixed = np.append(data_labels_agg_fixed, reduced_data_labels_agg[i])
    
    if index2label[reduced_data_labels_agg[i]] == 'dog':
      n_dog += 1
      if n_dog <= 500:
        images = data_augmentation(image)
        images = images.reshape(9, 3, 32, 32)
        for j in range(9):
          data_array_agg_fixed = np.append(data_array_agg_fixed, images[j], axis=0)
        data_labels_agg_fixed = np.append(data_labels_agg_fixed, dogs)
    elif index2label[reduced_data_labels_agg[i]] == 'cat':
      n_cat += 1
      if n_cat <= 500:
        images = data_augmentation(image)
        images = images.reshape(9, 3, 32, 32)
        for j in range(9):
          data_array_agg_fixed = np.append(data_array_agg_fixed, images[j], axis=0)
        data_labels_agg_fixed = np.append(data_labels_agg_fixed, cats)

data_array_agg_fixed = np.array(data_array_agg_fixed)
data_labels_agg_fixed = np.array(data_labels_agg_fixed)

data_array_agg_fixed = data_array_agg_fixed.reshape((-1, 3, 32, 32))

train_data_loader_new = to_dataloader(data_array_agg_fixed, data_labels_agg_fixed, batch_size=128)

net = Net()

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(net.parameters(), lr=0.001)
train_acc, test_acc, pred_test, target_test = train(net, criterion, optimizer, train_data_loader_new, test_data_loader, n_epochs)

plot_train_test_acc(train_acc, test_acc)

# Confusion Matrix
class_names=classes
confusion_mtx = confusion_matrix(target_test, pred_test)
print("confusion matrix=\n",confusion_mtx)

plot_confusion_matrix(confusion_mtx, class_names)