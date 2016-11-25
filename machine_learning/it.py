
# coding: utf-8

# # Programming Exercise 4: Neural Networks Learning

# In[1]:

get_ipython().magic('matplotlib inline')
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import scipy.io #Used to load the OCTAVE *.mat files
import scipy.misc #Used to show matrix as an image
import matplotlib.cm as cm #Used to display images in a specific colormap
import random #To pick random images to display
import scipy.optimize #fmin_cg to train neural network
import itertools
from scipy.special import expit #Vectorized sigmoid function


# ## Visualizing the data

# ### This visualization is (roughly) unchanged, from https://github.com/kaleko/CourseraML

# In[2]:

#Note this is actually a symlink... same data as last exercise,
#so there's no reason to add another 7MB to my github repo...
datafile = 'data/ex4data1.mat'
mat = scipy.io.loadmat( datafile )
X, Y = mat['X'], mat['y']
#Insert a column of 1's to X as usual
X = np.insert(X,0,1,axis=1)
print( "'Y' shape: %s. Unique elements in y: %s"%(mat['y'].shape,np.unique(mat['y'])) )
print( "'X' shape: %s. X[0] shape: %s"%(X.shape,X[0].shape) )
#X is 5000 images. Each image is a row. Each image has 400 pixels unrolled (20x20)
#y is a classification for each image. 1-10, where "10" is the handwritten "0"


# In[3]:

def tenToZero(digit):
    if digit == 10: return 0
    else: return digit
Y = np.vectorize(tenToZero)(Y)
YBool = np.zeros((Y.shape[0],10)) # because ten categories
for i in range(Y.shape[0]):
    YBool[i,Y[i]]=1
YBool;


# In[4]:

def getDatumImg(row):
    """
    Function that is handed a single np array with shape 1x400,
    crates an image object from it, and returns it
    """
    width, height = 20, 20
    square = row[1:].reshape(width,height)
    return square.T
    
def displaySomeData(indices_to_display = None):
    """
    Function that picks 100 random rows from X, creates a 20x20 image from each,
    then stitches them together into a 10x10 grid of images, and shows it.
    """
    width, height = 20, 20
    nrows, ncols = 10, 10
    if not indices_to_display:
        indices_to_display = random.sample(range(X.shape[0]), nrows*ncols)
    big_picture = np.zeros((height*nrows,width*ncols))
    irow, icol = 0, 0
    for idx in indices_to_display:
        if icol == ncols:
            irow += 1
            icol  = 0
        iimg = getDatumImg(X[idx])
        big_picture[irow*height:irow*height+iimg.shape[0],icol*width:icol*width+iimg.shape[1]] = iimg
        icol += 1
    fig = plt.figure(figsize=(6,6))
    img = scipy.misc.toimage( big_picture )
    plt.imshow(img,cmap = cm.Greys_r)


# In[5]:

displaySomeData()


# ## Architecture

# In[6]:

def mkRandCoeffsSymmetric(randUnifCoeffs):
    return randUnifCoeffs*2 - 1 # rand outputs in [0,1], not [-1,1]
def mkRandCoeffsSmall(randUnifCoeffs):
    a,b = randUnifCoeffs.shape
    e = np.sqrt(6) / np.sqrt(a+b)
    return randUnifCoeffs * e


# In[7]:

def mkRandCoeffs(lengths):
    # lengths :: [Int] lists input, hidden, and output layer lengths
    # and it does NOT include the constant terms
    acc = []
    for i in range(len(lengths)-1):
        acc.append(mkRandCoeffsSmall(mkRandCoeffsSymmetric(
                np.random.rand(lengths[i+1],lengths[i]+1) ) ) )
    return acc
mkRandCoeffs([3,2,1]) # example: 2 matrices, 3 layers (1 hidden)


# ## Forward-propogation

# In[8]:

def prependUnityColumn(colvec):
    return np.insert(colvec,0,1,axis=0)
test = np.array([[3,4]]).T
# (test, prependUnityColumn(test)) # test


# In[9]:

def forward(nnInputs,coeffMats):
    # nnInputs :: column vector of inputs to the neural net
    # coeffMats :: list of coefficient matrices
    latents = ["input layer latent vector does not exist"] # per-layer inputs to the sigmoid function
      # The last layer has the same number of latent and activ values.
      # Each hidden layer's latent (aka weighted input) vector is 1 neuron shorter than the corresponding activs vector.
      # HOWEVER, to make indexing the list of latents the same as the list of activs, 
          # I give it a dummy string value at position 0.
    activs = [nnInputs] # per-layer outputs from the sigmoid function
    for i in range(len(coeffMats)):
        newLatent = coeffMats[i].dot(activs[i])
        latents.append( newLatent )
        newActivs = expit( latents[i+1] )
        if i<len(coeffMats)-1: newActivs = prependUnityColumn(newActivs)
            # nnInputs already has the unity column.
            # The hidden layer activations get it prepended here.
            # The output vector doesn't need it.
            # Activations ("a") have it, latents ("z") do not.
        activs.append( newActivs )
    prediction = np.argmax(activs[-1])
    return (latents,activs,prediction)


# In[10]:

# It works! (The smaller test's arithmetic is even human-followable.)
forward(np.array([[1,2,3]]).T
       , [np.array([[5,2,0]])]
       )
x = forward(  np.array([[1,1,2]]).T
        , [np.array([[1,2,3]
                    ,[4,5,6]])
           , np.array([[3,2,1]
                      ,[5,5,5]])
          ] )


# ## Cost

# In[11]:

# contra tradition, neither cost needs to be scaled by 1/|obs|
def mkErrorCost(observed,predicted):
    return np.sum( # -y log hx - (1-y) log (1-hx)
        (-1) * observed * np.log(predicted)
        - (1 - observed) * np.log(1 - predicted)
    )
def mkRegularizationCost(coeffMats):
    flatMats = [np.delete(x,0,axis=1).flatten()
                for x in coeffMats]
    return np.concatenate(np.array(flatMats)**2).sum()
# mkRegularizationCost([np.eye(1),np.eye(2)]) # should be 1
# mkRegularizationCost([np.array([[10,1,2]])]) # should be 5
mkErrorCost(np.array([[1,0]]).T  # should be small
           , np.array([[.99,0.01]]).T);


# In[12]:

def testCost():
    nnInputs = np.array([[1,2,-1]]).T
    observedCategs = np.array([[1,0]])
    Thetas = mkRandCoeffs([2,2,2])
    latents,activs,predicts = forward(nnInputs,Thetas)
    ec = errorCost(observedCategs,activs[-1])
    rc = regularizationCost(Thetas)
# testCost()


# ## Errors, and back-propogating them

# In[13]:

def expitPrime(colVec): return expit(colVec) * expit(1-colVec)
    # the derivative of ("expit" = the sigmoid function)


# In[15]:

def mapShape(arrayList): return list(map(np.shape,arrayList))
def mkErrors(coeffMats,latents,activs,yVec):
    "Returns a list of error vectors, one per layer."
    nLayers = len(latents)
    errs = list( range( nLayers ) ) # dummy values, just for size
    errs[0] = "input layer has no error term"
    errs[-1] = activs[-1] - yVec # the last layer's error is different
    for i in reversed( range( 1, nLayers - 1 ) ): # indexing activs
        errs[i] = ( coeffMats[i].T.dot( errs[i+1] )[1:] 
                    # [1:] because the 0th is the "error" in the constant unity neuron
                    * expitPrime(latents[i]) )
    for i in range(1,len(errs)): errs[i] = errs[i].reshape((-1,1))
    return errs
def testMkErrors(): return mkErrors(
      [np.eye(2),np.eye(2),np.ones((2,2))]
    , ["nonexistent", np.array([[1,1]]).T,np.array([[1,1]]).T, "unimportant"]
    , [np.array([[1,1]]).T,np.array([[1,1]]).T,np.array([[1,1]]).T,np.array([[2,3]]).T]
    , np.array([[2,3.1]]).T
    )
def testMkErrors2(): return mkErrors(
      [np.eye(2),np.ones((2,2))]
    , ["nonexistent", np.array([[1,1]]).T, "unimportant"]
    , [np.array([[1,1]]).T,np.array([[1,1]]).T,np.array([[2,3]]).T]
    , np.array([[2,3.1]]).T
    )
testMkErrors2()


# In[16]:

def mkDeltaMats(errs,activs):
    "Compute the change in coefficient matrices implied by the error and activation vectors from a given observation."
    nMats = len(activs)-1
    acc = list(range(nMats)) # start with dummy values
    for i in range(nMats):
        acc[i] = errs[i+1].dot( activs[i].T )
    return acc
def testMkDeltaMats(): # result should be 3 by 3
    errs = ["nonexistent",np.ones((3,1))]
    activs = [np.ones((3,1)),"unimportant"]
    return mkDeltaMats(errs,activs)
testMkDeltaMats()


# ## Putting it together?

# In[17]:

def obsCoeffDeltas(coeffMats,X,YBool):
    latents,activs,_ = forward(X,coeffMats)
    errs = mkErrors(coeffMats,latents,activs,YBool)
    return mkDeltaMats(errs,activs)


# In[18]:

lengths = [400,25,10]
initCoeffs = mkRandCoeffs( lengths )
obsCoeffDeltas(
    initCoeffs,
    X[0].reshape((-1,1)),
    YBool[0].reshape((-1,1)))


# In[ ]:



