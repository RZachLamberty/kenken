########################################################################
#                                                                      #
#   KenKenClass.py                                                     #
#       Created: Jan 6, 2013                                           #
#                                                                      #
#       A class defining the properties of a ken ken puzzle            #
#                                                                      #
########################################################################

import scipy
import random

# ==================================================================== #
#   A kenken puzzle cage object                                        #
# ==================================================================== #
class KenKenCage():
    """
    A ken ken cage object.  The object itself is a collection of
    iterable lists of integer nodes
        
        [ [ (i,j), (k,l), ... ], ... ]
    
    The size of the kenken puzzle needs to be provided to make the cage
    """
    
    #   Constructor / Destructor  --------------------------------------
    def __init__( self, N = 6 ):
        """
        Given the kenken puzzle size, generate a random cage of the
        N x N nodes
        """
        self.kenkenSize = N
        self.cageListInit()
    
    
    def __del__( self ):
        """
        Deallocate anything that needs to be, and maybe save to file (later)
        """
        pass
    
    
    #   Overloaded operators
    #       __str__, __getitem__, __iter__
    
    
    #   Setters
    def cageListInit( self ):
        """
        Generate a random cage covering of an N x N array.  Return as an
        iterable of integer pairs [ (i,j), (k,l), ... ]
        """
        
        N = self.kenkenSize
        self.cageList = []
        
        indexSet = [ (i,j) for i in range( N ) for j in range(N) ]
        
        while indexSet != []:
            
            rootIndex = indexSet.pop( random.randrange( len( indexSet ) ) )
            
            cage = self.growCage( rootIndex, indexSet )
            
            self.cageList.append( cage )
        
        self.consolidateCageList()
    
    
    #   Getters
    def getCageList( self ):
        """
        Just what it says
        """
        return self.cageList
    
    
    #   Others
    def consolidateCageList( self, M = 4 ):
        """
        Cycle through, combining all but M of the equals sites
        """
        def numberOfSingles( cageList ):
            return scipy.sum( [ 1 for cage in cageList if len(cage) == 1 ] )
        
        while numberOfSingles( self.cageList ) > M:
            self.consolidateOneSingle()


    def consolidateOneSingle( self ):
        """
        Just get one down -- try to put them with "small" neighbors
        """
        for cage in self.cageList:
            if len( cage ) == 1:
                break
        
        node = cage[0]
        
        neighborCage = self.smallestNeighborCage( node )
        self.mergeCages( cage, neighborCage )


    def smallestNeighborCage( self, node ):
        """
        Find the cage neighboring node which is smallest
        """
        neighborCage = [ 0, 0, 0, 0, 0, 0, 0, 0, 0 ]
        
        i, j = node
        upNode    = i, j + 1
        downNode  = i, j - 1
        leftNode  = i - 1, j
        rightNode = i + 1, j
        
        for cage in self.cageList:
            if cage != [ node ]:
                if (upNode in cage) or (downNode in cage) or (leftNode in cage) or (rightNode in cage):
                    if len( cage ) < len( neighborCage ):
                        neighborCage = list( cage )
        
        return neighborCage


    def mergeCages( self, cage, neighborCage ):
        """
        pop the two cages listed from the list and combine them
        """
        newCage = sorted( cage + neighborCage )
        self.cageList.remove( cage )
        self.cageList.remove( neighborCage )
        self.cageList.append( newCage )
        

    def growCage( self, rootIndex, indexSet ):
        """
        Given a starting index and a list of remaining available indices,
        try to build a cage of an arbitrary length (let's say we bias our
        choice with a gaussian distribution centered at 3)
        """
        N = self.kenkenSize
        goalLength = self.desiredLength()
        
        cage = [ rootIndex ]
        canGrow = True
        
        while canGrow and ( len( cage ) < goalLength ):
            
            try:
                neighbor = self.findNeighbor( cage, indexSet )
                indexSet.remove( neighbor )
                cage.append(neighbor)
            
            except ValueError:
                canGrow = False
        
        return cage


    def desiredLength( self ):
        """
        Give the desired number of cells in a cage; come back with 2 and 3
        more often than 4, 4 more often than 1, etc.
        """
        r = random.random()
        
        if r < .03:
            return 1
        
        elif r < .388125:
            return 2
        
        elif r < .865625:
            return 3
        
        elif r < .985:
            return 4
        
        elif r < .995:
            return 5
        
        else:
            return 6


    def findNeighbor( self, cage, indexSet ):
        """
        Find a random neighbor of some site in cage that is in indexSet
        """
        N = self.kenkenSize
        
        UP,DOWN,LEFT,RIGHT = 0,1,2,3
        directionList = [UP,DOWN,LEFT,RIGHT]
        
        i = 0
        while i < len( cage ):
            
            #   Pick an index to grow from
            growIndex = cage[ -(i + 1) ]
            a, b = growIndex
            neighborIndex = -1, -1
            
            #   Cycle through directions randomly
            random.shuffle( directionList )
            
            for dir in directionList:
                
                if dir == UP:
                    if b != N - 1:
                        neighborIndex = a, b + 1
                    
                elif dir == DOWN:
                    if b != 0:
                        neighborIndex = a, b - 1
                    
                elif dir == LEFT:
                    if a != 0:
                        neighborIndex = a - 1, b
                    
                else:#dir == RIGHT:
                    if a != N - 1:
                        neighborIndex = a + 1, b
                
                if ( neighborIndex != (-1,-1) ) and ( neighborIndex in indexSet ):
                    return neighborIndex
            
            i += 1
        
        raise ValueError, "Can't grow cage to desired length"
