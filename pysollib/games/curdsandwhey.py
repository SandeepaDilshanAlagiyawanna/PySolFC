##---------------------------------------------------------------------------##
##
## PySol -- a Python Solitaire game
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING.
## If not, write to the Free Software Foundation, Inc.,
## 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
##
##---------------------------------------------------------------------------##

__all__ = []

# imports
import sys

# PySol imports
from pysollib.gamedb import registerGame, GameInfo, GI
from pysollib.util import *
from pysollib.mfxutil import kwdefault
from pysollib.stack import *
from pysollib.game import Game
from pysollib.layout import Layout
from pysollib.hint import AbstractHint, DefaultHint, CautiousDefaultHint

# /***********************************************************************
# // Curds and Whey
# // Miss Muffet
# // Nordic
# ************************************************************************/

class CurdsAndWhey_RowStack(BasicRowStack):

    def acceptsCards(self, from_stack, cards):
        if not BasicRowStack.acceptsCards(self, from_stack, cards):
            return False
        if not self.cards:
            return True
        c1, c2 = self.cards[-1], cards[0]
        if c1.suit == c2.suit:
            return c1.rank == c2.rank+1
        return c1.rank == c2.rank

    def canMoveCards(self, cards):
        return isSameSuitSequence(cards) or isRankSequence(cards, dir=0)

    def getHelp(self):
        return _('Row. Build down by suit or of the same rank.')


class CurdsAndWhey(Game):

    Hint_Class = CautiousDefaultHint
    RowStack_Class = StackWrapper(CurdsAndWhey_RowStack, base_rank=KING,
                                  max_move=UNLIMITED_MOVES, max_accept=UNLIMITED_ACCEPTS)

    #
    # game layout
    #

    def createGame(self, rows=13):
        # create layout
        l, s = Layout(self), self.s

        # set window
        w, h = l.XM+rows*l.XS, l.YM+l.YS+16*l.YOFFSET
        self.setSize(w, h)

        # create stacks
        x, y = l.XM, l.YM
        for i in range(rows):
            stack = self.RowStack_Class(x, y, self)
            s.rows.append(stack)
            x += l.XS

        s.talon = InitialDealTalonStack(w-l.XS, h-l.YS, self)

        # default
        l.defaultAll()

    #
    # game overrides
    #

    def startGame(self):
        for i in range(3):
            self.s.talon.dealRow(frames=0)
        self.startDealSample()
        self.s.talon.dealRow()

    def isGameWon(self):
        for s in self.s.rows:
            if s.cards:
                if len(s.cards) != 13 or not isSameSuitSequence(s.cards):
                    return False
        return True

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return card1.rank == card2.rank or (
            card1.suit == card2.suit and abs(card1.rank-card2.rank) == 1)


class MissMuffet(CurdsAndWhey):

    def createGame(self):
        CurdsAndWhey.createGame(self, rows=10)

    def startGame(self):
        for i in range(4):
            self.s.talon.dealRow(frames=0)
        self.s.talon.dealRow(rows=[self.s.rows[0], self.s.rows[-1]], frames=0)
        self.startDealSample()
        self.s.talon.dealRow()


class Nordic(MissMuffet):
    RowStack_Class = StackWrapper(CurdsAndWhey_RowStack, base_rank=ANY_RANK,
                                  max_move=UNLIMITED_MOVES, max_accept=UNLIMITED_ACCEPTS)


# /***********************************************************************
# // Dumfries
# // Galloway
# // Robin
# ************************************************************************/

class Dumfries_TalonStack(OpenTalonStack):
    rightclickHandler = OpenStack.rightclickHandler

class Dumfries_RowStack(BasicRowStack):

    def acceptsCards(self, from_stack, cards):
        if not BasicRowStack.acceptsCards(self, from_stack, cards):
            return False
        if not self.cards:
            return True
        c1, c2 = self.cards[-1], cards[0]
        if c1.color == c2.color:
            return False
        return c1.rank == c2.rank or c1.rank == c2.rank+1

    def canMoveCards(self, cards):
        return len(cards) == 1 or len(cards) == len(self.cards)

class Dumfries(Game):

    ##Hint_Class = KlondikeType_Hint

    def createGame(self, **layout):
        # create layout
        l, s = Layout(self), self.s
        kwdefault(layout, rows=8, waste=0, texts=1, playcards=20)
        apply(Layout.klondikeLayout, (l,), layout)
        self.setSize(l.size[0], l.size[1])
        # create stacks
        s.talon = Dumfries_TalonStack(l.s.talon.x, l.s.talon.y, self)
        for r in l.s.foundations:
            s.foundations.append(SS_FoundationStack(r.x, r.y, self,
                                                    suit=r.suit))
        for r in l.s.rows:
            s.rows.append(Dumfries_RowStack(r.x, r.y, self,
                                            max_move=UNLIMITED_MOVES,
                                            max_accept=UNLIMITED_ACCEPTS))
        # default
        l.defaultAll()
        self.sg.dropstacks.append(s.talon)

    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.fillStack()

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return card1.color != card2.color and abs(card1.rank-card2.rank) in (0, 1)


class Galloway(Dumfries):
    def createGame(self):
        Dumfries.createGame(self, rows=7)


class Robin(Dumfries):
    def createGame(self):
        Dumfries.createGame(self, rows=12)



# /***********************************************************************
# // Arachnida
# ************************************************************************/

class Arachnida_RowStack(BasicRowStack):

    def acceptsCards(self, from_stack, cards):
        if not BasicRowStack.acceptsCards(self, from_stack, cards):
            return False
        if not self.cards:
            return True
        c1, c2 = self.cards[-1], cards[0]
        if c1.rank == c2.rank+1:
            return True
        return c1.rank == c2.rank

    def canMoveCards(self, cards):
        return isSameSuitSequence(cards) or isRankSequence(cards, dir=0)


class Arachnida(CurdsAndWhey):

    def createGame(self):
        # create layout
        l, s = Layout(self), self.s

        # set window
        w, h = l.XM+11*l.XS, l.YM+l.YS+16*l.YOFFSET
        self.setSize(w, h)

        # create stacks
        x, y = l.XM, l.YM
        s.talon = DealRowTalonStack(x, y, self)
        l.createText(s.talon, "ss")
        x += l.XS
        for i in range(10):
            stack = Arachnida_RowStack(x, y, self, base_rank=ANY_RANK,
                                      max_move=UNLIMITED_MOVES,
                                      max_accept=UNLIMITED_ACCEPTS)
            s.rows.append(stack)
            x += l.XS

        # define stack-groups
        l.defaultStackGroups()

    def startGame(self):
        for i in range(4):
            self.s.talon.dealRow(flip=0, frames=0)
        self.s.talon.dealRow(rows=self.s.rows[:4], flip=0, frames=0)
        self.startDealSample()
        self.s.talon.dealRow()

    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return card1.rank == card2.rank or abs(card1.rank-card2.rank) == 1


# /***********************************************************************
# // German Patience
# // Bavarian Patience
# ************************************************************************/

class GermanPatience(Game):

    def createGame(self, rows=8):

        l, s = Layout(self), self.s

        w, h = l.XM+rows*l.XS, l.YM+2*l.YS+14*l.YOFFSET
        self.setSize(w, h)

        x, y = l.XM, l.YM
        for i in range(rows):
            s.rows.append(RK_RowStack(x, y, self, max_cards=13, mod=13, dir=1, max_move=1))
            x += l.XS
        x, y = l.XM, h-l.YS
        s.talon = WasteTalonStack(x, y, self, max_rounds=1)
        l.createText(s.talon, 'nn')
        x += l.XS
        s.waste = WasteStack(x, y, self)
        l.createText(s.waste, 'nn')

        l.defaultStackGroups()


    def startGame(self):
        self.startDealSample()
        self.s.talon.dealRow()
        self.s.talon.dealCards()


    def isGameWon(self):
        if self.s.waste.cards or self.s.talon.cards:
            return False
        for s in self.s.rows:
            if s.cards:
                if len(s.cards) != 13: # or not isRankSequence(s.cards):
                    return False
        return True


    def shallHighlightMatch(self, stack1, card1, stack2, card2):
        return ((card1.rank + 1) % 13 == card2.rank or
                (card2.rank + 1) % 13 == card1.rank)


class BavarianPatience(GermanPatience):
    def createGame(self, rows=10):
        GermanPatience.createGame(self, rows=10)


# register the game
registerGame(GameInfo(294, CurdsAndWhey, "Curds and Whey",
                      GI.GT_SPIDER | GI.GT_OPEN, 1, 0))
registerGame(GameInfo(311, Dumfries, "Dumfries",
                      GI.GT_1DECK_TYPE, 1, 0))
registerGame(GameInfo(312, Galloway, "Galloway",
                      GI.GT_1DECK_TYPE, 1, 0))
registerGame(GameInfo(313, Robin, "Robin",
                      GI.GT_2DECK_TYPE, 2, 0))
registerGame(GameInfo(348, Arachnida, "Arachnida",
                      GI.GT_SPIDER, 2, 0))
registerGame(GameInfo(349, MissMuffet, "Miss Muffet",
                      GI.GT_SPIDER | GI.GT_OPEN, 1, 0))
registerGame(GameInfo(352, Nordic, "Nordic",
                      GI.GT_SPIDER | GI.GT_OPEN, 1, 0))
registerGame(GameInfo(414, GermanPatience, "German Patience",
                      GI.GT_2DECK_TYPE, 2, 0))
registerGame(GameInfo(415, BavarianPatience, "Bavarian Patience",
                      GI.GT_2DECK_TYPE, 2, 0))

