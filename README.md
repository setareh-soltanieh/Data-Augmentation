One of the most critical problems in solving a classification problem is a limited dataset. In this regard, data augmentation comes in handy. 
We produce new images from a sample input image in data augmentation using different methods. These new images may not differ from the input image from human eyes, but the program will vary these images from the input image. 
Here our data augmentation methods consist of: 
1. Flipping 
2. Rotating
3. Scaling 
4. Brightening

These methods are applied on test.jpg 
To see data augmentation's effect on classification, we use the Cifar10 dataset, found at https://www.cs.toronto.edu/~kriz/cifar.html. 
In this dataset, we have 60000 images of 10 different classes. We use 5000 images in each class except dog and cat class that we only use 500 images. 
After finishing the classification using a CNN, we applied the data augmentation method on the dog and cat class to have 5000 images. 
