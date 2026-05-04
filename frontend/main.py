import os
os.add_dll_directory("C:/msys64/mingw64/bin")

import pygame, sys, math, random

try:
    import city_engine
    BACKEND = True
except ImportError:
    BACKEND = False

pygame.init()

SW, SH = 1280, 720
TW, TH = 64, 32
GRID   = 100
VP     = 18
FPS    = 60
HH     = 64
PW     = 240
MW     = SW - PW

def c(r,g,b): return (r,g,b)

SKY1=c(5,8,24);   SKY2=c(18,36,88)
GRA =c(32,80,22); GRB =c(42,102,28)
ROAD_C=c(48,48,58); ROAD_L=c(205,185,50)
WHITE=c(240,238,230); DIM=c(102,100,95); GOLD=c(255,200,45)
HUDC=c(7,11,26); PANC=c(9,14,32); BDR=c(38,50,90)

BC = {
    "res"    :(c(45,168,85),   c(20,102,48),  c(65,208,105)),
    "com"    :(c(40,115,212),  c(16,65,145),  c(55,145,252)),
    "office" :(c(32,102,202),  c(14,55,135),  c(48,132,245)),
    "ind"    :(c(208,135,20),  c(125,78,8),   c(245,165,35)),
    "garden" :(c(28,155,52),   c(10,95,30),   c(42,192,68)),
    "apark"  :(c(162,45,208),  c(92,20,135),  c(202,65,245)),
    "theatre":(c(185,40,160),  c(112,16,102), c(225,60,202)),
    "hosp"   :(c(240,240,248), c(175,175,185),c(255,255,255)),
    "police" :(c(22,55,175),   c(10,28,115),  c(32,75,215)),
    "railway":(c(192,175,152), c(125,112,95), c(215,198,175)),
    "airport":(c(168,180,205), c(108,120,145),c(188,200,225)),
}
ACC = {
    "road":c(78,78,95),"res":c(40,185,85),"com":c(48,135,235),
    "office":c(36,115,225),"ind":c(225,140,22),"garden":c(30,195,68),
    "apark":c(175,50,218),"theatre":c(195,45,165),"hosp":c(220,48,48),
    "police":c(48,95,225),"railway":c(195,155,25),"airport":c(95,75,225),
}
FP = {"road":1,"res":1,"com":1,"office":2,"ind":2,"garden":1,
      "apark":3,"theatre":1,"hosp":2,"police":1,"railway":3,"airport":4}
BH = {"road":0,"res":26,"com":32,"office":50,"ind":40,"garden":18,
      "apark":36,"theatre":28,"hosp":46,"police":30,"railway":34,"airport":30}

CATALOGUE = [
    ("road",  "road",    "Road",         100, 1),
    ("build", "res",     "House",        500, 1),
    ("build", "com",     "Shop",         800, 1),
    ("build", "office",  "Office Block", 1200,2),
    ("build", "ind",     "Factory",      1400,2),
    ("rec",   "garden",  "Garden",       600, 1),
    ("rec",   "apark",   "Amusement Pk", 2000,3),
    ("rec",   "theatre", "Theatre",      900, 1),
    ("util",  "hosp",    "Hospital",     2000,2),
    ("util",  "police",  "Police Stn",   1000,1),
    ("trans", "railway", "Railway Stn",  3000,3),
    ("trans", "airport", "Airport",      5000,4),
]
CAT_C={"road":c(78,78,98),"build":c(36,128,215),"rec":c(28,165,75),
       "util":c(195,52,52),"trans":c(115,55,212)}
CAT_L={"road":"── ROADS","build":"── BUILDINGS","rec":"── RECREATION",
       "util":"── UTILITIES","trans":"── TRANSPORT"}
B2K={"Road":"road","Residential":"res","Commercial":"com","Industrial":"ind",
     "OutdoorRecreation":"garden","IndoorRecreation":"theatre",
     "Utility":"hosp","Airport":"airport","RailwayStation":"railway"}

# ── ISO MATH ──────────────────────────────────────────────────────────────────
def t2s(row, col, cr, cc, ox, oy):
    r, c2 = row-cr, col-cc
    return (c2-r)*(TW//2)+ox, (c2+r)*(TH//2)+oy

def s2t(mx, my, cr, cc, ox, oy):
    my -= HH
    dx, dy = mx-ox, my-oy
    col = (dx/(TW//2)+dy/(TH//2))/2+cc
    row = (dy/(TH//2)-dx/(TW//2))/2+cr
    return int(math.floor(row)), int(math.floor(col))

# ── PRIMITIVES ────────────────────────────────────────────────────────────────
def fill_tile(surf, sx, sy, col, a=255, tw=TW, th=TH):
    sx,sy=int(sx),int(sy)
    pts=[(sx,sy),(sx+tw//2,sy+th//2),(sx,sy+th),(sx-tw//2,sy+th//2)]
    if a==255:
        pygame.draw.polygon(surf,col,pts)
    else:
        s=pygame.Surface((tw+2,th+2),pygame.SRCALPHA)
        lp=[(p[0]-sx+tw//2,p[1]-sy) for p in pts]
        pygame.draw.polygon(s,(*col[:3],a),lp)
        surf.blit(s,(sx-tw//2,sy))

def edge_tile(surf, sx, sy, col, w=2, a=200):
    sx,sy=int(sx),int(sy)
    s=pygame.Surface((TW+6,TH+6),pygame.SRCALPHA)
    lp=[(TW//2+3,1),(TW+4,TH//2+2),(TW//2+3,TH+3),(2,TH//2+2)]
    pygame.draw.polygon(s,(*col[:3],a),lp,w)
    surf.blit(s,(sx-TW//2-3,sy-1))

def draw_box(surf, sx, sy, h, top_c, left_c, right_c):
    sx,sy,h=int(sx),int(sy),int(h)
    hw=TW//2; hh=TH//2
    faces=[
        ([(sx-hw,sy+hh-h),(sx,sy+TH-h),(sx,sy+TH),(sx-hw,sy+hh)],   left_c),
        ([(sx,sy+TH-h),(sx+hw,sy+hh-h),(sx+hw,sy+hh),(sx,sy+TH)],   right_c),
        ([(sx,sy-h),(sx+hw,sy+hh-h),(sx,sy+TH-h),(sx-hw,sy+hh-h)],  top_c),
    ]
    for pts,col in faces:
        xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
        x0,y0=min(xs)-2,min(ys)-2; x1,y1=max(xs)+2,max(ys)+2
        s=pygame.Surface((x1-x0,y1-y0),pygame.SRCALPHA)
        lp=[(p[0]-x0,p[1]-y0) for p in pts]
        pygame.draw.polygon(s,(*col[:3],255),lp)
        surf.blit(s,(x0,y0))

def rbox(surf, rect, col, r=8, a=255, bc=None, bw=1):
    s=pygame.Surface((rect[2],rect[3]),pygame.SRCALPHA)
    pygame.draw.rect(s,(*col[:3],a),(0,0,rect[2],rect[3]),border_radius=r)
    if bc: pygame.draw.rect(s,(*bc[:3],a),(0,0,rect[2],rect[3]),bw,border_radius=r)
    surf.blit(s,(rect[0],rect[1]))

def wtxt(surf, text, font, col, x, y, sh=True):
    if sh: surf.blit(font.render(text,True,(0,0,0)),(x+1,y+1))
    surf.blit(font.render(text,True,col),(x,y))

# ── DECORATIONS ───────────────────────────────────────────────────────────────
def decor_res(surf, sx, sy, h):
    sx,sy,h=int(sx),int(sy),int(h)
    hw=TW//2; hh=TH//2
    peak=(sx, sy-h-hh-6)
    rl=[(sx-hw,sy+hh-h),(sx,sy+TH-h),peak]
    rr=[(sx,sy+TH-h),(sx+hw,sy+hh-h),peak]
    pygame.draw.polygon(surf,c(25,115,55),rl)
    pygame.draw.polygon(surf,c(38,152,78),rr)
    pygame.draw.lines(surf,c(15,75,35),True,[rl[0],rl[1],rl[2]],1)
    cx2,cy2=sx+12,sy-h-10
    pygame.draw.rect(surf,c(85,58,42),(cx2,cy2,6,14))
    pygame.draw.rect(surf,c(105,72,52),(cx2-1,cy2-3,8,4))
    for wy in [sy-h+8,sy-h+19]:
        pygame.draw.rect(surf,c(255,242,142),(sx+5,wy,9,7))
        pygame.draw.rect(surf,c(195,185,105),(sx+5,wy,9,7),1)
    pygame.draw.rect(surf,c(65,38,20),(sx-4,sy+TH-h-13,7,12))

def decor_com(surf, sx, sy, h):
    sx,sy,h=int(sx),int(sy),int(h)
    for i,ay in enumerate(range(sy-h+4,sy+TH//2-h+2,5)):
        stripe=c(215,45,45) if i%2==0 else c(242,242,242)
        pygame.draw.line(surf,stripe,(sx-TW//2+3,ay),(sx-4,ay+TH//4),2)
    rbox(surf,(sx-18,sy-h+2,36,10),c(255,200,38),3,245)
    sf=pygame.font.SysFont("Consolas",7,bold=True)
    surf.blit(sf.render("SHOP",True,c(30,30,60)),(sx-12,sy-h+4))
    for wy in [sy-h+16,sy-h+26]:
        pygame.draw.rect(surf,c(180,225,255),(sx+5,wy,10,9))
        pygame.draw.rect(surf,c(130,175,210),(sx+5,wy,10,9),1)

def decor_office(surf, sx, sy, h):
    sx,sy,h=int(sx),int(sy),int(h)
    for wy in range(sy-h+6,sy+TH//2-5,8):
        pygame.draw.rect(surf,c(148,205,255),(sx+5,wy,9,5))
        pygame.draw.rect(surf,c(108,165,218),(sx+5,wy,9,5),1)
    for wy in range(sy-h+6,sy+TH//2-5,8):
        pygame.draw.rect(surf,c(118,175,228),(sx-22,wy,9,5))
    pygame.draw.line(surf,c(182,185,212),(sx,sy-h),(sx,sy-h-25),2)
    pygame.draw.circle(surf,c(255,72,72),(sx,sy-h-25),3)
    pygame.draw.circle(surf,c(255,148,148),(sx,sy-h-25),2)

def decor_ind(surf, sx, sy, h):
    sx,sy,h=int(sx),int(sy),int(h)
    pygame.draw.rect(surf,c(55,55,65),(sx+12,sy-h-26,11,28))
    pygame.draw.rect(surf,c(72,72,82),(sx+11,sy-h-30,13,6))
    pygame.draw.rect(surf,c(55,55,65),(sx-2,sy-h-18,7,20))
    pygame.draw.rect(surf,c(72,72,82),(sx-3,sy-h-22,9,5))
    for i,(ox2,oy2,r2) in enumerate([(sx+17,sy-h-34,7),(sx+20,sy-h-43,5),(sx+22,sy-h-51,4)]):
        s2=pygame.Surface((r2*2+2,r2*2+2),pygame.SRCALPHA)
        pygame.draw.circle(s2,(148,145,155,128-i*32),(r2+1,r2+1),r2)
        surf.blit(s2,(ox2-r2,oy2-r2))
    pygame.draw.rect(surf,c(28,22,12),(sx-14,sy+TH-h-14,10,13))

def decor_garden(surf, sx, sy, h):
    sx,sy,h=int(sx),int(sy),int(h)
    fill_tile(surf,sx,sy,c(26,110,36),160)
    for ox2,oy2,th2 in [(-14,-TH//2-10,15),(12,-TH//2-8,13),(0,-TH//2-18,17),(-3,-TH//2+0,11)]:
        bx,by=sx+ox2,sy+TH//2+oy2
        pygame.draw.line(surf,c(72,46,16),(bx,by),(bx,by+5),2)
        pygame.draw.polygon(surf,c(20,136,40),[(bx,by-th2),(bx-7,by),(bx+7,by)])
        pygame.draw.polygon(surf,c(26,158,50),[(bx,by-th2-4),(bx-5,by-th2+6),(bx+5,by-th2+6)])

def decor_apark(surf, sx, sy, h):
    sx,sy,h=int(sx),int(sy),int(h)
    cx2=sx; cy2=sy-h-35; R=26
    pygame.draw.circle(surf,c(88,25,138),(cx2+2,cy2+2),R,4)
    pygame.draw.circle(surf,c(188,58,228),(cx2,cy2),R,4)
    pygame.draw.circle(surf,c(215,90,248),(cx2,cy2),R-8,2)
    pygame.draw.circle(surf,c(225,95,252),(cx2,cy2),6)
    pygame.draw.circle(surf,c(255,255,255),(cx2,cy2),3)
    gcols=[c(255,75,75),c(255,205,38),c(38,198,255),c(78,252,118),
           c(255,138,38),c(188,75,255),c(255,75,188),c(78,205,255)]
    for i,ang in enumerate(range(0,360,45)):
        rad=math.radians(ang)
        ex2=int(cx2+R*math.cos(rad)); ey2=int(cy2+R*math.sin(rad))
        pygame.draw.line(surf,c(162,48,202),(cx2,cy2),(ex2,ey2),2)
        gc=gcols[i%len(gcols)]
        pygame.draw.rect(surf,gc,(ex2-4,ey2-3,8,6),border_radius=2)
        pygame.draw.rect(surf,c(0,0,0),(ex2-4,ey2-3,8,6),1,border_radius=2)
    pygame.draw.line(surf,c(105,60,145),(cx2-12,cy2+R),(cx2-20,cy2+R+22),3)
    pygame.draw.line(surf,c(105,60,145),(cx2+12,cy2+R),(cx2+20,cy2+R+22),3)
    pygame.draw.line(surf,c(105,60,145),(cx2-20,cy2+R+22),(cx2+20,cy2+R+22),2)
    pygame.draw.arc(surf,c(228,82,82),(cx2+22,cy2+R-8,42,28),0,math.pi,4)
    gate_x=cx2-38; gate_y=cy2+R+5
    pygame.draw.rect(surf,c(255,205,45),(gate_x,gate_y,28,18),2,border_radius=3)
    pygame.draw.arc(surf,c(255,205,45),(gate_x+4,gate_y-6,20,14),0,math.pi,3)
    for fx,fc in [(cx2-28,c(255,75,75)),(cx2-14,c(255,205,38)),
                  (cx2,c(38,198,255)),(cx2+14,c(78,252,118))]:
        pygame.draw.line(surf,c(175,155,115),(fx,cy2-R-5),(fx,cy2-R-18),1)
        pygame.draw.polygon(surf,fc,[(fx,cy2-R-18),(fx+8,cy2-R-14),(fx,cy2-R-10)])

def decor_theatre(surf, sx, sy, h):
    sx,sy,h=int(sx),int(sy),int(h)
    pygame.draw.ellipse(surf,c(195,50,175),(sx-18,sy-h-16,36,18))
    pygame.draw.ellipse(surf,c(215,75,198),(sx-18,sy-h-16,36,18),2)
    pygame.draw.arc(surf,c(22,12,42),(sx-10,sy-h+4,20,13),0,math.pi,3)
    for lx2 in range(-14,16,6):
        pygame.draw.circle(surf,c(255,228,75),(sx+lx2,sy-h-18),2)
    for cx3 in [sx+5,sx+12,sx+19]:
        pygame.draw.line(surf,c(218,205,188),(cx3,sy-h+4),(cx3,sy+TH//2-2),1)

def decor_hosp(surf, sx, sy, h):
    sx,sy,h=int(sx),int(sy),int(h)
    # Bright red cross — very visible on white building
    pygame.draw.rect(surf,c(215,25,25),(sx-4,sy-h+2,8,22))
    pygame.draw.rect(surf,c(215,25,25),(sx-10,sy-h+9,20,8))
    pygame.draw.rect(surf,c(255,255,255),(sx-4,sy-h+2,8,22),1)
    pygame.draw.rect(surf,c(255,255,255),(sx-10,sy-h+9,20,8),1)
    # Blue windows (distinct from police)
    for wy in [sy-h+30,sy-h+42]:
        pygame.draw.rect(surf,c(80,160,255),(sx+5,wy,9,8))
        pygame.draw.rect(surf,c(40,120,215),(sx+5,wy,9,8),1)
    for wy in [sy-h+30,sy-h+42]:
        pygame.draw.rect(surf,c(80,160,255),(sx-22,wy,9,8))
    # Green entrance
    pygame.draw.rect(surf,c(38,180,95),(sx-6,sy+TH-h-15,13,14))
    pygame.draw.rect(surf,c(25,130,65),(sx-6,sy+TH-h-15,13,14),1)
    # H label
    sf=pygame.font.SysFont("Consolas",9,bold=True)
    surf.blit(sf.render("H",True,c(255,255,255)),(sx-3,sy+TH-h-14))

def decor_police(surf, sx, sy, h):
    sx,sy,h=int(sx),int(sy),int(h)
    # Yellow badge star on dark blue building
    for ang in range(0,360,60):
        rad=math.radians(ang)
        ex2=int(sx+11*math.cos(rad)); ey2=int(sy-h+13+9*math.sin(rad))
        pygame.draw.line(surf,c(255,218,45),(sx,sy-h+13),(ex2,ey2),2)
    pygame.draw.circle(surf,c(255,218,45),(sx,sy-h+13),5)
    pygame.draw.circle(surf,c(255,255,255),(sx,sy-h+13),2)
    # Red + blue light bar on roof (very visible)
    rbox(surf,(sx-13,sy-h-6,26,7),c(20,20,20),2,245)
    pygame.draw.rect(surf,c(255,40,40),(sx-12,sy-h-5,12,5))
    pygame.draw.rect(surf,c(40,120,255),(sx+1,sy-h-5,12,5))
    # White windows
    for wy in [sy-h+22,sy-h+33]:
        pygame.draw.rect(surf,c(200,220,255),(sx+5,wy,9,7))
        pygame.draw.rect(surf,c(160,185,230),(sx+5,wy,9,7),1)
    # P label
    sf=pygame.font.SysFont("Consolas",9,bold=True)
    surf.blit(sf.render("PD",True,c(255,255,255)),(sx-6,sy+TH-h-14))

def decor_railway(surf, sx, sy, h):
    sx,sy,h=int(sx),int(sy),int(h)
    pygame.draw.rect(surf,c(115,95,72),(sx-5,sy-h-40,10,42))
    pygame.draw.circle(surf,c(215,198,155),(sx,sy-h-40),11)
    pygame.draw.circle(surf,c(52,42,32),(sx,sy-h-40),11,1)
    pygame.draw.line(surf,c(25,16,6),(sx,sy-h-40),(sx+5,sy-h-34),1)
    pygame.draw.line(surf,c(25,16,6),(sx,sy-h-40),(sx-2,sy-h-46),1)
    fill_tile(surf,sx,sy-h-2,c(75,62,52),200,TW+20,TH+10)
    pygame.draw.line(surf,c(78,75,68),(sx-24,sy+TH-h),(sx+24,sy+TH-h),2)
    for offset in [-6,6]:
        pygame.draw.line(surf,c(88,82,75),(sx-28,sy+TH//2+offset),(sx+28,sy+TH//2+offset),2)
    for xi in range(-24,28,8):
        pygame.draw.line(surf,c(78,72,65),(sx+xi,sy+TH//2-8),(sx+xi,sy+TH//2+10),2)

def decor_airport(surf, sx, sy, h):
    sx,sy,h=int(sx),int(sy),int(h)
    # Runway centre markings
    for i in range(-4,5):
        pygame.draw.line(surf,c(212,192,55),
            (sx+i*14,sy+TH//2-14),(sx+i*14,sy+TH//2+14),2)
    # Runway edges
    pygame.draw.line(surf,c(178,172,158),(sx-52,sy+TH//2-2),(sx+52,sy+TH//2-2),1)
    pygame.draw.line(surf,c(178,172,158),(sx-52,sy+TH//2+2),(sx+52,sy+TH//2+2),1)
    # Terminal building
    pygame.draw.rect(surf,c(172,182,205),(sx-42,sy-h-2,32,h+10))
    pygame.draw.rect(surf,c(192,202,225),(sx-42,sy-h-2,32,h+10),1)
    for wy in range(sy-h+2,sy-2,7):
        pygame.draw.rect(surf,c(95,198,255),(sx-38,wy,6,5))
        pygame.draw.rect(surf,c(95,198,255),(sx-28,wy,6,5))
    # Control tower
    pygame.draw.rect(surf,c(135,145,175),(sx+28,sy-h-32,13,h+34))
    pygame.draw.rect(surf,c(152,162,192),(sx+24,sy-h-36,21,10))
    pygame.draw.rect(surf,c(92,195,255),(sx+25,sy-h-34,19,8),1)
    # Beacon
    pygame.draw.circle(surf,c(255,75,75),(sx+34,sy-h-38),4)
    pygame.draw.circle(surf,c(255,175,175),(sx+34,sy-h-38),2)
    # Taxiway lights
    for i in range(-3,4):
        pygame.draw.circle(surf,c(52,222,108),(sx+i*14,sy+TH+8),2)
    # Plane
    fnt=pygame.font.SysFont("Segoe UI Emoji",24)
    plane=fnt.render("✈",True,c(222,228,245))
    surf.blit(plane,(sx-45,sy-h+4))

DECOR={
    "res":decor_res,"com":decor_com,"office":decor_office,"ind":decor_ind,
    "garden":decor_garden,"apark":decor_apark,"theatre":decor_theatre,
    "hosp":decor_hosp,"police":decor_police,"railway":decor_railway,"airport":decor_airport,
}

# ── PARTICLES ─────────────────────────────────────────────────────────────────
class Particle:
    def __init__(self,x,y,col):
        self.x=x+random.randint(-22,22); self.y=y+random.randint(-8,8)
        self.vx=random.uniform(-2.5,2.5); self.vy=random.uniform(-5,-1.2)
        self.life=1.0; self.decay=random.uniform(0.018,0.042)
        self.col=col[:3]; self.r=random.randint(3,8)
    def update(self):
        self.x+=self.vx; self.y+=self.vy; self.vy+=0.14; self.life-=self.decay
    def draw(self,surf):
        if self.life<=0: return
        a=int(self.life*255)
        s=pygame.Surface((self.r*2+2,self.r*2+2),pygame.SRCALPHA)
        pygame.draw.circle(s,(*self.col,a),(self.r+1,self.r+1),self.r)
        surf.blit(s,(int(self.x)-self.r,int(self.y)-self.r))

class Note:
    def __init__(self,text,col,dur=2.8):
        self.text=text; self.col=col[:3]; self.timer=dur; self.yo=32
    def update(self,dt): self.timer-=dt; self.yo=max(0,self.yo-2.8)
    @property
    def alive(self): return self.timer>0
    @property
    def alpha(self): return int(min(1.0,self.timer/0.5)*215)

# ── BUTTONS ───────────────────────────────────────────────────────────────────
class Btn:
    def __init__(self,rect,lbl,col,font):
        self.rect=pygame.Rect(rect); self.lbl=lbl; self.col=col; self.font=font; self.hov=False
    def ev(self,e):
        if e.type==pygame.MOUSEMOTION: self.hov=self.rect.collidepoint(e.pos)
        if e.type==pygame.MOUSEBUTTONDOWN and e.button==1:
            if self.rect.collidepoint(e.pos): return True
        return False
    def draw(self,surf):
        col=tuple(min(255,v+50) for v in self.col) if self.hov else self.col
        rbox(surf,self.rect,col,7,225,bc=tuple(min(255,v+100) for v in self.col),bw=2)
        l=self.font.render(self.lbl,True,WHITE)
        surf.blit(l,(self.rect.centerx-l.get_width()//2,self.rect.centery-l.get_height()//2))

class BBtn:
    def __init__(self,rect,idx,font,sfont):
        self.rect=pygame.Rect(rect); self.idx=idx; self.font=font; self.sfont=sfont
        self.hov=False; self.sel=False
        _,key,name,cost,fp2=CATALOGUE[idx]
        self.key=key; self.name=name; self.cost=cost; self.fp2=fp2
        self.acc=ACC.get(key,c(100,100,120))
    def ev(self,e):
        if e.type==pygame.MOUSEMOTION: self.hov=self.rect.collidepoint(e.pos)
        if e.type==pygame.MOUSEBUTTONDOWN and e.button==1:
            if self.rect.collidepoint(e.pos): return True
        return False
    def draw(self,surf):
        bg=(24,30,62) if self.sel else (16,20,46)
        bc=tuple(min(255,v+90) for v in self.acc) if self.sel else (45,55,98)
        rbox(surf,self.rect,bg,6,238,bc=bc,bw=2 if self.sel else 1)
        if self.sel:
            gl=pygame.Surface((self.rect.w+10,self.rect.h+10),pygame.SRCALPHA)
            pygame.draw.rect(gl,(*self.acc,28),(0,0,self.rect.w+10,self.rect.h+10),border_radius=8)
            surf.blit(gl,(self.rect.x-5,self.rect.y-5))
            pygame.draw.rect(surf,self.acc,(self.rect.x,self.rect.y,3,self.rect.h),border_radius=2)
        rbox(surf,(self.rect.x+self.rect.w-30,self.rect.y+4,26,14),(40,50,92),3,210)
        fp_l=self.sfont.render(f"{self.fp2}×{self.fp2}",True,(130,150,210))
        surf.blit(fp_l,(self.rect.x+self.rect.w-28,self.rect.y+5))
        ef=pygame.font.SysFont("Consolas",14,bold=True)
        ic=ef.render(self.key[:2].upper(),True,self.acc if self.sel else tuple(min(255,v+50) for v in self.acc))
        surf.blit(ic,(self.rect.x+7,self.rect.centery-ic.get_height()//2))
        nc=WHITE if self.sel else DIM
        surf.blit(self.font.render(self.name,True,nc),(self.rect.x+32,self.rect.y+5))
        cc2=GOLD if self.sel else (85,85,115)
        surf.blit(self.sfont.render(f"${self.cost:,}",True,cc2),(self.rect.x+32,self.rect.y+20))

# ── MINIMAP ───────────────────────────────────────────────────────────────────
def draw_minimap(surf,grid,cr,cc,x,y,sz,font):
    mm=pygame.Surface((sz,sz),pygame.SRCALPHA)
    mm.fill((5,9,22,228))
    cell=sz/GRID
    KC={"road":c(65,65,82),"res":c(35,172,82),"com":c(45,120,218),
        "office":c(38,108,215),"ind":c(198,130,28),"garden":c(28,175,68),
        "apark":c(158,48,198),"theatre":c(188,48,158),"hosp":c(198,46,46),
        "police":c(44,88,208),"railway":c(188,148,26),"airport":c(88,68,215)}
    for r in range(GRID):
        for c2 in range(GRID):
            k=grid[r][c2]
            if k=="empty" or k.startswith("_"): continue
            col=KC.get(k,c(55,55,75))
            fp2=FP.get(k,1)
            px2,py2=int(c2*cell),int(r*cell)
            sz2=max(2,int(cell*fp2))
            mm.fill(col,(px2,py2,sz2,sz2))
    vx=int(cc*sz/GRID); vy=int(cr*sz/GRID)
    vw=max(4,int(VP*sz/GRID)); vh=max(4,int(VP*sz/GRID))
    pygame.draw.rect(mm,(78,198,255,208),(vx,vy,vw,vh),2)
    pygame.draw.rect(mm,(45,58,115,188),(0,0,sz,sz),1)
    surf.blit(mm,(x,y))
    l=font.render("MINIMAP",True,(75,85,125))
    surf.blit(l,(x+sz//2-l.get_width()//2,y-15))

# ── GAME ──────────────────────────────────────────────────────────────────────
class Game:
    def __init__(self):
        self.screen=pygame.display.set_mode((SW,SH))
        pygame.display.set_caption("City Builder — PimpriCity")
        self.clock=pygame.time.Clock()
        self.F={
            "big"  :pygame.font.SysFont("Consolas",22,bold=True),
            "hud"  :pygame.font.SysFont("Consolas",13,bold=True),
            "btn"  :pygame.font.SysFont("Consolas",11,bold=True),
            "small":pygame.font.SysFont("Consolas",10),
            "stat" :pygame.font.SysFont("Consolas",12,bold=True),
        }
        self.ox=MW//2; self.oy=SH//5+HH
        self.city=city_engine.City("PimpriCity",GRID) if BACKEND else None
        self.grid=[["empty"]*GRID for _ in range(GRID)]
        self.cr=0; self.cc=0
        self.sel=None; self.demo=False; self.hr=-1; self.hc=-1
        self.budget=50000; self.pop=0; self.joy=50; self.turn=1
        self.parts=[]; self.notes=[]; self.tod=0.0
        self.stars=[(random.randint(0,SW),random.randint(0,HH+180),
                     random.uniform(0.3,1.0)) for _ in range(110)]
        self._mk_ui(); self._sync()

    def _mk_ui(self):
        px=SW-PW+8; pw=PW-16
        self.bbtns=[]; y=HH+8; cur=None
        for i,b in enumerate(CATALOGUE):
            if b[0]!=cur: cur=b[0]; y+=20
            self.bbtns.append(BBtn((px,y,pw,34),i,self.F["btn"],self.F["small"]))
            y+=37
        self.btn_turn=Btn((SW-PW+8,SH-56,PW-16,44),"NEXT TURN  ▶",c(30,98,50),self.F["hud"])
        self.btn_demo=Btn((SW-PW+8,SH-104,PW-16,38),"DEMOLISH  ✕",c(122,30,30),self.F["btn"])

    def _sync(self):
        if not self.city: return
        self.budget=self.city.getBudget(); self.pop=self.city.getPopulation()
        self.joy=self.city.getHappiness(); self.turn=self.city.getTurn()
        raw=self.city.getGridState()
        for r in range(GRID):
            for c2 in range(GRID):
                bn=raw[r][c2]
                self.grid[r][c2]=B2K.get(bn,"empty") if bn!="empty" else "empty"

    def note(self,text,col=None): self.notes.append(Note(text,col or c(32,198,108)))
    def burst(self,sx,sy,col,n=14):
        for _ in range(n): self.parts.append(Particle(sx,sy,col))

    def _fp_ok(self,row,col,fp2):
        for dr in range(fp2):
            for dc in range(fp2):
                nr,nc=row+dr,col+dc
                if not(0<=nr<GRID and 0<=nc<GRID): return False
                if self.grid[nr][nc]!="empty": return False
        return True

    def place(self,row,col):
        if self.sel is None: return
        _,key,name,cost,fp2=CATALOGUE[self.sel]
        if not self._fp_ok(row,col,fp2):
            self.note("Cannot place here!",c(215,48,48)); return
        if self.budget<cost:
            self.note(f"Need ${cost:,}!",c(215,48,48)); return
        ok=False
        if self.city:
            if   key=="road"            : ok=self.city.placeRoad(row,col)
            elif key=="res"             : ok=self.city.placeResidential(row,col)
            elif key in("com","office") : ok=self.city.placeCommercial(row,col,"shop")
            elif key=="ind"             : ok=self.city.placeIndustrial(row,col)
            elif key=="garden"          : ok=self.city.placeOutdoorRec(row,col,"garden")
            elif key=="apark"           : ok=self.city.placeOutdoorRec(row,col,"amusement_park")
            elif key=="theatre"         : ok=self.city.placeIndoorRec(row,col,"theatre")
            elif key=="hosp"            : ok=self.city.placeUtility(row,col,"hospital")
            elif key=="police"          : ok=self.city.placeUtility(row,col,"police")
            elif key=="airport"         : ok=self.city.placeAirport(row,col)
            elif key=="railway"         : ok=self.city.placeRailway(row,col)
        else:
            self.budget-=cost; ok=True
        if ok:
            for dr in range(fp2):
                for dc in range(fp2):
                    self.grid[row+dr][col+dc]=key if(dr==0 and dc==0) else f"_{key}"
            self._sync()
            sx,sy=t2s(row,col,self.cr,self.cc,self.ox,self.oy)
            self.burst(int(sx),int(sy)+TH,ACC.get(key,c(100,100,120)))
            self.note(f"{name} placed!  −${cost:,}",ACC.get(key,c(32,198,108)))
        else:
            self.note("Cannot place here!",c(215,48,48))

    def demolish(self,row,col):
        key=self.grid[row][col]
        if key=="empty": self.note("Nothing here!",DIM); return
        root=key.lstrip("_")
        fp2=FP.get(root,1)
        for dr in range(fp2):
            for dc in range(fp2):
                nr,nc=row-dr,col-dc
                if 0<=nr<GRID and 0<=nc<GRID and self.grid[nr][nc]==root:
                    for r2 in range(fp2):
                        for c2 in range(fp2):
                            if 0<=nr+r2<GRID and 0<=nc+c2<GRID:
                                self.grid[nr+r2][nc+c2]="empty"
                    if self.city: self.city.removeObject(nr,nc); self._sync()
                    sx,sy=t2s(row,col,self.cr,self.cc,self.ox,self.oy)
                    self.burst(int(sx),int(sy)+TH,c(215,48,48),10)
                    self.note("Demolished!",c(215,48,48)); return
        self.grid[row][col]="empty"
        if self.city: self.city.removeObject(row,col); self._sync()
        self.note("Demolished!",c(215,48,48))

    def next_turn(self):
        if self.city: self.city.nextTurn(); self._sync()
        else:
            self.turn+=1; self.budget+=random.randint(350,950)
            self.joy=max(0,min(100,self.joy+random.randint(-4,9)))
            self.pop+=random.randint(0,14)
        self.note(f"Turn {self.turn} — income collected!",GOLD)

    def draw_bg(self):
        t=(math.sin(self.tod*math.pi)+1)/2
        sky=tuple(int(SKY1[i]+(SKY2[i]-SKY1[i])*t) for i in range(3))
        self.screen.fill(sky)
        sa=int(255*(1-t))
        if sa>10:
            for sx2,sy2,sz2 in self.stars:
                s2=pygame.Surface((4,4),pygame.SRCALPHA)
                pygame.draw.circle(s2,(255,255,255,sa),(2,2),max(1,int(sz2*2)))
                self.screen.blit(s2,(sx2,sy2))

    def draw_map(self):
        bldg_list=[]
        # Pass 1: ground tiles
        for row in range(self.cr+VP+2,self.cr-3,-1):
            for col in range(self.cc-2,self.cc+VP+4):
                if not(0<=row<GRID and 0<=col<GRID): continue
                sx,sy=t2s(row,col,self.cr,self.cc,self.ox,self.oy)
                sx,sy=int(sx),int(sy)
                if sx<-TW or sx>MW+TW: continue
                if sy<HH-TH or sy>SH+TH*3: continue
                grass=GRA if(row+col)%2==0 else GRB
                fill_tile(self.screen,sx,sy,grass)
                k=self.grid[row][col]
                if k=="road":
                    fill_tile(self.screen,sx,sy,ROAD_C)
                    for dx in [-18,-9,0,9,18]:
                        pygame.draw.line(self.screen,ROAD_L,(sx+dx,sy+TH//2-2),(sx+dx,sy+TH//2+2),1)
                if k not in("empty","road") and not k.startswith("_"):
                    bldg_list.append((row,col,sx,sy,k))

        # Pass 2: buildings back to front
        bldg_list.sort(key=lambda x:x[0]+x[1])
        for row,col,sx,sy,key in bldg_list:
            fp2=FP.get(key,1)
            h=BH.get(key,24)
            cols=BC.get(key,(c(82,82,98),c(46,46,60),c(102,102,120)))
            top_c,left_c,right_c=cols
            if fp2>1:
                # Centre of footprint in grid space
                cr2=row+(fp2-1)/2.0; cc2=col+(fp2-1)/2.0
                csx,csy=t2s(cr2,cc2,self.cr,self.cc,self.ox,self.oy)
                csx,csy=int(csx),int(csy)
                fill_tile(self.screen,csx,csy,top_c,80,TW*fp2,TH*fp2)
                draw_box(self.screen,csx,csy,h,top_c,left_c,right_c)
                fn=DECOR.get(key)
                if fn: fn(self.screen,csx,csy,h)
            else:
                draw_box(self.screen,sx,sy,h,top_c,left_c,right_c)
                fn=DECOR.get(key)
                if fn: fn(self.screen,sx,sy,h)

        # Pass 3: hover
        if 0<=self.hr<GRID and 0<=self.hc<GRID:
            sx,sy=t2s(self.hr,self.hc,self.cr,self.cc,self.ox,self.oy)
            sx,sy=int(sx),int(sy)
            if self.demo:
                edge_tile(self.screen,sx,sy,c(215,48,48),3,225)
            elif self.sel is not None:
                fp2=CATALOGUE[self.sel][4]
                ok=self._fp_ok(self.hr,self.hc,fp2)
                hl=c(32,195,138) if ok else c(215,48,48)
                edge_tile(self.screen,sx,sy,hl,3,228)
                if ok and fp2>1:
                    for dr in range(fp2):
                        for dc in range(fp2):
                            if dr==0 and dc==0: continue
                            nr,nc=self.hr+dr,self.hc+dc
                            if 0<=nr<GRID and 0<=nc<GRID:
                                fsx,fsy=t2s(nr,nc,self.cr,self.cc,self.ox,self.oy)
                                fill_tile(self.screen,int(fsx),int(fsy),c(32,195,138),52)
                                edge_tile(self.screen,int(fsx),int(fsy),c(32,195,138),2,130)
            else:
                edge_tile(self.screen,sx,sy,DIM,2,95)

    def draw_hud(self):
        rbox(self.screen,(0,0,SW,HH),HUDC,0,250,bc=BDR,bw=1)
        title=self.F["big"].render("PIMPRI CITY",True,GOLD)
        self.screen.blit(title,(14,HH//2-title.get_height()//2))
        jcol=c(32,195,108) if self.joy>60 else c(235,148,28) if self.joy>30 else c(215,48,48)
        for val,col2,label,x in [
            (f"${self.budget:,}",c(32,195,108),"BUDGET",165),
            (f"{self.pop:,}",    c(45,135,250),"POPULATION",335),
            (f"{self.joy}%",     jcol,         "HAPPINESS",505),
            (f"Turn {self.turn}",c(145,85,250),"TURN",655),
        ]:
            rbox(self.screen,(x,5,152,54),(17,22,50),8,215,bc=(45,55,108),bw=1)
            self.screen.blit(self.F["small"].render(label,True,(78,82,128)),(x+8,9))
            self.screen.blit(self.F["stat"].render(val,True,col2),(x+8,26))
        rbox(self.screen,(505,46,150,7),(12,14,38),4,185)
        fw=int(self.joy/100*148)
        if fw>0: rbox(self.screen,(505,46,fw,7),jcol,4,228)
        rbox(self.screen,(835,5,200,54),(17,22,50),8,188,bc=(45,55,108),bw=1)
        for i,(t2,col2) in enumerate([
            ("WASD / Arrows — move",c(68,75,118)),
            ("Shift — move faster", c(68,75,118)),
            ("ESC / RClick — cancel",c(68,75,118)),
        ]):
            self.screen.blit(self.F["small"].render(t2,True,col2),(843,9+i*15))

    def draw_panel(self):
        px=SW-PW
        rbox(self.screen,(px,HH,PW,SH-HH),PANC,0,250,bc=BDR,bw=1)
        y=HH+8; cur=None
        for i,btn in enumerate(self.bbtns):
            cat=CATALOGUE[i][0]
            if cat!=cur:
                cur=cat; cc2=CAT_C[cat]
                l=self.F["small"].render(CAT_L[cat],True,cc2)
                self.screen.blit(l,(px+8,y+4))
                pygame.draw.line(self.screen,(*cc2,75),
                    (px+8+l.get_width()+5,y+11),(px+PW-6,y+11),1)
                y+=20
            btn.rect.y=y; btn.sel=(i==self.sel); btn.draw(self.screen); y+=37
        mms=PW-18; mmy=SH-mms-118
        draw_minimap(self.screen,self.grid,self.cr,self.cc,px+9,mmy,mms,self.F["small"])
        self.btn_demo.draw(self.screen)
        self.btn_turn.draw(self.screen)

    def draw_notes(self):
        y=SH-158
        for n in self.notes:
            a=max(0,min(255,n.alpha)); r2,g2,b2=n.col
            s=pygame.Surface((368,35),pygame.SRCALPHA)
            bg=pygame.Surface((368,35),pygame.SRCALPHA)
            pygame.draw.rect(bg,(r2,g2,b2,min(155,a)),(0,0,368,35),border_radius=7)
            s.blit(bg,(0,0))
            bar=pygame.Surface((4,35),pygame.SRCALPHA)
            pygame.draw.rect(bar,(r2,g2,b2,min(255,a+50)),(0,0,4,35))
            s.blit(bar,(0,0))
            s.blit(self.F["hud"].render(n.text,True,WHITE),(14,35//2-self.F["hud"].get_height()//2))
            self.screen.blit(s,(MW//2-184,y-int(n.yo))); y-=42

    def draw_sel(self):
        if self.demo:
            s=pygame.Surface((MW,26),pygame.SRCALPHA); s.fill((185,28,28,132))
            self.screen.blit(s,(0,HH))
            wtxt(self.screen,"  DEMOLISH MODE — click building to remove   |   ESC to cancel",
                 self.F["btn"],WHITE,10,HH+5,False)
            return
        if self.sel is None: return
        _,key,name,cost,fp2=CATALOGUE[self.sel]
        acc=ACC.get(key,c(100,100,120))
        rbox(self.screen,(8,SH-50,360,42),(11,15,38),8,228,bc=(48,58,108),bw=1)
        ef=pygame.font.SysFont("Consolas",17,bold=True)
        self.screen.blit(ef.render(key[:2].upper(),True,acc),(16,SH-46))
        wtxt(self.screen,name,self.F["hud"],acc,44,SH-46)
        wtxt(self.screen,f"${cost:,}   {fp2}×{fp2} tiles   click grid to place",
             self.F["small"],DIM,44,SH-30,False)

    def run(self):
        while True:
            dt=self.clock.tick(FPS)/1000.0
            self.tod=(self.tod+dt*0.014)%1.0
            for ev in pygame.event.get():
                if ev.type==pygame.QUIT: pygame.quit(); sys.exit()
                if ev.type==pygame.KEYDOWN and ev.key==pygame.K_ESCAPE:
                    self.sel=None; self.demo=False
                for i,btn in enumerate(self.bbtns):
                    if btn.ev(ev): self.sel=i; self.demo=False
                if self.btn_turn.ev(ev): self.next_turn()
                if self.btn_demo.ev(ev): self.demo=not self.demo; self.sel=None
                if ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1:
                    mx,my=ev.pos
                    if mx<MW and my>HH:
                        row,col=s2t(mx,my,self.cr,self.cc,self.ox,self.oy)
                        if 0<=row<GRID and 0<=col<GRID:
                            if self.demo: self.demolish(row,col)
                            else: self.place(row,col)
                if ev.type==pygame.MOUSEBUTTONDOWN and ev.button==3:
                    self.sel=None; self.demo=False
            keys=pygame.key.get_pressed()
            spd=2 if keys[pygame.K_LSHIFT] else 1
            if keys[pygame.K_LEFT]  or keys[pygame.K_a]: self.cc=max(0,self.cc-spd)
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.cc=min(GRID-VP,self.cc+spd)
            if keys[pygame.K_UP]    or keys[pygame.K_w]: self.cr=max(0,self.cr-spd)
            if keys[pygame.K_DOWN]  or keys[pygame.K_s]: self.cr=min(GRID-VP,self.cr+spd)
            mx,my=pygame.mouse.get_pos()
            if mx<MW and my>HH: self.hr,self.hc=s2t(mx,my,self.cr,self.cc,self.ox,self.oy)
            else: self.hr=self.hc=-1
            self.parts=[p for p in self.parts if p.life>0]
            self.notes=[n for n in self.notes if n.alive]
            for p in self.parts: p.update()
            for n in self.notes: n.update(dt)
            self.draw_bg()
            self.draw_map()
            pygame.draw.rect(self.screen,PANC,(SW-PW,HH,PW,SH-HH))
            self.draw_panel()
            self.draw_hud()
            for p in self.parts: p.draw(self.screen)
            self.draw_notes()
            self.draw_sel()
            fps=self.F["small"].render(f"FPS {int(self.clock.get_fps())}",True,(38,42,72))
            self.screen.blit(fps,(4,SH-13))
            pygame.display.flip()

if __name__=="__main__":
    Game().run()