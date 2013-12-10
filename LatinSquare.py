########################################################################
#                                                                      #
#   LatinSquare.py                                                     #
#       Created: Jan 6, 2013                                           #
#                                                                      #
#       A class to generate latin squares                              #
#                                                                      #
########################################################################

import scipy
import random

def randomLatinSquare( N = 6 ):
    """
    Return a randomized latin square of dimensions N x N
    """
    return notSoRandom()
    #return bruteForceLatinSquare( N )


def notSoRandom():
    """
    A test square
    """
    a = scipy.array(                        \
           [[ 2, 8, 6, 1, 3, 9, 7, 4, 5 ],  \
            [ 1, 7, 4, 3, 6, 2, 5, 9, 8 ],  \
            [ 4, 2, 5, 7, 9, 8, 1, 6, 3 ],  \
            [ 8, 4, 3, 9, 1, 6, 2, 5, 7 ],  \
            [ 5, 6, 9, 4, 2, 3, 8, 7, 1 ],  \
            [ 9, 3, 8, 2, 7, 5, 4, 1, 6 ],  \
            [ 7, 9, 2, 6, 5, 1, 3, 8, 4 ],  \
            [ 3, 1, 7, 5, 8, 4, 6, 2, 9 ],  \
            [ 6, 5, 1, 8, 4, 7, 9, 3, 2 ]]  \
        )
    return a
    

def bruteForceLatinSquare( N = 6 ):
    """
    A brute force means of calculating a random square of size N x N
    """
    a = scipy.zeros( (N,N) )
    intList = range( 1, N + 1 )
    
    for i in range( N ):
        for j in range( N ):
            
            random.shuffle( intList )
            ind = 0
            
            while a[i,j] == 0:
                randInt = intList[ ind ]
                
                if randInt not in a[i,:j] and randInt not in a[:i,j]:
                    a[i,j] = randInt
                    
                else:
                    ind += 1
    
    return a
