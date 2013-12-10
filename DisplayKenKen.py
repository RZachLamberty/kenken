########################################################################
#                                                                      #
#   DisplayKenKen.py                                                   #
#       Created: Jan 6, 2013                                           #
#                                                                      #
#       A module for displaying ken ken problems                       #
#                                                                      #
########################################################################

import pygame
import scipy

import KenKenClass as K
from KenKenClass import EQUALS, PLUS, TIMES, MINUS, DIVIDE


# ==================================================================== #
#   Define the colors (RGB), widths, etc.                              #
# ==================================================================== #

BLACK       = [   0,   0,   0 ]
WHITE       = [ 255, 255, 255 ]
BLUE        = [   0,   0, 255 ]
GREEN       = [   0, 255,   0 ]
RED         = [ 255,   0,   0 ]
ORANGE      = [ 255, 165,   0 ]
YELLOW      = [ 255, 255,   0 ]
INDIGO      = [ 147, 112, 219 ]
PURPLE      = [ 160,  32, 240 ]
FULL_PURPLE = [ 255,   0, 255 ]

THIN_WIDTH  = 2
THICK_WIDTH = 5

LABEL_FONT_SIZE = 25
BIG_NUMBER_FONT_SIZE = 75
SMALL_NUMBER_FONT_SIZE = 25

UP, DOWN, LEFT, RIGHT = 0, 1, 2, 3


# ==================================================================== #
#   Our display object                                                 #
# ==================================================================== #

class KenKenDisplay():
    """
    An object which mostly contains the screen information of the
    display
    """
    
    #   Constructor / Destructor  --------------------------------------
    def __init__( self, k, displayTitle = "Draw dat kenken" ):
        """
        Given the kenken object, generate a screen to draw on
        """
        
        #   Initialize the screen
        pygame.init()
        self.size = [ 800, 800 ]
        self.border = 25
        self.sizeX, self.sizeY = self.size
        self.screen = pygame.display.set_mode( self.size )
        pygame.display.set_caption( displayTitle )
        self.screen.fill( WHITE )
        self.updateScreen()
        
        #   Display dimension variables variables
        self.N = k.size
        self.deltaX = ( self.sizeX - 2 * self.border ) / self.N
        self.deltaY = ( self.sizeY - 2 * self.border ) / self.N
        
        #   Font initialization
        self.labelFont = pygame.font.Font( None, LABEL_FONT_SIZE )
        self.bigNumberFont = pygame.font.Font( None, BIG_NUMBER_FONT_SIZE )
        self.smallNumberFont = pygame.font.Font( None, SMALL_NUMBER_FONT_SIZE )
        
        #   Do it!
        self.drawKenKen( k )
        
    
    
    def __del__( self ):
        """
        Deallocate anything that needs to be, and maybe save to file (later)
        """
        pyagme.quit()
    
    
    #   Setters
    def updateScreen( self ):
        pygame.display.flip()
    
    
    def drawKenKen( self, k ):
        """
        Given a kenken object k, draw it!
        """
        
        self.screen.fill( WHITE )
        
        self.drawBackground( k )
        self.drawCages( k )
        self.drawDisplayNumbers( k )
        self.drawPossibleNumbers( k )
        
        self.updateScreen()

    
    #   Background  ----------------------------------------------------
    def drawBackground( self, k ):
        """
        Draw the basic background (thick border, thin edges to be drawn over
        by cage borders)
        """
        
        #   Draw boundaries
        pygame.draw.line( self.screen, BLACK, [ self.border, self.border ], [ self.sizeX - self.border, self.border ], THICK_WIDTH )
        pygame.draw.line( self.screen, BLACK, [ self.border, self.border ], [ self.border, self.sizeY - self.border ], THICK_WIDTH )
        pygame.draw.line( self.screen, BLACK, [ self.sizeX - self.border, self.border ], [ self.sizeX - self.border, self.sizeY - self.border ], THICK_WIDTH )
        pygame.draw.line( self.screen, BLACK, [ self.border, self.sizeY - self.border ], [ self.sizeX - self.border, self.sizeY - self.border ], THICK_WIDTH )
        
        #   Draw backbone
        for i in range(1, 9):
            #   vertical
            pygame.draw.line( self.screen, BLACK, [ self.border + i * self.deltaX, self.border ], [ self.border + i * self.deltaX, self.sizeY - self.border ], THIN_WIDTH )
            
            #   horizontal
            pygame.draw.line( self.screen, BLACK, [ self.border, self.border + i * self.deltaY ], [ self.sizeX - self.border, self.border + i * self.deltaX ], THIN_WIDTH )


    #   Cages  ---------------------------------------------------------
    def drawCages( self, k ):
        """
        Draw the non-border boundaries of cages and label them with the
        operation and value
        """
        for rule in k.ruleList:
            self.drawCage( rule )
            self.labelCage( rule )


    def drawCage( self, rule ):
        """
        durt
        """
        cage, operation, value = rule
        
        for node in cage:
            i,j = node
            
            for direction in [ UP, DOWN, LEFT, RIGHT ]:
                if self.shouldDrawEdge( node, cage, direction ):
                    self.drawEdge( node, direction )


    def shouldDrawEdge( self, node, cage, direction ):
        """
        is the node in the direction relative to node in the cage?
        """
        i, j = node
        neighborNode = ( -1, -1 )
        if direction == RIGHT:
            if i != self.N - 1:
                neighborNode = ( i + 1, j )
        elif direction == LEFT:
            if i != 0:
                neighborNode = ( i - 1, j )
        elif direction == DOWN:
            if j != 0:
                neighborNode = ( i, j - 1 )
        else:#direction == UP:
            if j != self.N - 1:
                neighborNode = ( i, j + 1 )
        
        return neighborNode not in cage


    def drawEdge( self, node, direction ):
        """
        durt
        """
        
        i, j = node
        
        #   Initialize in the bottom left corner, then add to those positions
        startNode = [ self.border + i * self.deltaX, self.sizeY - self.border - j * self.deltaY ]
        endNode   = [ self.border + i * self.deltaX, self.sizeY - self.border - j * self.deltaY ]
        
        #   What to add
        if direction == UP:
            startNode[ 0 ] += 0
            startNode[ 1 ] -= self.deltaY
            endNode[0]     += self.deltaX
            endNode[1]     -= self.deltaY
        elif direction == DOWN:
            startNode[ 0 ] += 0
            startNode[ 1 ] -= 0
            endNode[0]     += self.deltaX
            endNode[1]     -= 0
        elif direction == LEFT:
            startNode[ 0 ] += 0
            startNode[ 1 ] -= 0
            endNode[0]     += 0
            endNode[1]     -= self.deltaY
        else:#direction == RIGHT:
            startNode[ 0 ] += self.deltaX
            startNode[ 1 ] -= 0
            endNode[0]     += self.deltaX
            endNode[1]     -= self.deltaY
        
        pygame.draw.line( self.screen, BLACK, startNode, endNode, THICK_WIDTH )


    def labelCage( self, rule ):
        """
        draw the "4x" sorts of labels in the cages
        """
        cage, operation, value = rule
        
        #   Find the upperleftmost square
        maxJ, minI = 0, self.N
        for node in cage:
            i, j = node
            if j >= maxJ:
                if i <= minI:
                    maxJ, minI = j, i
        
        i, j = minI, maxJ
        
        #   Draw the label in the upperleft corner of this square
        label = str( value )
        if operation == EQUALS:
            label += '='
        elif operation == PLUS:
            label += '+'
        elif operation == TIMES:
            label += 'x'
        elif operation == MINUS:
            label += '-'
        else:#operation == DIVIDE:
            label += '/'
        
        labelText = self.labelFont.render( label, True, BLACK )
        labelLoc = [ self.border + i * self.deltaX + 3, self.sizeY - self.border - (j + 1) * self.deltaY + 6 ]
        self.screen.blit( labelText, labelLoc )


    #   Display numbers  -----------------------------------------------
    def drawDisplayNumbers( self, k ):
        """
        Given the numbers which are supposed to be displayed as listed in
        k.displayedNumbers, draw them, yo!
        """
        for (node, value) in k.displayedNumbers.iteritems():
            self.drawSingleDisplayNumber( node, value )


    def drawSingleDisplayNumber( self, node, value ):
        """
        Durt
        """
        displayLoc = self.displayNumberLoc( node )
        
        numberText = self.bigNumberFont.render( str( value ), True, BLUE )
        self.screen.blit( numberText, displayLoc )


    def displayNumberLoc( self, node ):
        """
        Find the location to print the display number
        """
        i, j = node
        return [ self.border + i * self.deltaX + 30, self.sizeY  - (j + 1) * self.deltaY - 10 ]


    #   Possible numbers  ----------------------------------------------
    def drawPossibleNumbers( self, k ):
        """
        Draw all possibilities (lists of length greater than 1) in
        k.possDic
        """
        
        for (node, possList) in k.possDic.iteritems():
            if len( possList ) > 1:
                self.drawSinglePossibleNumber( node, possList )
    
    
    def drawSinglePossibleNumber( self, node, possList ):
        """
        durt
        """
        for val in possList:
            possLoc = self.possibleNumberLoc( node, val )
            
            possText = self.smallNumberFont.render( str( val ), True, RED )
            self.screen.blit( possText, possLoc )

    
    def possibleNumberLoc( self, node, val ):
        """
        Find the location for a possible number (array arrangement NxN)
        """
        i, j = node
        cornerX, cornerY = self.border + i * self.deltaX, self.sizeY - self.border - j * self.deltaY
        rootN = int( scipy.ceil( scipy.sqrt( self.N ) ) )
        offsetX = 5 + 15 * ( ( val - 1 ) % rootN )
        offsetY = 10 + 15 * ( rootN - int( val - 1 ) / rootN )
        
        return [ cornerX + offsetX, cornerY - offsetY ]
