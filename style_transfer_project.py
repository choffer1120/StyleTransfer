# -*- coding: utf-8 -*-
"""Style Transfer Project

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1-paI5zfTNQcP4-SFylpwLzVtgbvgpEc3
"""

import PIL.Image
import matplotlib.pyplot as plt
from keras.preprocessing.image import load_img, img_to_array
import numpy as np
from scipy.optimize import fmin_l_bfgs_b, minimize
import time
from keras.applications import vgg19
from keras import backend as K
from PIL import Image
import scipy.misc
import tensorflow as tf
import cv2

"""
List the paths of your base and sytle images, as well as the number of iterations 
(200 seems to work well enough without needing to wait a super long time for results)
"""
base_image_path = 'nyc.jpg'
style_image_path = 'rain_princess.jpg' 
result_prefix = './output'
iterations = 100

# These are the weights of the different loss components
style_weight = 1.0
content_weight = 0.05

# Image dimensions
target_width = 450
target_height = 300
total_size = target_width * target_height

mean_sub = np.array([123.68, 116.779, 103.939], dtype=np.float32) #weight normalization from ImageNet

preprocess = lambda x: (np.expand_dims(np.array(x), 0) - mean_sub)[:,:,:,::-1]
convert_back = lambda x: np.clip(x.reshape((1, target_height, target_width, 3))[:,:,:,::-1] + mean_sub, 0, 255)


# Load in out images
base_image = K.variable(preprocess(Image.open(base_image_path)))
style_image = K.variable(preprocess(Image.open(style_image_path)))

#Create a placeholder for the generated image
generated_image = K.placeholder((1, target_height, target_width, 3))

#Put all 3 together for our tensor
input_tensor = K.concatenate([base_image, style_image, generated_image], axis=0)

# build the VGG19 network with our 3 images as input the model will be loaded with pre-trained ImageNet weights
model = vgg19.VGG19(input_tensor=input_tensor, weights='imagenet', include_top=False)

def get_gram(input_tensor):
    a = tf.reshape(input_tensor, [-1, int(input_tensor.shape[-1])])
    return tf.matmul(a, a, transpose_a=True)
  
def test_gram(input_array):
  a = np.reshape(input_array, [-1, int(input_array.shape[-1])])
  return np.matmul(a, a.transpose())

def style_loss(style, combination):
    return tf.reduce_sum(tf.square(get_gram(style) - get_gram(combination))) / (36. * (total_size ** 2))
  
def test_style_loss(img1, img2, test_height, test_width):
    test_size = test_height * test_width
    return np.sum(np.power((test_gram(img1) - test_gram(img2)),2)) / (36. * (test_size ** 2))

def content_loss(base, combination):
    return tf.reduce_sum(tf.square(combination - base))
  
def test_content_loss(base, combination):
    return np.sum(np.power((combination - base), 2))

#layers we want to change in original
content_layer = 'block5_conv2' 

#layers we want to draw from in the style image
style_layers = ['block1_conv1', 'block2_conv1', 'block3_conv1', 'block4_conv1', 'block5_conv1']

#Definte out loss variable as a sum of the content and style losses
loss = K.variable(0.)

loss += content_weight * content_loss(model.get_layer('block5_conv2').output[0, :, :, :], model.get_layer('block5_conv2').output[2, :, :, :])
loss += sum([style_loss(model.get_layer(layer_name).output[1, :, :, :], 
  model.get_layer(layer_name).output[2, :, :, :]) for layer_name in style_layers]) * (style_weight / len(style_layers))

#Accessor functions to get the loss and gradients when optimizing
def get_loss(x):
    x = x.reshape((1, target_height, target_width, 3))
    return loss_and_gradient_function([x])[0] 

def get_gradients(x):
    x = x.reshape((1, target_height, target_width, 3))
    return loss_and_gradient_function([x])[1].flatten().astype('float64')

loss_and_gradient_function = K.function([generated_image], [loss] + K.gradients(loss, generated_image))


#Actual Style Transfer! YAY!
def run_style_transfer():
  x=preprocess(Image.open(base_image_path))

  for i in range(iterations + 1):
      x, min_val, info = fmin_l_bfgs_b(get_loss, x.flatten(), fprime=get_gradients, maxfun=20)

      if (i % 20 == 0):
          img = convert_back(x.copy())[0]
          fname = result_prefix + '_at_iteration_%d.png' % i
          scipy.misc.toimage(img).save(fname)
          print("Saved at iteration ", i)
    
run_style_transfer()




"""# Test Cases

Test gram matrix, content loss, style loss, preprocessing and a single iteration
"""

'''
Simple test to ensure were getting a singular output and matrix multiplcation is working
'''
def test_case_gram_matrix():
    a = np.array([[[1]],[[2]],[[3]]])
    
    result = test_gram(a)
    expected = np.array([[1,2,3], [2,4,6], [3,6,9]])
    assert result.all() == expected.all()

'''
Only difference between two images is a single pixel black dot, since it's across all pixels,
the output will be 3
'''
def test_case_content_loss():
    dot = cv2.imread("dot.png")/1.0
    blank = cv2.imread("blank.png")/1.0
    assert test_content_loss(dot, blank) == 3.0
    assert test_content_loss(blank, dot) == 3.0

'''
Only difference between two images is a single pixel black dot, dimensions of each are 10x10
'''
def test_case_style_loss():
    dot = cv2.imread("dot.png")/1.0
    blank = cv2.imread("blank.png")/1.0

    test_img_height = 10
    test_img_width = 10

    #already test gram so can add that here
    expected = np.sum(np.power((test_gram(dot) - test_gram(blank)),2))
    expected = expected / (36.0 * test_img_height**2 * test_img_width**2)

    assert test_style_loss(dot, blank, test_img_height, test_img_width) == expected
    assert test_style_loss(blank, dot, test_img_height, test_img_width) == expected

def test_case_preprocess_and_convert_back():
    original = cv2.imread("nyc.jpg")/1.0
    processed = cv2.imread("nyc.jpg")/1.0
    
    processed = preprocess(processed)
    processed = convert_back(processed)
    
    assert original.all() == processed.all()

'''
Testing that the first iteration of style transfer works correctly

NEED TO CHANGE THE PATHS OF CONTENT AND STYLE to nyc.jpg and rain_princess.jpg!!!
'''
def test_case_nyc_first_iteration():
  ## IMPORTANT ##
  # Change base image path to nyc.jpg
  # Change style image path to rain_princess.jpg
  x=preprocess(Image.open(base_image_path))
  x, min_val, info = fmin_l_bfgs_b(get_loss, x.flatten(), fprime=get_gradients, maxfun=20)
  
  output_image = np.around(convert_back(x.copy())[0]).astype(int)
  expected_image = np.array(Image.open("nycToRain_output_at_iteration_0.png"))
 
  #just check that random pixels are equal
  assert output_image[0][0][0] == expected_image[0][0][0]
  assert output_image[127][205][1] == expected_image[127][205][1]
  assert output_image[99][199][2] == expected_image[99][199][2]

'''
Test Cases!!
'''
# test_case_gram_matrix()
# test_case_content_loss()
# test_case_style_loss()
# test_case_preprocess_and_convert_back()
# test_case_nyc_first_iteration()