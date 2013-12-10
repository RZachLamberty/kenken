########################################################################
#                                                                      #
#   SolveKenKen.py                                                     #
#       Created: Jan 6, 2013                                           #
#                                                                      #
#       A module for solving ken ken problems                          #
#                                                                      #
########################################################################

import copy
import scipy
import itertools

import KenKenClass as K
import DisplayKenKen as DKK
from KenKenClass import EQUALS, PLUS, TIMES, MINUS, DIVIDE


class KenKenSolver():
    """
    An object to hold a local copy of the rule list and solve dictionary
    """
    
    #   Constructor / Destructor  --------------------------------------
    def __init__( self, k, showOnFly = False ):
        """
        Given the kenken object, generate a solver object
        """
        self.k = k
        self.size = k.size
        self.ruleList = list( k.ruleList )
        self.possDic = copy.deepcopy( k.possDic )
        self.solveDic = copy.deepcopy( k.solveDic )
        self.solved = False
        
        self.showOnFly = showOnFly
        if self.showOnFly == True:
            self.copyK = k.copy()
            self.displayK = DKK.KenKenDisplay( self.copyK )
    
    
    def __del__( self ):
        """
        Deallocate anything that needs to be
        """
        pass
    
    
    #   Major solver routines  -----------------------------------------
    def solveKenKen( self, shouldPrint = False ):
        """
        Given a kenken object k (primarily the rules and solveDic) try to
        figure out the solution (which is also contained in the kenken
        object, for what it's worth)
        """
        
        def updatePrint( string ):
            if shouldPrint == True:
                print string
        
        self.kenkenSolved()
        exit = 'n'
        while not self.solved and exit != 'y' and exit != '':
            
            solveDicSizeBefore = scipy.sum( [ len( self.solveDic[ key ] ) for key in self.solveDic ] )
            
            updatePrint( "Cleaning Singles" )
            self.cleanSingles()
            
            updatePrint( "Paring Values" )
            self.pareValues()
            
            #self.singleValueInRules()
            
            updatePrint( "Checking subgroups" )
            self.subGroups()
            
            updatePrint( "Checking necessary values" )
            self.necessaryRuleValues()
            
            self.kenkenSolved()
            
            solveDicSizeAfter = scipy.sum( [ len( self.solveDic[ key ] ) for key in self.solveDic ] )
            
            if solveDicSizeBefore == solveDicSizeAfter:
                print '\n\n\t\tNo Change This Cycle!'
                exit = raw_input( 'Exit? [y/n] ' )
        
        self.k.updateSolveDic( self.solveDic )
        self.k.updatePossDic( self.possDic )
        
        print '\n\n\t\tSOLVED!'
        
    
    def cleanSingles( self ):
        """
        Just set all of the squares which are isolated to the value in
        their rule
        """
        equalsRules = [ rule for rule in self.ruleList if rule[1] == EQUALS ]
        
        for rule in equalsRules:
            self.ruleList.remove( rule )
            nodeList, e, val = rule
            node = nodeList[0]
            self.setNodeEqual( node, val )
            self.solveDic[ tuple(nodeList) ] = [ (val,) ]
        
        if self.showOnFly == True:
            self.updateAndDisplay()
    
    
    def pareValues( self ):
        """
        Take a given rule and establish which values are even possible
        in the squares associated with that rule
        """
        for rule in self.ruleList:
            nodeList, operation, value = rule
            l = len( nodeList )
            
            #   Figure out what the possible combinations of numbers are
            #   that will satisfy the rule in the first place
            solveSet = [ [ possValOrder for possValOrder in itertools.permutations( possVals )      \
                           if self.possValOrderFits( nodeList, possValOrder ) ]                     \
                           for possVals in self.possibleValuesForOperation( operation, value, l )   ]
           
            #   Flatten and remove duplicates
            tempSolveSet = [ ]
            
            for el in solveSet:
                tempSolveSet += el
            solveSet = list( tempSolveSet )
            
            solveSet = removeDuplicates( solveSet )
            
            del( tempSolveSet )
            
            #   Update solveDic and possDic
            self.updateSolveAndPoss( solveSet, nodeList )
        
        if self.showOnFly == True:
            self.updateAndDisplay()


    def possibleValuesForOperation( self, operation, value, l ):
        """
        Return a generator object which will cycle through the allowed
        possible values of l object
        """
        if operation == EQUALS:
            raise ValueError, "Equals rule that wasn't removed"
            
        elif operation == PLUS:
            x = itertools.combinations_with_replacement( range( 1, self.size + 1 ), l )
            return ( el for el in x if ( scipy.sum( el ) == value ) )
            
        elif operation == TIMES:
            x = itertools.combinations_with_replacement( range( 1, self.size + 1 ), l )
            return ( el for el in x if ( scipy.product( el ) == value ) )
            
        elif operation == MINUS:
            x = itertools.combinations( range( 1, self.size + 1 ), 2 )
            return ( el for el in x if el[1] - el[0] == value )
            
        else:#operation == DIVIDE:
            x = itertools.combinations( range( 1, self.size + 1 ), 2 )
            return ( el for el in x if float(el[1]) / el[0] == value )
    
    
    def possValOrderFits( self, nodeList, possValOrder ):
        """
        Given a list of nodes and a specific order for those values,
        determine whether or not those values can go in those nodes
        """
        
        #   Restrict the allowed values in a given set of nodes
        #   to combinations which are subsests of these allowed
        #   values AND valid given the state of the solve
        #   dictionary (i.e avoid overlaps in the possible 
        #   solution itself, contain only numbers already 
        #   present in the solveDic for the given nodes, and 
        #   don't use any of the solved values, etc.)
        
        for i in range( len( nodeList ) ):
            node = nodeList[ i ]
            possVal = possValOrder[ i ]
            a, b = node
            
            #   Check that this value hasn't already been ruled out
            if possVal not in self.possDic[ node ]:
                return False
            
            #   Check that this value isn't in that row or column
            for j in range( self.size ):
                if ( j != b and self.possDic[ a, j ] == [ possVal ] ) or ( j != a and self.possDic[ j, b ] == [ possVal ] ):
                    return False
            
        #   Check that the suggested arangement of these values 
        #   isn't a problem itself
        invertDic = {}
        for (i,val) in enumerate( possValOrder ):
            node = nodeList[ i ]
            if val not in invertDic:
                invertDic[ val ] = []
            invertDic[ val ].append( node )
        
        for val, nodesWithVal in invertDic.iteritems():
            if len( nodesWithVal ) != 1:
                #   If there are any repetitions among the x or y
                #   component of the nodes inside, reject the values
                for ( node1, node2 ) in itertools.combinations( nodesWithVal, 2 ):
                    if node1[0] == node2[0] or node1[1] == node2[1]:
                        return False
        
        del( invertDic )
        
        return True

    
    def updateSolveAndPoss( self, solveSet, nodeList ):
        """
        Combine the process of declaring all of the solutions allowed
        for a set of nodes and paring the possVals list in the process
        """
        l = len( nodeList )
        self.solveDic[ tuple( nodeList ) ] = solveSet
        
        #   Update possDic
        #   Reduce the lists into the acceptable values in each of
        #   the node slots
        for i in range( l ):
            z = sorted( [ x[ i ] for x in solveSet ] )
            
            z = removeDuplicates( z )
        
            #   Update the solveDic
            self.possDic[ nodeList[ i ] ] = z
    
    
    #def singleValueInRules( self ):
    #    """
    #    Cycle through the rules.  If there are N nodes and only N
    #    possible values, check to see if there are any 
    #    """
    #    #   Trim to allowed combinations available in the rule
    #    #   Look for single instances of a necessary value within a rule
    #    pass


    def subGroups( self ):
        """
        For each rule, row, and column, check to see if there are any
        groups of N squares in which only N values are allowed.
        If such a combination exists, remove those values from the
        solveDic lists of the other nodes in that rule, row, or column
        """
        for rule in self.ruleList:
            if len( rule[0] ) >= 3:
                #self.reduceRule( rule )
                pass
        
        for i in range( self.size ):
            self.reduceRow( i )
            self.reduceColumn( i )
    
    
    def reduceRule( self, rule ):
        """
        Cycle through all combinations of unsolved nodes in a given
        rule.  If there is any subset of N of those nodes for which
        there are only N allowed values, remove those N values from the
        other M - N nodes
        """
        nodeList, operation, value = rule
        l = len( nodeList )
        
        for i in range( 2, l ):
            #   Find all i-length subsets of nodes
            for nodeSet in itertools.combinations( nodeList, i ):
                #   Collect the total allowed values
                allowedVals = self.allowedValueSet( nodeSet )
                if len( allowedVals ) == i:
                    #   Collect the nodes from which we are removing
                    #   values, the remove those values
                    dropNodes = [ node for node in nodeList if node not in nodeSet ]
                    self.dropValsFromNodesRule( allowedVals, dropNodes, tuple(nodeList) )
        
        if self.showOnFly == True:
            self.updateAndDisplay()
    
    
    def reduceRow( self, rowIndex ):
        """
        Cycle through all combinations of unsolved nodes in a given
        row.  If there is any subset of N of those M nodes for which
        there are only N allowed values, remove those N values from the
        other M - N nodes
        """
        rowNodeList = [ ( i, rowIndex ) for i in range(0, self.size) ]
        l = self.size
        
        for i in range( 2, l ):
            #   Find all i-length subsets of nodes in this row
            for rowNodeSubSet in itertools.combinations( rowNodeList, i ):
                #   Collect the total allowed values
                allowedVals = self.allowedValueSet( rowNodeSubSet )
                if len( allowedVals ) == i:
                    #   Collect the nodes from which we are removing
                    #   values, the remove those values
                    dropNodes = [ node for node in rowNodeList if node not in rowNodeSubSet ]
                    self.dropValsFromNodesRow( allowedVals, dropNodes )
        
        if self.showOnFly == True:
            self.updateAndDisplay()
    
    
    def reduceColumn( self, columnIndex ):
        """
        Cycle through all combinations of unsolved nodes in a given
        column.  If there is any subset of N of those M nodes for which
        there are only N allowed values, remove those N values from the
        other M - N nodes
        """
        colNodeList = [ ( columnIndex, i ) for i in range( self.size) ]
        l = self.size
        
        for i in range( 2, l ):
            #   Find all i-length subsets of nodes in this row
            for colNodeSubSet in itertools.combinations( colNodeList, i ):
                #   Collect the total allowed values
                allowedVals = self.allowedValueSet( colNodeSubSet )
                if len( allowedVals ) == i:
                    #   Collect the nodes from which we are removing
                    #   values, the remove those values
                    dropNodes = [ node for node in colNodeList if node not in colNodeSubSet ]
                    self.dropValsFromNodesRow( allowedVals, dropNodes )
        
        if self.showOnFly == True:
            self.updateAndDisplay()
    
    
    def allowedValueSet( self, nodeSet ):
        """
        Given a set of nodes, make a list of all the values in those
        lists
        """
        allowedValList = []
        for node in nodeSet:
            allowedValList += self.possDic[ node ]
        
        #   drop duplicates
        return removeDuplicates( allowedValList )
    
    
    def dropValsFromNodesRule( self, dropVals, dropNodes, nodeList ):
        """
        Given a list of values to be dropped and nodes to drop them,
        perform the simple task of dropping those values from possDic,
        but also drop all rules which have that value at those nodes
        """
        for val, node in itertools.product( dropVals, dropNodes ):
            #   Get the new solveSet
            nodeIndex = nodeList.index[ node ]
            solveSet = [ solution for solution in self.solveDic[ nodeList ] if solution[ nodeIndex ] != val ]
            updateSolveAndPoss( self, solveSet, nodeList )
    
    
    def dropValsFromNodesRow( self, dropVals, dropNodes ):
        """
        Given a list of values to be dropped and nodes to drop them 
        from, go node to node and update the rules containing those
        nodes.  This may be redundant, so be it.
        """
        for val, node in itertools.product( dropVals, dropNodes ):
            #   Get the rule that this node is in, and find all the
            #   solutions which don't contain the value at that node
            for nodeList in self.solveDic.keys():
                if node in nodeList:
                    nodeIndex = nodeList.index( node )
                    solveSet = [ solution for solution in self.solveDic[ nodeList ] if solution[nodeIndex] != val ]
                    self.updateSolveAndPoss( solveSet, nodeList )
                    break
    
    
    '''
    def necessaryRuleValues( self ):
        """
        Cycle through rules, and see if any one rule specifically
        requires one value to be in one row (for example, an L-shaped)
        configuration that multiplies to 14 in which the posssible
        values are
        
            1   2       1   7       2   1       2   7
                7           2           7           1
        
        i.e. there must be a 7 in the second column.  I think the way
        to do this is to cycle through all the allowed solutions as
        listed in solveDic, make a dictionary of all the row or column
        indices associated with that value (including a "None" for
        solutions that do not contain that value).  Then, any element
        whose keys contain only one element in either the row or
        column slot can be zeroed out.  For the example above, assuming 
        that the bottom-left corner is node (0,0), we would have
        
            rowDic = {
                1 : [0,1]
                2 : [0,1]
                7 : [0,1]
            }
            
            columnDic = {
                1 : [0,1]
                2 : [0,1]
                3 : [1]
            }
        
        thus we can be sure that 7 cannot be in any node in column 1
        except those nodes in this rule.
        """
        for (nodeSet, possValList) in self.solveDic.iteritems():
            
            #   Only proceed if this rule hasn't been solved
            goOn = False
            for node in nodeSet:
                if len( self.possDic[ node ] ) != 1:
                    goOn = True
                    break
            
            if goOn:
                rowDic = {}
                columnDic = {}
                for possVal in possValList:
                    #   Update for these values
                    for (i, val) in enumerate( possVal ):
                        x, y = nodeSet[ i ]
                        if val not in rowDic:
                            if i != 0:
                                rowDic[ val ] = [ None ]
                                columnDic[ val ] = [ None ]
                            else:
                                rowDic[ val ] = []
                                columnDic[ val ] = []
                        if x not in rowDic[ val ]:
                            rowDic[ val ].append( x )
                        if y not in columnDic[ val ]:
                            columnDic[ val ].append( y )
                
                #   Add a None to any values which have been seen but are
                #   not in every rule
                for val in rowDic:
                    for possVal in possValList:
                        if val not in possVal:
                            if None not in rowDic[ val ]:
                                rowDic[ val ].append( None )
                            if None not in columnDic[ val ]:
                                columnDic[ val ].append( None )
                
                #   Now find values which have only one row or column option
                #   and zero that value out of other squares in that row
                for val in rowDic:
                    dropVals = [ val ]
                    if len( rowDic[val] ) == 1:
                        #raw_input( '\t' + str( ( nodeSet, val, rowDic ) ) )
                        xCoord = rowDic[ val ][ 0 ]
                        dropNodes = [ (xCoord,j) for j in range(self.size) if (xCoord,j) not in nodeSet ]
                        self.dropValsFromNodesRow( dropVals, dropNodes )
                    if len( columnDic[val] ) == 1:
                        #raw_input( '\t' + str( ( nodeSet, val, columnDic ) ) )
                        yCoord = columnDic[ val ][ 0 ]
                        dropNodes = [ (j,yCoord) for j in range(self.size) if (j,yCoord) not in nodeSet ]
                        self.dropValsFromNodesRow( dropVals, dropNodes )
    '''
    
    def necessaryRuleValues( self ):
        """
        The general statement of this rule is as follows:
        
            If there are N rules which have some *necessary* value only
            in the same N rows or columns, zero out the elements in
            those N rows or columns that are not in those N rules
        
        In practice, we will create dictionaries of the form
        
            { intVal :
                (
                    { xCoordSet :
                        [ rule0, rule1, ... ], ...
                    },
                    { yCoordSet :
                        [ rule0, rule1, ... ], ...
                    },
                )
            }
        
        With these dictionaries, we can cycle through integer values,
        and then the x and y dictionaries for those values, and if any
        set of coordinates has as many rules as coordinates remove that
        value from the nodes in those rows or collumns that are not in
        those rules.
        """
        
        masterDic = {}
        
        for (nodeSet, possValList) in self.solveDic.iteritems():
            
            #   Only proceed if this rule hasn't been solved
            goOn = False
            for node in nodeSet:
                if len( self.possDic[ node ] ) != 1:
                    goOn = True
                    break
            
            rowDic = {}
            columnDic = {}
            
            if goOn:
                for (i,possVal) in enumerate( possValList ):
                    #   Update for these values
                    for (j, val) in enumerate( possVal ):
                        x, y = nodeSet[ j ]
                        if val not in rowDic:
                            if i != 0:
                                rowDic[ val ] = [ None ]
                                columnDic[ val ] = [ None ]
                            else:
                                rowDic[ val ] = []
                                columnDic[ val ] = []
                        if x not in columnDic[ val ]:
                            columnDic[ val ].append( x )
                        if y not in rowDic[ val ]:
                            rowDic[ val ].append( y )
                        
                
                #   Add a None to any values which have been seen but
                #   are not in every rule
                for val in rowDic:
                    for possVal in possValList:
                        if val not in possVal:
                            if None not in rowDic[ val ]:
                                rowDic[ val ].append( None )
                            if None not in columnDic[ val ]:
                                columnDic[ val ].append( None )
                
                #   Now invert to add to the masterDic
                for val in rowDic:
                    xSet = tuple( sorted( rowDic[ val ] ) )
                    if None not in xSet:
                        if val not in masterDic:
                            masterDic[ val ] = ( {}, {} )
                        if xSet not in masterDic[ val ][ 0 ]:
                            masterDic[ val ][ 0 ][ xSet ] = []
                        masterDic[ val ][ 0 ][ xSet ].append( nodeSet )
                    ySet = tuple( sorted( columnDic[ val ] ) )
                    if None not in ySet:
                        if val not in masterDic:
                            masterDic[ val ] = ( {}, {} )
                        if ySet not in masterDic[ val ][ 1 ]:
                            masterDic[ val ][ 1 ][ ySet ] = []
                        masterDic[ val ][ 1 ][ ySet ].append( nodeSet )
        
        #   If there are M rules contained within N ( >= M ) net rows or
        #   columns, zero out all of nodes in those rows or columns
        #   which are not in those rules
        
        def reduceIndices( indexSetGroup ):
            reduceList = []
            for indexSet in indexSetGroup:
                for el in indexSet:
                    if el not in reduceList:
                        reduceList.append( el )
            return tuple( sorted( reduceList ) )
        
        for intVal in masterDic:
            for (i, coordDic) in enumerate( masterDic[ intVal ] ):
                
                #   Construct the coordSet and ruleList
                coordKeys = coordDic.keys()
                for j in range( 1, self.size ):
                    #   Find the minimum overlap among the combinations
                    #   of coordinate kets
                    for indexSetGroup in itertools.combinations( coordKeys, j ):
                        coordSet = reduceIndices( indexSetGroup )
                            
                        #   We have M indices covered by M index
                        #   sets.  Now construct the set of rules
                        #   covered by these M index sets, and see
                        #   if there is the "right" number of rules
                        ruleList = []
                        for indexSet in indexSetGroup:
                            ruleList += coordDic[ indexSet ]
                        
                        if len( coordSet ) == len( ruleList ):
                            for coord in coordSet:
                                #   Generate all the nodes which are not in
                                #   the rule lists, and drop the value from
                                #   those nodes
                                dropNodes = []
                                for k in range( self.size ):
                                    if i == 0:
                                        node = (k, coord)
                                    else:
                                        node = (coord, k)
                                    
                                    isDropNode = True
                                    for ruleNodeSet in ruleList:
                                        if node in ruleNodeSet:
                                            isDropNode = False
                                    
                                    if isDropNode:
                                        dropNodes.append( node )
                                
                                dropVals = [ intVal ]
                                self.dropValsFromNodesRow( dropVals, dropNodes )
        
    
    def updateAndDisplay( self ):
        """
        Update the copyK dictionary, then display it.
        """
        self.copyK.updateSolveDic( self.solveDic )
        self.copyK.updatePossDic( self.possDic )
        self.displayK.drawKenKen( self.copyK )
        raw_input( "Press [Enter] to continue" )

    
    def kenkenSolved( self ):
        """
        Check to see if the kenken has been solved
        """
        def check():
            for ( node, solveList ) in self.possDic.iteritems():
                if len( solveList ) != 1:
                    return False
            
            return True
        
        self.solved = check()
    
    
    #   Utility routines  ----------------------------------------------
    def setNodeEqual( self, node, val ):
        """
        Update the solveDic for the node, then remove the value from all
        of the rows and columns
        """
        i, j = node
        self.possDic[ node ] = [ val ]
        
        for a in range( 9 ):
            if a != j:
                try:
                    self.possDic[ i, a ].remove( val )
                except:
                    pass
            if a != i:
                try:
                    self.possDic[ a, j ].remove( val )
                except:
                    pass


def removeDuplicates( z ):
    """
    Given a possibly unsorted list z, remove duplicate values and return
    the pared down list
    """
    z = sorted( z )
    j = 0
    while j < len( z ) - 1:
        if z[ j ] == z[ j + 1 ]:
            z.pop( j + 1 )
        else:
            j += 1
    
    return z
