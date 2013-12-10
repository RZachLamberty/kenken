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

import LatinSquare as LS
import KenKenCage as KKC

# ==================================================================== #
#   Module Constants                                                   #
# ==================================================================== #
EQUALS = 0
PLUS = 1
TIMES = 2
MINUS = 3
DIVIDE = 4


# ==================================================================== #
#   Kenken class object                                                #
# ==================================================================== #
class KenKen():
    """
    A ken ken problem object.  The object itself is a collection of
    rules of the form
        
        ( square list, operation, result )
    
    as well as some other information.  The size of the kenken puzzle is
    N x N
    """
    
    #   Constructor / Destructor  --------------------------------------
    def __init__( self, N = 6 ):
        """
        Given the kenken puzzle size, generate a random kenken puzzle.
        Variables:
            ruleList
            size
            solution
            solvableDic
            displayedNumbers
        """
        
        #   Creating a puzzle
        self.ruleList = []
        self.size = N
        self.randomKenKenInit()
        
        #   Solving a puzzle
        self.possDic = {}
        self.solveDic = {}
        self.possDicInit()
        self.solveDicInit()
        
        #   Displaying a puzzle
        self.displayedNumbers = {}
    
    
    def __del__( self ):
        """
        Deallocate anything that needs to be, and maybe save to file (later)
        """
        pass
    
    
    def copy( self ):
        """
        Make a regular kenken, but then update everything by copying it
        """
        copyK = KenKen( self.size )
        copyK.ruleList = self.ruleList
        copyK.size = self.size
        copyK.solveDic = self.solveDic
        copyK.displayedNumbers = self.displayedNumbers
        
        return copyK

    
    #   Overloaded operators
    #       __str__, __getitem__, __iter__
    
    
    #   Setters  -------------------------------------------------------
    def randomKenKenInit( self ):
        """
        Create the rules defining this instance of a kenken puzzle
        """
        self.solution = LS.randomLatinSquare( self.size )
        kenkenCage = KKC.KenKenCage( self.size )
        cages = kenkenCage.getCageList()
        self.createRules( cages )
    
    
    def solveDicInit( self ):
        """
        Set up an object which contains nodelist : possval lists
        """
        for rule in self.ruleList:
            self.solveDic[ tuple( rule[0] ) ] = []
    
    
    def possDicInit( self ):
        """
        Add 1 - 9 to every dictionary
        """
        for i in range( 9 ):
            for j in range( 9 ):
                self.possDic[ i, j ] = [ 1, 2, 3, 4, 5, 6, 7, 8, 9 ]
        
    
    def removePossValue( self, node, value ):
        """
        Remove the value from the possDic for a given node
        """
        try:
            self.possDic[ node ].remove( value )
        except:
            pass
    
    
    def addDisplayValue( self, node, value ):
        """
        Add the solved value to the possDic with key node
        """
        self.displayedNumbers[ node ] = value
    
    
    def updateSolveDic( self, solveDic ):
        """
        given a dictionary of node : list pairs, update the
        self.solveDic
        """
        self.solveDic.update( solveDic )
    
    
    def updatePossDic( self, possDic ):
        """
        given a dictionary of node : list pairs, update the
        self.possDic
        """
        self.possDic.update( possDic )
        
        for (node, nodeList) in possDic.iteritems():
            if len( nodeList ) == 1:
                self.addDisplayValue( node, nodeList[0] )

    
    #   Getters  -------------------------------------------------------
    def getSolveValues( self, nodeList ):
        """
        Exactly what you expect
        """
        return self.solveDic[ nodeList ]
        
    
    def getPossValues( self, node ):
        """
        Return the possible solution values at node
        """
        return self.possDic[ node ]
    
    
    def getDisplayDic( self ):
        return self.displayedNumbers
    
    
    #   Others  --------------------------------------------------------
    def createRules( self, cages ):
        """
        Create a random set of rules for the latin square given by
        self.solution under the cage structure defined in cages
        """
        
        for cage in cages:
            
            if len( cage ) == 1:
                operation = EQUALS
                value = self.solution[ cage[0] ]
                
            else:
                
                if len( cage ) == 2:
                    operation = random.randint(1,4)
                    values = sorted( [ self.solution[ index ] for index in cage ] )
                    
                    if operation == PLUS:
                        value = scipy.sum( values )
                    
                    elif operation == MINUS:
                        value = values[1] - values[0]
                        
                    elif operation == TIMES:
                        value = scipy.prod( values )
                        
                    elif operation == DIVIDE:
                        vMin, vMax = values
                        if vMax % vMin == 0:
                            value = vMax / vMin
                        else:
                            operation = MINUS
                            value = vMax - vMin
                    
                    else:
                        raise ValueError, "Operation -- I'm the doctor for you"
                        
                
                else:
                    operation = random.randint( 1, 2 )
                    values = sorted( [ self.solution[ index ] for index in cage ] )
                        
                    if operation == PLUS:
                        value = scipy.sum( values )
                    
                    elif operation == TIMES:
                        value = scipy.prod( values )
                    
                    else:
                        raise ValueError, "Operation not possible for this list, dog"
                
            self.ruleList.append( (cage, operation, value) )
    
    
    def isSolved( self ):
        """
        Check every node to see if it is solved
        """
        for i in range( self.size ):
            for j in range( self.size ):
                if not self.nodeSolved( (i,j) ):
                    return False
        
        return True
    
    
    def nodeSolved( self, node ):
        """
        Check and see if an individual node is solved
        """
        return len( self.possDic[ node ] ) == 1
