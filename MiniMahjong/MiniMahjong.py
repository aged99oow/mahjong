#
# MiniMahjong.py 2022/9/14
#
import random
import pyxel
import mmfont

RELEASE_CANDIDATE = True
OPENWALL   = False
OPENHAND   = True
P1, P2, P3 = 1, 2, 3
NEXTTURN   = {P1:P2, P2:P3, P3:P1}
TRANS      = 99
ALLTILES   = [0,2,4,6,8,10,12,14,16,18,19,
              0,2,4,6,8,10,12,14,16,18,19,
              0,2,4,6,8,10,12,14,16,18,19,
              1,3,5,7,9,11,13,15,17,18,19]
MAX_ROUND  = 12
MAX_CHARA  = 12

HAND_X,     HAND_Y     = {P1: 46, P2: 46, P3: 46}, {P1:138, P2: 24, P3: 70}  # 手牌
DISCARD_X,  DISCARD_Y  = {P1:  2, P2:  2, P3:  2}, {P1:114, P2:  2, P3: 48}  # 捨て牌
SCORE_X,    SCORE_Y    = {P1:  2, P2:  2, P3:  2}, {P1:140, P2: 26, P3: 72}
CHARA_X,    CHARA_Y    = {P1: 23, P2: 23, P3: 23}, {P1:138, P2: 24, P3: 70}
WALL_X,     WALL_Y     = 159,   2  # 山
ROUND_X,    ROUND_Y    = 163, 146
DORA_X,     DORA_Y     = 190, 125
MSG_X,      MSG_Y      =  18,  92
BESTSCR_X,  BESTSCR_Y  = 218, 114
SELFBTN_X,  SELFBTN_Y  = 131, 145
DSCRDBTN_X, DSCRDBTN_Y = 117, 145
TILEBTN_X,  TILEBTN_Y  = 217, 141
SCRBTN_X,   SCRBTN_Y   = 217, 151
ST_TITLE1          = 110
ST_TITLE2          = 120
ST_DEAL            = 210
ST_CLK_START       = 310
ST_DRAW            = 410
ST_CLK_WINSELFDRAW = 420
ST_P2P3WINSELFDRAW = 430
ST_P2P3DISCARD     = 440
ST_P1WINDISCARD    = 450
ST_CLK_WINDISCARD  = 460
ST_P2P3WINDISCARD  = 470
ST_SORT            = 480
ST_CLK_SCOREUP     = 490
ST_CLK_END         = 510
CHARA_NAME = ('ピノキオ', 'ピーターパン', '人魚', '桃太郎', '金太郎', '裸の王様', 
              'ホームズ', '赤ちゃん', '孫悟空', '三蔵法師', 'エイリアン', '忍者')

class App:
    def reset(self):
        self.msg1 = self.msg2 = ''
        self.msgscrl = 0
        self.remain = [3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,4,4]
        self.hand = {P1:[], P2:[], P3:[]}
        self.discard = {P1:[], P2:[], P3:[]}
        self.extra = -1
        self.wallpos = 44
    
    def __init__(self):
        pyxel.init(244, 162, title='MiniMahjong')
        pyxel.load('assets/MiniMahjong.pyxres')
        pyxel.mouse(True)
        self.waitcount = 0
        self.wall = ALLTILES[:]
        self.round = -1
        self.charano = {P1:-1, P2:-1, P3:-1}
        self.dealer = self.turn = -1
        self.win = self.feed = -1
        self.score = {P1:-1, P2:-1, P3:-1}
        self.bestscore = 40
        self.alltilesbtn   = self.alltiles   = True
        self.scoretablebtn = self.scoretable = True
        self.recordscore = True
        self.openwallbtn = self.openwall = False
        self.openhandbtn = self.openhand = False
        self.winbutton = False
        self.reset()
        self.status = ST_TITLE1
        pyxel.run(self.update, self.draw)
    
    def in_message(self, newmsg, keep=False):
        if keep or self.msg1 == '':
            self.msg1 = newmsg
        elif newmsg:
            self.msgscrl = 7
            self.msg2 = self.msg1
            self.msg1 = newmsg
    
    def selecttile(self, hand):
        if hand.count(18) in (1, 2, 4) and self.remain[18] < 3:  # 発
            if not RELEASE_CANDIDATE and self.openhand:
                self.in_message(f'P{self.turn}:Green')
            return hand.index(18)
        if hand.count(19) in (1, 2, 4) and self.remain[19] < 3:  # 中
            if not RELEASE_CANDIDATE and self.openhand:
                self.in_message(f'P{self.turn}:Red')
            return hand.index(19)
        
        evalhand = [0] * 6
        for i in range(6):
            for j, r in enumerate(self.remain):
                if r:
                    temphand = hand[:]
                    temphand[i] = j
                    s, _ = self.calcscore(temphand)
                    #evalhand[i] += s * r
                    evalhand[i] += (s + r) if s else 0
        if max(evalhand) > 0:
            if not RELEASE_CANDIDATE and self.openhand:
                self.in_message(f'P{self.turn}:{evalhand}:Ready')
            return random.choice([i for i, v in enumerate(evalhand) if v == max(evalhand)])
        
        sorthand = sorted(hand)
        formhand = [i-1 if i in range(1,18,2) else i for i in sorthand]
        formremain = self.remain[:]
        for i in range(1, 18, 2):
            formremain[i-1] += self.remain[i]
        for i in formhand:
            formremain[i] -= 1
        
        pong = [0]*6  # 刻子/槓子
        for i in range(4):
            if formhand[i] == formhand[i+2] and (i == 3 or (i < 3 and formhand[i] != formhand[i+3])):
                for j in range(6):
                    if j < i or j > i+2:
                        pong[j] = 1
        #if max(pong):
        #    print(f'[P{self.turn}]pong:{pong}')
        
        chow = [0]*6  # 順子
        for i in range(4):
            for j in range(i+1, 5):
                for k in range(j+1, 6):
                    if formhand[k] < 18 and formhand[i]+4 == formhand[j]+2 == formhand[k]:
                        for l in range(6):
                            if l != i and l != j and l != k:
                                chow[l] = 1
        #if max(chow):
        #    print(f'[P{self.turn}]chow:{chow}')
        
        pair = [0]*6  # 対子
        for i in range(5):
            if formhand[i] == formhand[i+1] and \
                    (i == 0 or (i > 0 and formhand[i] != formhand[i-1])) and \
                    (i == 4 or (i < 4 and formhand[i] != formhand[i+2])):
                for j in range(6):
                    if j != i and j != i+1:
                        pair[j] += formremain[formhand[i]]
        #if max(pair):
        #    print(f'[P{self.turn}]pair:{pair}')
        
        serialpair = [0]*6  # 塔子
        for i in range(5):
            for j in range(i+1, 6):
                if formhand[j] < 18 and formhand[i]+2 == formhand[j]:  # 両面塔子/辺張塔子
                    for k in range(6):
                        if k != i and k != j:
                            if formhand[i] > 0:
                                serialpair[k] += formremain[formhand[i]-2]
                            if formhand[j] < 16:
                                serialpair[k] += formremain[formhand[j]+2]
                if formhand[j] < 18 and formhand[i]+4 == formhand[j]:  # 嵌張塔子
                    for k in range(6):
                        if k != i and k != j:
                            serialpair[k] += formremain[formhand[i]+2]
        #if max(serialpair):
        #    print(f'[P{self.turn}]serialpair:{serialpair}')
        
        formextra = self.extra-1 if self.extra in range(1,18,2) else self.extra
        redextra = [0]*6  # 赤牌/ドラ
        for i in range(6):
            if sorthand[i] in range(0, 19, 2):  # 赤牌
                redextra[i] += 1
            if formhand[i] != formextra:  # ドラ
                redextra[i] += 1
        #if max(redextra):
        #    print(f'[P{self.turn}]redextra:{redextra}')
        
        evalhand = [0]*6
        for i in range(6):
            evalhand[i] = pong[i]*12+chow[i]*8+pair[i]*4+serialpair[i]+redextra[i]*2
        if not RELEASE_CANDIDATE and self.openhand:
            self.in_message(f'P{self.turn}:{evalhand}')
        idx = random.choice([i for i, v in enumerate(evalhand) if v == max(evalhand)])
        return hand.index(sorthand[idx])
    
    def calcscore(self, hand):
        sorthand = sorted(hand)
        formhand = [i-1 if i in range(1,18,2) else i for i in sorthand]
        score = 0
        handname = ''
        hand1 = formhand[0]
        for i in range(1, 5):
            for j in range(i+1, 6):
                hand2 = formhand[i]
                hand3 = formhand[j]
                if hand1 == hand2 == hand3:
                    hand4 = [0] * 3
                    for p, q in enumerate(set(range(1, 6))-{i, j}):
                        hand4[p] = formhand[q]
                    if hand4[0] == hand4[1] == hand4[2]:
                        handname = '同じ2 同じ2'
                        score += 4
                        break
                    elif hand4[2] < 18 and hand4[0]+4 == hand4[1]+2 == hand4[2]:
                        handname = '同じ2 連番1'
                        score += 3
                        break
                if hand3 < 18 and hand1+4 == hand2+2 == hand3:
                    hand4 = [0] * 3
                    for p, q in enumerate(set(range(1, 6))-{i, j}):
                        hand4[p] = formhand[q]
                    if hand4[0] == hand4[1] == hand4[2]:
                        handname = '連番1 同じ2'
                        score += 3
                        break
                    elif hand4[2] < 18 and hand4[0]+4 == hand4[1]+2 == hand4[2]:
                        handname = '連番1 連番1'
                        score += 2
                        break
            else:
                continue
            break
        if score:
            green = red = thisextra = simple = 0
            for h in hand:
                if h in (2, 4, 6, 10, 14, 18):
                    green += 1
                if h in range(1, 20, 2):
                    red += 1
                if h in range(2, 16):
                    simple += 1
            formextra = self.extra-1 if self.extra in range(1,18,2) else self.extra
            for h in formhand:
                if h == formextra:
                    thisextra += 1
            if green == 6:
                handname += ' オールグリーン10'
                score += 10
            elif simple == 0:
                handname += ' チンヤオ15'
                score += 15
            elif red == 6:
                handname += ' スーパーレッド20'
                score += 20
            else:
                if red:
                    handname += f' 赤牌{red}'
                    score += red
                if thisextra:
                    handname += f' ドラ{thisextra}'
                    score += thisextra
                if simple == 6:
                    handname += ' タンヤオ1'
                    score += 1
                elif simple in (2, 4):
                    handname += ' チャンタ2'
                    score += 2
        return score, handname
    
    def furiten(self, recentdiscard, owndiscard):
        formrecentdiscard = recentdiscard-1 if recentdiscard in range(1,18,2) else recentdiscard
        formowndiscard    = [i-1 if i in range(1,18,2) else i for i in owndiscard]
        #print('formrecentdiscard:', formrecentdiscard)
        #print('formowndiscard:', formowndiscard)
        return formrecentdiscard in formowndiscard
    
    def leftclick(self, opentile = False):
        if self.alltilesbtn:
            self.alltiles = True
        elif self.scoretablebtn:
            self.scoretable = True
        elif self.openwallbtn:
            self.openwall = not self.openwall
            if opentile and self.recordscore:
                self.recordscore = False
                self.in_message('オープンしたので *eベストスコア*7は記録されません')
        elif self.openhandbtn:
            self.openhand = not self.openhand
            if opentile and self.recordscore:
                self.recordscore = False
                self.in_message('オープンしたので *eベストスコア*7は記録されません')
        else:
            return False
        return True
    
    def update(self):
        if self.alltiles:
            if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
                self.alltiles = False
            return
        if self.scoretable:
            if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
                self.scoretable = False
            return
        if self.msgscrl:
            self.msgscrl -= 1
        if self.waitcount:
            self.waitcount -= 1
            return
        
        self.alltilesbtn = TILEBTN_X <= pyxel.mouse_x < TILEBTN_X+26 and TILEBTN_Y <= pyxel.mouse_y < TILEBTN_Y+10
        self.scoretablebtn = SCRBTN_X <= pyxel.mouse_x < SCRBTN_X+26 and SCRBTN_Y <= pyxel.mouse_y < SCRBTN_Y+10
        self.openwallbtn = WALL_X <= pyxel.mouse_x < WALL_X+13 and WALL_Y <= pyxel.mouse_y < WALL_Y+16
        self.openhandbtn = (HAND_X[P2] <= pyxel.mouse_x < HAND_X[P2]+13 and 
                HAND_Y[P2] <= pyxel.mouse_y < HAND_Y[P2]+20) or (HAND_X[P3] <= pyxel.mouse_x < HAND_X[P3]+13 and 
                HAND_Y[P3] <= pyxel.mouse_y < HAND_Y[P3]+20)
        
        if self.status == ST_TITLE1:
            self.alltiles = False
            self.status = ST_TITLE2
            
        elif self.status == ST_TITLE2:
            self.scoretable = False
            self.win = self.feed = -1
            self.round = 0
            n = random.sample(range(MAX_CHARA), 3)
            self.charano[P1], self.charano[P2], self.charano[P3] = n[0], n[1], n[2]
            self.dealer = random.choice([P1, P2, P3])
            self.turn = self.dealer
            self.score = {P1:40, P2:40, P3:40}
            self.status = ST_DEAL
        
        elif self.status == ST_DEAL:
            self.reset()
            if self.recordscore:
                self.openwall = False
                self.openhand = False
            random.shuffle(self.wall)
            self.round += 1
            self.dealer = NEXTTURN[self.dealer]
            self.turn = self.dealer
            self.wallpos -= 1
            self.extra = self.wall[self.wallpos]
            self.remain[self.extra] -= 1
            #print(f'remain:{self.remain}')
            for p in (P1, P2, P3):  # 配る
                self.wallpos -= 5
                self.hand[p] = self.wall[self.wallpos:self.wallpos+5]
                self.hand[p].sort()
            if self.round == 1:
                self.in_message(f'全{MAX_ROUND}局 さあ 始めましょう')
            elif self.round == MAX_ROUND:
                self.in_message(f'最終局です 始めましょう')
            else:
                self.in_message(f'第{self.round}局 始めましょう')
            self.status = ST_CLK_START
        
        elif self.status == ST_CLK_START:
            if  pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
                if self.leftclick(True):
                    pass
                else:
                    self.win = self.feed = -1
                    self.status = ST_DRAW
        
        elif self.status == ST_DRAW:
            self.discardpos = -1
            if self.wallpos > 0:
                self.wallpos -= 1
                self.hand[self.turn].append(self.wall[self.wallpos])  # ツモる
                self.thisscore, self.thishandname = self.calcscore(self.hand[self.turn])
                if self.turn == P1:
                    self.status = ST_CLK_WINSELFDRAW
                else:
                    self.waitcount = 5
                    self.status = ST_P2P3WINSELFDRAW
            else:
                self.in_message('流局')
                self.status = ST_CLK_SCOREUP
        
        elif self.status == ST_CLK_WINSELFDRAW:  # P1あがり／捨て牌
            self.winbutton = self.thisscore >= 5 and \
                    SELFBTN_X<=pyxel.mouse_x<SELFBTN_X+18 and SELFBTN_Y-4<=pyxel.mouse_y<SELFBTN_Y+14
            self.discardpos = (pyxel.mouse_x-HAND_X[P1])//14 if HAND_X[P1] <= pyxel.mouse_x < HAND_X[P1]+14*6 and \
                    HAND_Y[P1] <= pyxel.mouse_y < HAND_Y[P1]+20 else -1
            if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
                if self.leftclick(True):
                    pass
                elif self.winbutton:  # あがり
                    if self.turn == self.dealer:
                        self.thishandname += ' 親2'
                        self.thisscore += 2
                    self.win  = self.turn
                    self.feed = self.turn
                    self.thishandname = f'*eツモ {self.thisscore}点*7 … ' + self.thishandname
                    self.in_message(self.thishandname)
                    self.status = ST_CLK_SCOREUP
                elif self.discardpos >= 0:  # P1捨て牌
                    self.discard[self.turn].append(self.hand[self.turn][self.discardpos])
                    self.remain[self.hand[self.turn][self.discardpos]] -= 1
                    #print(f'remain:{self.remain}')
                    self.hand[self.turn][self.discardpos] = TRANS
                    self.status = ST_P2P3WINDISCARD
        
        elif self.status == ST_P2P3WINSELFDRAW:  # P2,P3あがり
            if self.thisscore >= 5:
                if self.turn == self.dealer:
                    self.thishandname += ' 親2'
                    self.thisscore += 2
                self.win  = self.turn
                self.feed = self.turn
                self.thishandname = f'*eツモ {self.thisscore}点*7 … ' + self.thishandname
                self.in_message(self.thishandname)
                self.status = ST_CLK_SCOREUP
            else:
                self.waitcount = 5
                self.status = ST_P2P3DISCARD
        
        elif self.status == ST_P2P3DISCARD:  # P2,P3捨て牌
            self.discardpos = self.selecttile(self.hand[self.turn])
            self.discard[self.turn].append(self.hand[self.turn][self.discardpos])
            self.remain[self.hand[self.turn][self.discardpos]] -= 1
            #print(f'remain:{self.remain}')
            self.hand[self.turn][self.discardpos] = TRANS
            self.status = ST_P1WINDISCARD
        
        elif self.status == ST_P1WINDISCARD:  # P2,P3捨て牌でP1あがり確認
            thishand = self.hand[P1][:]
            thishand.append(self.discard[self.turn][-1])
            self.thisscore, self.thishandname = self.calcscore(thishand)
            if self.thisscore >= 5 and not self.furiten(self.discard[self.turn][-1], self.discard[P1]):
                if P1 == self.dealer:
                    self.thishandname += ' 親2'
                    self.thisscore += 2
                self.status = ST_CLK_WINDISCARD
            else:
                self.status = ST_P2P3WINDISCARD
        
        elif self.status == ST_CLK_WINDISCARD:  # P2,P3捨て牌でP1あがり
            self.winbutton = DSCRDBTN_X<=pyxel.mouse_x<DSCRDBTN_X+18 and \
                    DSCRDBTN_Y-4<=pyxel.mouse_y<DSCRDBTN_Y+14
            if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
                if self.leftclick(True):
                    pass
                elif self.winbutton:
                    self.win  = P1
                    self.feed = self.turn
                    self.hand[P1].append(self.discard[self.turn][-1])
                    self.thishandname = f'*eロン {self.thisscore}点*7 … ' + self.thishandname
                    self.in_message(self.thishandname)
                    self.status = ST_CLK_SCOREUP
                else:
                    self.status = ST_P2P3WINDISCARD
        
        elif self.status == ST_P2P3WINDISCARD:  # P1,P2,P3捨て牌でP2,P3あがり
            for p in {P2, P3}-{self.turn}:
                thishand = self.hand[p][:]
                thishand.append(self.discard[self.turn][-1])
                self.thisscore, self.thishandname = self.calcscore(thishand)
                if self.thisscore >= 5 and not self.furiten(self.discard[self.turn][-1], self.discard[p]):
                    if p == self.dealer:
                        self.thishandname += ' 親2'
                        self.thisscore += 2
                    self.win  = p
                    self.feed = self.turn
                    self.hand[p].append(self.discard[self.turn][-1])
                    self.thishandname = f'*eロン {self.thisscore}点*7 … ' + self.thishandname
                    self.in_message(self.thishandname)
                    self.status = ST_CLK_SCOREUP
                    break
            else:
                self.waitcount = 10
                self.status = ST_SORT
        
        elif self.status == ST_SORT:  # ツモ牌ソート
            del self.hand[self.turn][self.discardpos]
            self.hand[self.turn].sort()
            self.turn = NEXTTURN[self.turn]
            self.status = ST_DRAW
        
        elif self.status == ST_CLK_SCOREUP:
            if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
                if self.leftclick():
                    pass
                else:
                    if self.thisscore:
                        if self.win == self.feed:
                            self.thisscore += self.thisscore % 2
                            self.score[self.win] += self.thisscore
                            for p in {P1, P2, P3}-{self.win}:
                                self.score[p] -= self.thisscore // 2
                        else:
                            self.score[self.win]  += self.thisscore
                            self.score[self.feed] -= self.thisscore
                    if self.round < MAX_ROUND:
                        self.waitcount = 10
                        self.status = ST_DEAL
                    else:
                        if self.score[P1] > self.bestscore and self.recordscore:
                            self.in_message(f'ベストスコア *e{self.bestscore}点 *7を更新しました')
                            self.bestscore = self.score[P1]
                        yourank = sorted(self.score.values(), reverse=True).index(self.score[P1])+1
                        self.in_message(f'全{MAX_ROUND}局終了 あなた … *e{self.score[P1]}点 *a{yourank}位')
                        self.waitcount = 10
                        self.status = ST_CLK_END
        
        elif self.status == ST_CLK_END:
            if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT):
                if self.leftclick():
                    pass
                else:
                    self.recordscore = True
                    self.openwall = False
                    self.openhand = False
                    self.status = ST_TITLE2
    
    def draw_tile(self, x, y, piece = -1, front = True, thick = True):
        if piece < 0:  # 裏
            if thick:
                pyxel.blt(x, y+(0 if front==True else 16), 0, 0, 16 if front==True else 24, 13, 4, 1)
            pyxel.blt(x, y+(4 if front==True else 0), 0, 0, 0, 13, 16, 1)
        elif 0 <= piece < 18:
            if thick:
                pyxel.blt(x, y+(0 if front==True else 16), 0, 0, 20 if front==True else 28, 13, 4, 1)
            pyxel.blt(x, y+(4 if front==True else 0), 0, (piece//2)*16+16, (piece%2)*16, 13, 16, 1)
        elif 18 <= piece < 20:
            if thick:
                pyxel.blt(x, y+(0 if front==True else 16), 0, 0, 20 if front==True else 28, 13, 4, 1)
            pyxel.blt(x, y+(4 if front==True else 0), 0, (piece-7)*16, 0, 13, 16, 1)
    
    def draw_wall(self):
        for i in range(self.wallpos):
            self.draw_tile(WALL_X+(i%6)*14, WALL_Y+(i//6)*17, self.wall[i] if self.openwall else -1, False, \
                    False if i < self.wallpos-6 else True)
            if self.openwall and i%3 == self.dealer-1:
                pyxel.blt(WALL_X+(i%6)*14, WALL_Y+(i//6)*17, 0, 0, 32, 13, 16, 1)
    
    def draw_message(self):
        pyxel.rectb(MSG_X  , MSG_Y  , 204, 19, 7)
        pyxel.rect( MSG_X+1, MSG_Y+1, 202, 17, 1)
        if self.msgscrl:
            mmfont.text(MSG_X+2, MSG_Y+2+self.msgscrl, self.msg2, 7)  # col:1
        else:
            mmfont.text(MSG_X+2, MSG_Y+2, self.msg2, 7)
            mmfont.text(MSG_X+2, MSG_Y+10, self.msg1, 7)  # col:1
    
    def draw_button(self, x, y, txt, btn):
        for dy in range(3):
            for dx in range(3):
                if dy != 1 or dx != 1:
                    mmfont.text(x+dx, y+dy, txt, 0)
        mmfont.text(x+1, y+1, txt, 7 if btn else 1)
    
    def draw_alltiles(self):
        mmfont.text(110, 12, '牌一覧', 6)
        mmfont.text(35, 27, '1   2   3   4   5   6   7   8   9  ハツ チュン', 7)
        for i in range(len(ALLTILES)):
            self.draw_tile(30+(i%11)*16+(((i%11)-8)*4 if (i%11)>8 else 0), 40+(i//11)*24, ALLTILES[i], False)
        pyxel.rectb(26, 109, 149, 26, 14)
        pyxel.rectb(194, 37, 21, 98, 14)
        mmfont.text(93, 137, '赤牌                      赤牌', 14)
    
    def draw_scoretable(self):
        mmfont.text(102, 1, '必須の3個3個', 6)
        pyxel.rectb(1, 9, 242, 24, 7)
        mmfont.text(5, 17, '3個連番....*e1点*7 例              3個同じ....*e2点*7 例', 7)
        self.draw_tile( 74, 11,  0, False)
        self.draw_tile( 88, 11,  2, False)
        self.draw_tile(102, 11,  4, False)
        self.draw_tile(198, 11, 14, False)
        self.draw_tile(212, 11, 14, False)
        self.draw_tile(226, 11, 14, False)
        mmfont.text(47, 34, '+ボーナス    *7←両立しない→     *6+役満', 6)
        pyxel.rectb(  1, 42, 125, 111,  7)
        pyxel.rectb(128, 42, 115, 111,  7)
        mmfont.text(3, 50, '赤牌..*e各1点*7       ‥', 7)
        self.draw_tile( 47, 44,  1, False)
        self.draw_tile( 61, 44,  3, False)
        self.draw_tile( 83, 44, 15, False)
        self.draw_tile( 97, 44, 17, False)
        self.draw_tile(111, 44, 19, False)
        pyxel.rectb(49, 65, 20, 20, 7)
        #pyxel.rect (50, 66, 18, 18, 0)
        mmfont.text(3, 71, 'ドラ..*e各1点*7 ドラ と同じもの', 7)
        mmfont.text(3, 86, 'タンヤオ...*e1点', 7)
        self.draw_tile(27, 94,  2, False)
        self.draw_tile(49, 94, 14, False)
        self.draw_tile(63, 94,  3, False)
        self.draw_tile(85, 94, 15, False)
        mmfont.text(41, 100, '‥       ‥    で作る', 7)
        mmfont.text( 3, 115, 'チャンタ...*e2点', 7)
        self.draw_tile(27, 123,  0, False)
        self.draw_tile(41, 123, 16, False)
        self.draw_tile(55, 123,  1, False)
        self.draw_tile(69, 123, 17, False)
        self.draw_tile(83, 123, 18, False)
        self.draw_tile(97, 123, 19, False)
        mmfont.text(112, 129, 'が', 7)
        mmfont.text( 56, 144, '3個2組両方にある', 7)
        mmfont.text(130,  45, 'オールグリーン.........*e10点', 7)
        self.draw_tile(132, 54,  2, False)
        self.draw_tile(146, 54,  4, False)
        self.draw_tile(160, 54,  6, False)
        self.draw_tile(174, 54, 10, False)
        self.draw_tile(188, 54, 14, False)
        self.draw_tile(202, 54, 18, False)
        mmfont.text(216, 60, 'で作る', 7)
        mmfont.text(130, 80, 'チンヤオ...............*e15点', 7)
        self.draw_tile(132, 89,  0, False)
        self.draw_tile(146, 89, 16, False)
        self.draw_tile(160, 89,  1, False)
        self.draw_tile(174, 89, 17, False)
        self.draw_tile(188, 89, 18, False)
        self.draw_tile(202, 89, 19, False)
        mmfont.text(216,  95, 'で作る', 7)
        mmfont.text(130, 115, 'スーパーレッド.........*e20点', 7)
        self.draw_tile(132, 124,  1, False)
        self.draw_tile(146, 124,  3, False)
        self.draw_tile(168, 124, 15, False)
        self.draw_tile(182, 124, 17, False)
        self.draw_tile(196, 124, 19, False)
        mmfont.text(160, 130, '‥           で作る', 7)
        mmfont.text(2, 154, 'あがるには*e合計5点以上*7が必要 あがったあとで*e親*7なら*eボーナス+2点', 7)
    
    def draw(self):
        if self.alltiles:
            pyxel.cls(1)
            self.draw_alltiles()
            return
        elif self.scoretable:
            pyxel.cls(1)
            self.draw_scoretable()
            return
        
        pyxel.cls(5)
        self.draw_button(TILEBTN_X, TILEBTN_Y, '牌一覧', self.alltilesbtn)
        self.draw_button(SCRBTN_X,  SCRBTN_Y,  '得点表', self.scoretablebtn)
        
        if self.round > 0:
            mmfont.text(ROUND_X, ROUND_Y, f'第{self.round}局', 7)
        
        mmfont.text(DORA_X+3, DORA_Y, 'ドラ', 7)
        pyxel.rectb(DORA_X  , DORA_Y+9,  23, 26, 7)
        pyxel.rect (DORA_X+1, DORA_Y+10, 21, 24, 1)
        if self.extra >= 0:
            self.draw_tile(DORA_X+5, DORA_Y+12, self.extra, False)
        
        if self.dealer in (P1, P2, P3):
            mmfont.text(SCORE_X[self.dealer]+8, SCORE_Y[self.dealer]+9, '親', 7)
        self.draw_message()
        self.draw_wall()
        for p in (P1, P2, P3):
            col = 7
            if self.status in (ST_DEAL, ST_CLK_START, ST_CLK_END):
                if p == self.win:
                    col = 10
                elif self.win in (P1, P2, P3) and (self.win == self.feed or p == self.feed):
                    col = 13
            mmfont.text(SCORE_X[p], SCORE_Y[p], f'{self.score[p]:3}点', col)
            pyxel.rectb(CHARA_X[p], CHARA_Y[p], 20, 20, 7)
            if self.status == ST_CLK_SCOREUP and p == self.win:
                pyxel.rect (CHARA_X[p]+1, CHARA_Y[p]+1, 18, 18, 12)
            elif self.status == ST_CLK_END and self.score[p] == max(self.score.values()):
                pyxel.rect (CHARA_X[p]+1, CHARA_Y[p]+1, 18, 18, pyxel.frame_count//3%4+9)
            else:
                pyxel.rect (CHARA_X[p]+1, CHARA_Y[p]+1, 18, 18, 1)
            pyxel.blt(CHARA_X[p]+2, CHARA_Y[p]+2, 1, self.charano[p]*16, 0, 16, 16, 1)
            for i, tile in enumerate(self.discard[p]):  # 山
                if self.status in (ST_P1WINDISCARD, ST_CLK_WINDISCARD, ST_P2P3WINDISCARD, ST_SORT) and \
                        p == self.turn and i == len(self.discard[p])-1:
                    self.draw_tile(DISCARD_X[p]+14*i+4, DISCARD_Y[p], tile, False)
                elif self.win != self.feed and p == self.feed and i == len(self.discard[p])-1:
                    self.draw_tile(DISCARD_X[p]+14*i+4, DISCARD_Y[p], tile, False)
                else:
                    self.draw_tile(DISCARD_X[p]+14*i, DISCARD_Y[p], tile, False)
            for i, tile in enumerate(self.hand[p]):  # 手牌
                if not (self.openhand or p == P1 or p == self.win or tile == TRANS) or \
                        (self.status == ST_CLK_START and (p == P1 or (not self.openhand and p in (P2, P3)))):
                    tile = -1
                if self.status == ST_CLK_WINSELFDRAW and p == P1 and self.discardpos == i:
                    self.draw_tile(HAND_X[p]+14*i, HAND_Y[p]-4, tile)
                elif self.status != ST_CLK_START and p == self.win and self.win != self.feed and i == 5:
                    self.draw_tile(HAND_X[p]+14*i+4, HAND_Y[p], tile, False)
                elif self.status == ST_CLK_START or p == self.win:
                    self.draw_tile(HAND_X[p]+14*i, HAND_Y[p], tile, False)
                else:
                    self.draw_tile(HAND_X[p]+14*i, HAND_Y[p], tile)
        mmfont.text(BESTSCR_X  , BESTSCR_Y   , 'ベスト\nスコア', 7 if self.recordscore else 13)
        mmfont.text(BESTSCR_X+4, BESTSCR_Y+16, f'{self.bestscore}点', \
                14 if self.status == ST_CLK_END and self.bestscore == self.score[P1] else 7 if self.recordscore else 13)
        if self.status == ST_CLK_WINSELFDRAW and self.thisscore >= 5:
            self.draw_button(SELFBTN_X, SELFBTN_Y, 'ツモ', self.winbutton)
        if self.status == ST_CLK_WINDISCARD:
            self.draw_button(DSCRDBTN_X, DSCRDBTN_Y, 'ロン', self.winbutton)

App()

