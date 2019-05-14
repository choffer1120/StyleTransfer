# Running the code is a lot easier and quicker on Google Colab! Please see below!

Hi there, in order to not spend 6 hours of CPU time one each trial for Style Transfer, I used Google Colab, which is basically Google Docs + Jupyter Notebooks that run on free Google cloud gpus, so I figure it will be much easier for you guys to do the same.

Steps to get it running.
- Go to the colab link: https://colab.research.google.com/drive/1-paI5zfTNQcP4-SFylpwLzVtgbvgpEc3
- In Colab, turn the GPU on: Edit > Notebook settings > Hardware Accelerators > Select GPU
- Insert base and test images: On far left there is a little arrow > click arrow > click files > click upload > upload all of the images from my submission (or your own 300x450 images if you want to try others)
- Should be good to go form there! If there are any issues you can defintely reach out, or you can simply run the included python file (will be kind of slow on CPU though)


### Test cases
To run the test cases, you can just uncomment a particular case at the bottom of the file. You will also probably want to comment out the "run_style_transfer()" command too so your not rerunning a whole style transfer when looking at the test cases.
