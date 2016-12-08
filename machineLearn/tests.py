import unittest

def importTheData():
    datafile = 'digits,handwritten.mat'
    mat = scipy.io.loadmat( datafile )
    X, Y = mat['X'], mat['y']
    X = np.insert(X,0,1,axis=1)    # Insert a column of 1's
    Y = np.vectorize(tenToZero)(Y)
    YBool = digitVecToBoolArray(Y)
    return (X,YBool)

class TheTestCase(unittest.TestCase):
    def testTenToZero(self):
        assert ( list(map(tenToZero, range(1,11))) ==
          list(range(1,10)) + [0] ), "problem in tenToZero"

    def testFlattenCoeffs(self):
        assert np.array_equal( 
            flattenCoeffs( [np.eye(1),np.eye(2)] )
            , np.array( [1,1,0,0,1] )
        ), "problem in flatten"

    def testRavelCoeffs(self):
        makeIt = ravelCoeffs( [1,2,2]
                              , np.array( [ 1,2,3,4,
                                            11,12,13,14,15,16 ] ) )
        mustBe = [ np.array( [[1,2], [3,4]] )
                 , np.array([[11, 12, 13], [14, 15, 16]] )
        ]
        assert np.array_equal(makeIt[0], mustBe[0]), "problem in ravel"
        assert np.array_equal(makeIt[1], mustBe[1]), "problem in ravel"

    def testMkErrorCost(self):
        X,YBool = importTheData()
        lengths = [400,26,10]
        coeffVec = flattenCoeffs( mkRandCoeffs( lengths ) )
        mkErrorCost(coeffVec,lengths,X,YBool) # just make sure it runs
