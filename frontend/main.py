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
    "com"    :(c(220,80,20),   c(155,45,10),  c(255,110,35)),
    "office" :(c(32,102,202),  c(14,55,135),  c(48,132,245)),
    "ind"    :(c(208,135,20),  c(125,78,8),   c(245,165,35)),
    "garden" :(c(28,155,52),   c(10,95,30),   c(42,192,68)),
    "apark"  :(c(80,20,140),   c(45,10,90),   c(115,35,195)),
    "theatre":(c(185,40,160),  c(112,16,102), c(225,60,202)),
    "hosp"   :(c(240,240,248), c(175,175,185),c(255,255,255)),
    "police" :(c(22,55,175),   c(10,28,115),  c(32,75,215)),
    "railway":(c(192,175,152), c(125,112,95), c(215,198,175)),
    "airport":(c(168,180,205), c(108,120,145),c(188,200,225)),
}
ACC = {
    "road":c(78,78,95),"res":c(40,185,85),"com":c(245,105,28),
    "office":c(36,115,225),"ind":c(225,140,22),"garden":c(30,195,68),
    "apark":c(185,55,255),"theatre":c(195,45,165),"hosp":c(220,48,48),
    "police":c(48,95,225),"railway":c(195,155,25),"airport":c(95,75,225),
}
FP = {"road":1,"res":1,"com":1,"office":2,"ind":2,"garden":1,
      "apark":3,"theatre":1,"hosp":2,"police":1,"railway":3,"airport":4}
BH = {"road":0,"res":26,"com":30,"office":52,"ind":40,"garden":18,
      "apark":20,"theatre":28,"hosp":46,"police":30,"railway":18,"airport":14}

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

B2K={
    "Road":"road","Residential":"res","Commercial":"com","Industrial":"ind",
    "IndoorRecreation":"theatre","Utility":"hosp",
    "Airport":"airport","RailwayStation":"railway",
}
KEEP_FRONTEND={"garden","apark","theatre","hosp","police",
               "_garden","_apark","_theatre","_hosp","_police"}

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

def draw_box(surf, sx, sy, h, top_c, left_c, right_c, fp=1):
    """
    Draw isometric box. sx,sy = TOP-TIP of footprint diamond = t2s(row,col).
    Footprint: top=(sx,sy) right=(sx+hw,sy+hh) bottom=(sx,sy+fh) left=(sx-hw,sy+hh)
    """
    sx,sy,h=int(sx),int(sy),int(h)
    hw=(TW*fp)//2; hh=(TH*fp)//2; fh=TH*fp
    faces=[
        ([(sx-hw,sy+hh-h),(sx,sy+fh-h),(sx,sy+fh),(sx-hw,sy+hh)],  left_c),
        ([(sx,sy+fh-h),(sx+hw,sy+hh-h),(sx+hw,sy+hh),(sx,sy+fh)],  right_c),
        ([(sx,sy-h),(sx+hw,sy+hh-h),(sx,sy+fh-h),(sx-hw,sy+hh-h)], top_c),
    ]
    for pts,col in faces:
        xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
        x0,y0=min(xs)-2,min(ys)-2; x1,y1=max(xs)+2,max(ys)+2
        s=pygame.Surface((x1-x0,y1-y0),pygame.SRCALPHA)
        lp=[(p[0]-x0,p[1]-y0) for p in pts]
        pygame.draw.polygon(s,(*col[:3],255),lp)
        surf.blit(s,(x0,y0))

def draw_shadow(surf, sx, sy, fp=1):
    """Draw a soft isometric shadow beneath a building."""
    sx,sy=int(sx),int(sy)
    hw=(TW*fp)//2+4; hh=(TH*fp)//2+2; fh=TH*fp+4
    s=pygame.Surface((hw*2+8,fh+8),pygame.SRCALPHA)
    pts=[(hw+4,2),(hw*2+6,hh+2),(hw+4,fh+6),(2,hh+2)]
    pygame.draw.polygon(s,(0,0,0,38),pts)
    surf.blit(s,(sx-hw-4,sy-2))

def rbox(surf, rect, col, r=8, a=255, bc=None, bw=1):
    s=pygame.Surface((rect[2],rect[3]),pygame.SRCALPHA)
    pygame.draw.rect(s,(*col[:3],a),(0,0,rect[2],rect[3]),border_radius=r)
    if bc: pygame.draw.rect(s,(*bc[:3],a),(0,0,rect[2],rect[3]),bw,border_radius=r)
    surf.blit(s,(rect[0],rect[1]))

def wtxt(surf, text, font, col, x, y, sh=True):
    if sh: surf.blit(font.render(text,True,(0,0,0)),(x+1,y+1))
    surf.blit(font.render(text,True,col),(x,y))

# ── PRE-CACHED FONTS (created once at startup, never inside draw loops) ───────
_FONTS = {}
def get_font(name, size, bold=False):
    k=(name,size,bold)
    if k not in _FONTS: _FONTS[k]=pygame.font.SysFont(name,size,bold=bold)
    return _FONTS[k]

# ── PRE-CACHED STAR SURFACE (drawn once) ─────────────────────────────────────
_STAR_SURF = None
_STAR_DATA = None
def get_star_surf(stars, alpha):
    """Return a surface with all stars at a given alpha (cached per alpha level)."""
    global _STAR_SURF, _STAR_DATA
    a=max(0,min(255,int(alpha)))
    if a==0: return None
    s=pygame.Surface((SW,HH+200),pygame.SRCALPHA)
    for sx2,sy2,sz2 in stars:
        r=max(1,int(sz2*2))
        pygame.draw.circle(s,(255,255,255,a),(sx2,sy2),r)
    return s

# ── GEOMETRY HELPERS ─────────────────────────────────────────────────────────
# sx,sy = TOP-TIP of footprint diamond.
# hw = TW*fp//2, hh = TH*fp//2, fh = TH*fp
# RIGHT face: top-left=(sx,sy+fh-h), top-right=(sx+hw,sy+hh-h), bot-right=(sx+hw,sy+hh), bot-left=(sx,sy+fh)
# LEFT  face: top-right=(sx,sy+fh-h), top-left=(sx-hw,sy+hh-h), bot-left=(sx-hw,sy+hh), bot-right=(sx,sy+fh)

def win_right(surf, sx, sy, h, fp, fx, fy, ww=9, wh=6,
              col=c(200,230,255), border=c(120,160,210)):
    sx,sy,h=int(sx),int(sy),int(h)
    hw=(TW*fp)//2; hh=(TH*fp)//2; fh=TH*fp
    top_y=(sy+fh-h)-fx*(fh-hh)
    bot_y=(sy+fh)  -fx*(fh-hh)
    x=sx+fx*hw
    y=top_y+fy*(bot_y-top_y)
    pygame.draw.rect(surf,col,(int(x),int(y),ww,wh))
    pygame.draw.rect(surf,border,(int(x),int(y),ww,wh),1)

def win_right_glow(surf, sx, sy, h, fp, fx, fy, ww=9, wh=6, night=0.0):
    """Window with night glow effect. night in [0,1]."""
    day_col=c(200,220,255); night_col=c(255,235,120)
    day_bdr=c(120,150,210); night_bdr=c(200,160,60)
    rc=tuple(int(day_col[i]+(night_col[i]-day_col[i])*night) for i in range(3))
    rb=tuple(int(day_bdr[i]+(night_bdr[i]-day_bdr[i])*night) for i in range(3))
    win_right(surf,sx,sy,h,fp,fx,fy,ww,wh,rc,rb)
    if night>0.3:
        sx2,sy2,h2=int(sx),int(sy),int(h)
        hw=(TW*fp)//2; hh=(TH*fp)//2; fh=TH*fp
        top_y=(sy2+fh-h2)-fx*(fh-hh)
        bot_y=(sy2+fh)   -fx*(fh-hh)
        x=sx2+fx*hw; y=top_y+fy*(bot_y-top_y)
        gl=pygame.Surface((ww+6,wh+6),pygame.SRCALPHA)
        pygame.draw.rect(gl,(255,220,80,int(120*night)),(0,0,ww+6,wh+6),border_radius=2)
        surf.blit(gl,(int(x)-3,int(y)-3))

def win_left(surf, sx, sy, h, fp, fx, fy, ww=9, wh=6,
             col=c(160,200,240), border=c(90,140,195)):
    sx,sy,h=int(sx),int(sy),int(h)
    hw=(TW*fp)//2; hh=(TH*fp)//2; fh=TH*fp
    top_y=(sy+fh-h)-fx*(fh-hh)
    bot_y=(sy+fh)  -fx*(fh-hh)
    x=sx-fx*hw
    y=top_y+fy*(bot_y-top_y)
    pygame.draw.rect(surf,col,(int(x)-ww,int(y),ww,wh))
    pygame.draw.rect(surf,border,(int(x)-ww,int(y),ww,wh),1)

# ── DECORATIONS ───────────────────────────────────────────────────────────────
# sx,sy = TOP-TIP of footprint diamond. fp = actual footprint size.
# night in [0,1]: 0=day, 1=night (for window glow)

def decor_res(surf, sx, sy, h, fp=1, night=0.0):
    sx,sy,h=int(sx),int(sy),int(h)
    hw=TW*fp//2; hh=TH*fp//2; fh=TH*fp
    peak=(sx, sy-h-hh-6)
    rl=[(sx-hw,sy+hh-h),(sx,sy+fh-h),peak]
    rr=[(sx,sy+fh-h),(sx+hw,sy+hh-h),peak]
    pygame.draw.polygon(surf,c(25,115,55),rl)
    pygame.draw.polygon(surf,c(38,152,78),rr)
    pygame.draw.lines(surf,c(15,75,35),True,rl,1)
    # Chimney
    cx2=sx+10; cy2=sy-h-8
    pygame.draw.rect(surf,c(85,58,42),(cx2,cy2,5,12))
    pygame.draw.rect(surf,c(105,72,52),(cx2-1,cy2-3,7,4))
    # Lit windows
    win_right_glow(surf,sx,sy,h,fp,0.25,0.25,9,7,night)
    win_right_glow(surf,sx,sy,h,fp,0.25,0.68,9,7,night)
    # Door
    pygame.draw.rect(surf,c(65,38,20),(sx-5,sy+fh-h-14,7,13))

def decor_com(surf, sx, sy, h, fp=1, night=0.0):
    sx,sy,h=int(sx),int(sy),int(h)
    hw=TW*fp//2; hh=TH*fp//2; fh=TH*fp
    # Awning stripes on left face
    for i in range(4):
        fy=0.05+i*0.14
        top_y=(sy+fh-h)
        stripe_y=int(top_y+fy*(h*0.4))
        col_stripe=c(245,110,30) if i%2==0 else c(255,240,220)
        pygame.draw.line(surf,col_stripe,(sx-hw+3,stripe_y),(sx-3,stripe_y+2),2)
    # Sign
    sign_y=sy+fh-h+2
    rbox(surf,(sx-hw+4,sign_y,hw-6,11),c(245,110,30),3,255,bc=c(200,70,10),bw=1)
    f=get_font("Consolas",7,True)
    surf.blit(f.render("SHOP",True,c(255,255,255)),(sx-hw+8,sign_y+2))
    # Windows
    win_right_glow(surf,sx,sy,h,fp,0.18,0.30,10,9,night)
    win_right_glow(surf,sx,sy,h,fp,0.18,0.70,10,9,night)
    # Door
    pygame.draw.rect(surf,c(120,55,15),(sx+2,sy+fh-h-14,8,13))

def decor_office(surf, sx, sy, h, fp=2, night=0.0):
    sx,sy,h=int(sx),int(sy),int(h)
    hw=TW*fp//2; hh=TH*fp//2; fh=TH*fp
    for fx in [0.15,0.45,0.72]:
        for row_i in range(6):
            fy=0.08+row_i*0.13
            win_right_glow(surf,sx,sy,h,fp,fx,fy,9,5,night)
    for fx in [0.25,0.65]:
        for row_i in range(5):
            fy=0.10+row_i*0.15
            win_left(surf,sx,sy,h,fp,fx,fy,9,5,c(100,165,228),c(60,120,185))
    # Rooftop
    pygame.draw.rect(surf,c(60,80,140),(sx-8,sy-h-4,16,5))
    pygame.draw.line(surf,c(180,190,215),(sx,sy-h),(sx,sy-h-30),2)
    pygame.draw.circle(surf,c(255,68,68),(sx,sy-h-30),3)
    f=get_font("Consolas",6,True)
    surf.blit(f.render("CORP",True,c(180,210,255)),(sx+4,sy+fh-h+3))

def decor_ind(surf, sx, sy, h, fp=2, night=0.0, tick=0):
    sx,sy,h=int(sx),int(sy),int(h)
    hw=TW*fp//2; hh=TH*fp//2; fh=TH*fp
    # Chimneys
    pygame.draw.rect(surf,c(55,55,65),(sx+10,sy-h-30,12,32))
    pygame.draw.rect(surf,c(72,72,82),(sx+9,sy-h-34,14,6))
    pygame.draw.rect(surf,c(55,55,65),(sx-6,sy-h-22,8,24))
    pygame.draw.rect(surf,c(72,72,82),(sx-7,sy-h-26,10,5))
    # Animated smoke — tick drives vertical offset
    for i,(bx,by,r2,speed) in enumerate([(sx+16,sy-h-38,7,1),(sx+16,sy-h-52,5,1.4),(sx+16,sy-h-64,3,1.8)]):
        offset=int((tick*speed*0.4+i*8)%20)
        s2=pygame.Surface((r2*2+2,r2*2+2),pygame.SRCALPHA)
        alpha=max(0,110-i*30-offset*3)
        pygame.draw.circle(s2,(148,145,155,alpha),(r2+1,r2+1),r2)
        surf.blit(s2,(bx-r2,by-offset-r2))
    # Windows
    win_right(surf,sx,sy,h,fp,0.20,0.25,10,6,c(180,160,100),c(120,105,60))
    win_right(surf,sx,sy,h,fp,0.55,0.25,10,6,c(180,160,100),c(120,105,60))
    win_right(surf,sx,sy,h,fp,0.20,0.60,10,6,c(180,160,100),c(120,105,60))
    win_right(surf,sx,sy,h,fp,0.55,0.60,10,6,c(180,160,100),c(120,105,60))
    # Door
    pygame.draw.rect(surf,c(28,22,12),(sx-hw+8,sy+fh-h-16,14,15))

def decor_garden(surf, sx, sy, h, fp=1, night=0.0):
    sx,sy,h=int(sx),int(sy),int(h)
    hw=TW*fp//2; hh=TH*fp//2; fh=TH*fp
    fill_tile(surf,sx,sy,c(26,110,36),160)
    tree_spots=[(-12,sy+hh-8,15),(12,sy+hh-8,13),(0,sy+hh//2-4,17),(-2,sy+hh+6,11)]
    for ox2,ty,th2 in tree_spots:
        bx=sx+ox2; by=ty
        pygame.draw.line(surf,c(72,46,16),(bx,by),(bx,by+5),2)
        pygame.draw.polygon(surf,c(20,136,40),[(bx,by-th2),(bx-7,by),(bx+7,by)])
        pygame.draw.polygon(surf,c(26,158,50),[(bx,by-th2-4),(bx-5,by-th2+6),(bx+5,by-th2+6)])

def decor_apark(surf, sx, sy, h, fp=3, night=0.0, tick=0):
    sx,sy,h=int(sx),int(sy),int(h)
    hw=(TW*fp)//2; hh=(TH*fp)//2; fh=TH*fp
    fill_tile(surf,sx,sy,c(48,15,85),160,TW*fp,TH*fp)
    # Animated ferris wheel
    cx2=sx-20; cy2=sy-h-42; R=30
    wheel_angle=tick*0.6  # degrees per frame
    pygame.draw.circle(surf,c(55,10,100),(cx2+3,cy2+3),R,5)
    pygame.draw.circle(surf,c(195,62,235),(cx2,cy2),R,5)
    pygame.draw.circle(surf,c(220,95,252),(cx2,cy2),R-10,2)
    pygame.draw.circle(surf,c(228,100,255),(cx2,cy2),7)
    pygame.draw.circle(surf,c(255,255,255),(cx2,cy2),3)
    gcols=[c(255,72,72),c(255,208,35),c(35,200,255),c(75,255,115),
           c(255,135,35),c(185,72,255),c(255,72,185),c(72,208,255)]
    for i,ang in enumerate(range(0,360,45)):
        rad=math.radians(ang+wheel_angle)
        ex2=int(cx2+R*math.cos(rad)); ey2=int(cy2+R*math.sin(rad))
        pygame.draw.line(surf,c(158,45,205),(cx2,cy2),(ex2,ey2),2)
        gc=gcols[i%len(gcols)]
        pygame.draw.rect(surf,gc,(ex2-4,ey2-4,9,7),border_radius=2)
        pygame.draw.rect(surf,c(15,10,25),(ex2-4,ey2-4,9,7),1,border_radius=2)
    pygame.draw.line(surf,c(108,58,148),(cx2-12,cy2+R),(cx2-18,cy2+R+20),3)
    pygame.draw.line(surf,c(108,58,148),(cx2+12,cy2+R),(cx2+18,cy2+R+20),3)
    pygame.draw.line(surf,c(108,58,148),(cx2-18,cy2+R+20),(cx2+18,cy2+R+20),2)
    # Roller coaster
    pygame.draw.arc(surf,c(235,85,85),(cx2+42,cy2+R-5,50,30),0,math.pi,5)
    pygame.draw.arc(surf,c(200,55,55),(cx2+44,cy2+R-3,46,26),0,math.pi,2)
    # Entrance
    gate_x=sx-14; gate_y=sy+hh-10
    pygame.draw.rect(surf,c(255,205,42),(gate_x,gate_y,28,18),2,border_radius=4)
    pygame.draw.arc(surf,c(255,205,42),(gate_x+4,gate_y-8,20,14),0,math.pi,3)
    # Flags
    top_y=sy-h-6
    for fx2,fc in [(-28,c(255,72,72)),(-14,c(255,208,35)),(0,c(35,200,255)),(14,c(75,255,115))]:
        pygame.draw.line(surf,c(175,155,112),(sx+fx2,top_y),(sx+fx2,top_y-14),1)
        pygame.draw.polygon(surf,fc,[(sx+fx2,top_y-14),(sx+fx2+9,top_y-10),(sx+fx2,top_y-6)])

def decor_theatre(surf, sx, sy, h, fp=1, night=0.0):
    sx,sy,h=int(sx),int(sy),int(h)
    hw=TW*fp//2; hh=TH*fp//2; fh=TH*fp
    dome_cx=sx; dome_cy=sy-h-8
    pygame.draw.ellipse(surf,c(195,50,175),(dome_cx-18,dome_cy-8,36,18))
    pygame.draw.ellipse(surf,c(215,75,198),(dome_cx-18,dome_cy-8,36,18),2)
    arch_y=sy+fh-h+4
    pygame.draw.arc(surf,c(22,12,42),(sx-8,arch_y,20,13),0,math.pi,3)
    # Marquee lights — blink at night
    light_col=c(255,228,75) if night<0.3 else (c(255,80,80) if int(pygame.time.get_ticks()//400)%2 else c(255,228,75))
    for lx2 in range(-14,16,6):
        pygame.draw.circle(surf,light_col,(sx+lx2,sy-h-2),2)
    for cx3 in [sx+6,sx+14,sx+22]:
        col_top_y=sy+fh-h+3; col_bot_y=sy+hh-2
        if col_bot_y>col_top_y:
            pygame.draw.line(surf,c(218,205,188),(cx3,col_top_y),(cx3,col_bot_y),1)

def decor_hosp(surf, sx, sy, h, fp=2, night=0.0):
    sx,sy,h=int(sx),int(sy),int(h)
    hw=TW*fp//2; hh=TH*fp//2; fh=TH*fp
    # Red cross
    cross_x=sx+8; cross_y=sy+fh-h+4
    pygame.draw.rect(surf,c(215,22,22),(cross_x-4,cross_y,8,22))
    pygame.draw.rect(surf,c(215,22,22),(cross_x-11,cross_y+7,22,8))
    pygame.draw.rect(surf,c(255,255,255),(cross_x-4,cross_y,8,22),1)
    pygame.draw.rect(surf,c(255,255,255),(cross_x-11,cross_y+7,22,8),1)
    # Windows
    for args in [(0.35,0.35),(0.65,0.35),(0.35,0.60),(0.65,0.60),(0.35,0.80),(0.65,0.80)]:
        win_right_glow(surf,sx,sy,h,fp,args[0],args[1],10,8,night)
    win_left(surf,sx,sy,h,fp,0.30,0.55,10,8,c(55,130,235),c(28,90,195))
    win_left(surf,sx,sy,h,fp,0.30,0.80,10,8,c(55,130,235),c(28,90,195))
    # Entrance
    ent_x=sx+4; ent_y=sy+fh-h-16
    pygame.draw.rect(surf,c(35,180,92),(ent_x,ent_y,15,15))
    pygame.draw.rect(surf,c(22,128,62),(ent_x,ent_y,15,15),1)
    f=get_font("Consolas",9,True)
    surf.blit(f.render("H",True,c(255,255,255)),(ent_x+3,ent_y+2))
    # Flashing emergency lights at night
    tick=pygame.time.get_ticks()
    r_on=(tick//300)%2==0; b_on=(tick//300)%2==1
    pygame.draw.circle(surf,c(255,55,55) if r_on else c(80,20,20),(sx-12,sy-h-5),4)
    pygame.draw.circle(surf,c(55,155,255) if b_on else c(15,40,80),(sx+12,sy-h-5),4)

def decor_police(surf, sx, sy, h, fp=1, night=0.0):
    sx,sy,h=int(sx),int(sy),int(h)
    hw=TW*fp//2; hh=TH*fp//2; fh=TH*fp
    # Gold badge
    badge_cx=sx+8; badge_cy=sy+fh-h+int(h*0.35)
    for ang in range(0,360,60):
        rad=math.radians(ang)
        ex2=int(badge_cx+12*math.cos(rad)); ey2=int(badge_cy+10*math.sin(rad))
        pygame.draw.line(surf,c(255,215,40),(badge_cx,badge_cy),(ex2,ey2),2)
    pygame.draw.circle(surf,c(255,215,40),(badge_cx,badge_cy),6)
    pygame.draw.circle(surf,c(255,255,255),(badge_cx,badge_cy),3)
    # Flashing light bar
    tick=pygame.time.get_ticks()
    r_on=(tick//200)%2==0
    rbox(surf,(sx-14,sy-h-7,28,8),c(18,18,28),2,255)
    pygame.draw.rect(surf,c(255,35,35) if r_on else c(80,15,15),(sx-13,sy-h-6,13,6))
    pygame.draw.rect(surf,c(35,115,255) if not r_on else c(10,35,80),(sx+1,sy-h-6,12,6))
    # Windows
    win_right_glow(surf,sx,sy,h,fp,0.22,0.30,10,8,night)
    win_right_glow(surf,sx,sy,h,fp,0.22,0.68,10,8,night)
    # PD sign
    pd_x=sx+2; pd_y=sy+fh-h-14
    pygame.draw.rect(surf,c(18,38,128),(pd_x,pd_y,18,13))
    f=get_font("Consolas",8,True)
    surf.blit(f.render("PD",True,c(255,215,40)),(pd_x+1,pd_y+2))

def decor_railway(surf, sx, sy, h, fp=3, night=0.0):
    sx,sy,h=int(sx),int(sy),int(h)
    hw=(TW*fp)//2; hh=(TH*fp)//2; fh=TH*fp
    fill_tile(surf,sx,sy,c(155,145,132),200,TW*fp,TH*fp)
    # Station building
    bw=60; bld_left=sx-bw//2; bld_top=sy-h-8; bld_h=h+8
    pygame.draw.rect(surf,c(198,182,162),(bld_left,bld_top,bw,bld_h))
    pygame.draw.rect(surf,c(215,200,178),(bld_left,bld_top,bw,bld_h),1)
    # Roof
    fill_tile(surf,sx,sy-h-10,c(78,65,52),220,TW+28,TH+14)
    # Clock tower
    pygame.draw.rect(surf,c(115,95,72),(sx-6,sy-h-52,12,46))
    pygame.draw.circle(surf,c(215,198,155),(sx,sy-h-52),13)
    pygame.draw.circle(surf,c(52,42,32),(sx,sy-h-52),13,1)
    pygame.draw.line(surf,c(25,16,6),(sx,sy-h-52),(sx+6,sy-h-44),2)
    pygame.draw.line(surf,c(25,16,6),(sx,sy-h-52),(sx-3,sy-h-60),1)
    # Rails
    rail_y1=sy+hh+4; rail_y2=sy+hh+10
    pygame.draw.line(surf,c(95,88,80),(sx-hw+8,rail_y1),(sx+hw-8,rail_y1),2)
    pygame.draw.line(surf,c(95,88,80),(sx-hw+8,rail_y2),(sx+hw-8,rail_y2),2)
    for xi in range(-hw+12,hw-8,12):
        pygame.draw.line(surf,c(80,70,58),(sx+xi,rail_y1-2),(sx+xi,rail_y2+2),2)
    pygame.draw.line(surf,c(180,168,152),(sx-hw+4,sy+hh),(sx+hw-4,sy+hh),2)
    # Windows
    for wx in [bld_left+8,bld_left+24,bld_left+40]:
        for wy in [bld_top+8,bld_top+22]:
            wc=c(255,235,140) if night>0.3 else c(200,218,245)
            pygame.draw.rect(surf,wc,(wx,wy,12,8))
            pygame.draw.rect(surf,c(150,175,215),(wx,wy,12,8),1)

def decor_airport(surf, sx, sy, h, fp=4, night=0.0):
    sx,sy,h=int(sx),int(sy),int(h)
    hw=(TW*fp)//2; hh=(TH*fp)//2; fh=TH*fp
    fill_tile(surf,sx,sy,c(52,52,62),200,TW*fp,TH*fp)
    # Runway
    rw_span=int(hw*0.75)
    for i in range(-4,5):
        pygame.draw.line(surf,c(212,192,55),(sx+i*18,sy+hh-16),(sx+i*18,sy+hh+16),3)
    pygame.draw.line(surf,c(185,178,162),(sx-rw_span,sy+hh-4),(sx+rw_span,sy+hh-4),1)
    pygame.draw.line(surf,c(185,178,162),(sx-rw_span,sy+hh+4),(sx+rw_span,sy+hh+4),1)
    # Terminal
    tw2=54; term_x=sx-76; term_y=sy-h-6
    pygame.draw.rect(surf,c(172,182,205),(term_x,term_y,tw2,h+12))
    pygame.draw.rect(surf,c(192,202,225),(term_x,term_y,tw2,h+12),1)
    for wy in range(term_y+6,term_y+h-4,8):
        for wx in [term_x+6,term_x+18,term_x+30,term_x+42]:
            wc=c(255,235,140) if night>0.3 else c(95,198,255)
            pygame.draw.rect(surf,wc,(wx,wy,7,5))
            pygame.draw.rect(surf,c(55,160,225),(wx,wy,7,5),1)
    f=get_font("Consolas",7,True)
    surf.blit(f.render("TERM",True,c(200,215,235)),(term_x+6,term_y+3))
    # Control tower
    ct_x=sx+40; ct_y=sy-h-38
    pygame.draw.rect(surf,c(135,145,175),(ct_x,ct_y,14,h+40))
    pygame.draw.rect(surf,c(152,162,192),(ct_x-4,ct_y-10,22,10))
    pygame.draw.rect(surf,c(92,195,255),(ct_x-3,ct_y-8,20,8),1)
    # Flashing beacon
    tick=pygame.time.get_ticks()
    bcol=c(255,75,75) if (tick//500)%2==0 else c(80,20,20)
    pygame.draw.circle(surf,bcol,(ct_x+7,ct_y-14),5)
    # Taxiway lights
    for i in range(-4,5):
        lcol=c(52,222,108) if (tick//600+i)%2==0 else c(20,80,40)
        pygame.draw.circle(surf,lcol,(sx+i*18,sy+fh-10),3)
    # Plane
    fnt=get_font("Segoe UI Emoji",26)
    plane=fnt.render("✈",True,c(228,232,248))
    surf.blit(plane,(sx-16,sy+hh-20))

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
        # Pre-render icon font — created ONCE, not per frame
        self._icon_font=get_font("Consolas",14,True)
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
        ic=self._icon_font.render(self.key[:2].upper(),True,self.acc if self.sel else tuple(min(255,v+50) for v in self.acc))
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
    KC={"road":c(65,65,82),"res":c(35,172,82),"com":c(238,108,30),
        "office":c(38,108,215),"ind":c(198,130,28),"garden":c(28,175,68),
        "apark":c(175,50,235),"theatre":c(188,48,158),"hosp":c(198,46,46),
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
            "big"  :get_font("Consolas",22,True),
            "hud"  :get_font("Consolas",13,True),
            "btn"  :get_font("Consolas",11,True),
            "small":get_font("Consolas",10,False),
            "stat" :get_font("Consolas",12,True),
        }
        self.ox=MW//2; self.oy=SH//5+HH
        self.city=city_engine.City("PimpriCity",GRID) if BACKEND else None
        self.grid=[["empty"]*GRID for _ in range(GRID)]
        self.cr=0; self.cc=0
        self.sel=None; self.demo=False; self.hr=-1; self.hc=-1
        self.budget=50000; self.pop=0; self.joy=50; self.turn=1
        self.parts=[]; self.notes=[]; self.tod=0.0
        self.tick=0  # integer frame counter for animations
        self.stars=[(random.randint(0,SW),random.randint(0,HH+200),
                     random.uniform(0.3,1.0)) for _ in range(130)]
        # Pre-render star surface (static positions, only alpha changes)
        self._star_base=pygame.Surface((SW,HH+200),pygame.SRCALPHA)
        for sx2,sy2,sz2 in self.stars:
            r=max(1,int(sz2*2))
            pygame.draw.circle(self._star_base,(255,255,255,255),(sx2,sy2),r)
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
                current=self.grid[r][c2]
                if bn=="empty":
                    self.grid[r][c2]="empty"
                elif current in KEEP_FRONTEND:
                    pass
                elif bn in B2K:
                    self.grid[r][c2]=B2K[bn]

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

    def _night(self):
        """0=day, 1=night, derived from time-of-day."""
        return max(0.0, min(1.0, 1.0 - abs(self.tod - 0.5)*4))

    def draw_bg(self):
        t=(math.sin(self.tod*math.pi)+1)/2
        sky=tuple(int(SKY1[i]+(SKY2[i]-SKY1[i])*t) for i in range(3))
        self.screen.fill(sky)
        # Stars: blit pre-rendered surface at scaled alpha
        sa=int(255*(1-t))
        if sa>10:
            star_s=self._star_base.copy()
            star_s.set_alpha(sa)
            self.screen.blit(star_s,(0,0))
        # Horizon glow at dawn/dusk
        glow_t=1.0-abs((self.tod%1.0)-0.5)*4
        if glow_t>0:
            glow_t=max(0,min(1,glow_t))
            gh=pygame.Surface((MW,60),pygame.SRCALPHA)
            gh.fill((255,140,40,int(55*glow_t)))
            self.screen.blit(gh,(0,HH+10))

    def draw_map(self):
        bldg_list=[]
        night=self._night()
        # Pass 1: ground tiles
        for row in range(self.cr+VP+2,self.cr-3,-1):
            for col in range(self.cc-2,self.cc+VP+4):
                if not(0<=row<GRID and 0<=col<GRID): continue
                sx,sy=t2s(row,col,self.cr,self.cc,self.ox,self.oy)
                sx,sy=int(sx),int(sy)
                if sx<-TW or sx>MW+TW: continue
                if sy<HH-TH or sy>SH+TH*3: continue
                grass=GRA if(row+col)%2==0 else GRB
                # Darken grass at night
                if night>0.1:
                    grass=tuple(int(v*(1-night*0.5)) for v in grass)
                fill_tile(self.screen,sx,sy,grass)
                k=self.grid[row][col]
                if k=="road":
                    fill_tile(self.screen,sx,sy,ROAD_C)
                    # Road centre line dashes
                    for dx in [-18,-9,0,9,18]:
                        pygame.draw.line(self.screen,ROAD_L,(sx+dx,sy+TH//2-2),(sx+dx,sy+TH//2+2),1)
                    # Road edge lines connecting to adjacent tiles
                    for drow,dcol,ex,ey in [(-1,0,sx,sy),(1,0,sx,sy+TH),(0,-1,sx-TW//2,sy+TH//2),(0,1,sx+TW//2,sy+TH//2)]:
                        nr2,nc2=row+drow,col+dcol
                        if 0<=nr2<GRID and 0<=nc2<GRID and self.grid[nr2][nc2]=="road":
                            pygame.draw.line(self.screen,c(62,62,75),(sx,sy+TH//2),(ex,ey),3)
                if k not in("empty","road") and not k.startswith("_"):
                    bldg_list.append((row,col,sx,sy,k))

        # Pass 2: building shadows then buildings back-to-front
        bldg_list.sort(key=lambda x:x[0]+x[1])
        for row,col,sx,sy,key in bldg_list:
            fp2=FP.get(key,1)
            draw_shadow(self.screen,sx,sy,fp2)
        for row,col,sx,sy,key in bldg_list:
            fp2=FP.get(key,1)
            h=BH.get(key,24)
            cols=BC.get(key,(c(82,82,98),c(46,46,60),c(102,102,120)))
            top_c,left_c,right_c=cols
            # Darken buildings at night
            if night>0.1:
                f=1-night*0.35
                top_c=tuple(int(v*f) for v in top_c)
                left_c=tuple(int(v*f) for v in left_c)
                right_c=tuple(int(v*f) for v in right_c)
            draw_box(self.screen,sx,sy,h,top_c,left_c,right_c,fp2)
            fn=DECOR.get(key)
            if fn:
                # Pass night and tick to decor functions that support them
                import inspect
                sig=inspect.signature(fn)
                params=list(sig.parameters.keys())
                kwargs={}
                if "night" in params: kwargs["night"]=night
                if "tick" in params: kwargs["tick"]=self.tick
                fn(self.screen,sx,sy,h,fp2,**kwargs)

        # Pass 3: hover highlight
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
                if fp2>1:
                    for dr in range(fp2):
                        for dc in range(fp2):
                            if dr==0 and dc==0: continue
                            nr,nc=self.hr+dr,self.hc+dc
                            if 0<=nr<GRID and 0<=nc<GRID:
                                fsx,fsy=t2s(nr,nc,self.cr,self.cc,self.ox,self.oy)
                                fill_tile(self.screen,int(fsx),int(fsy),c(32,195,138) if ok else c(215,48,48),52)
                                edge_tile(self.screen,int(fsx),int(fsy),hl,2,130)
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
        # Day/night indicator
        tod_pct=self.tod
        tod_label="☀" if tod_pct<0.5 else "☾"
        tc=c(255,200,45) if tod_pct<0.5 else c(160,180,255)
        self.screen.blit(self.F["small"].render(tod_label,True,tc),(1060,9))

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
        ef=get_font("Consolas",17,True)
        self.screen.blit(ef.render(key[:2].upper(),True,acc),(16,SH-46))
        wtxt(self.screen,name,self.F["hud"],acc,44,SH-46)
        wtxt(self.screen,f"${cost:,}   {fp2}×{fp2} tiles   click grid to place",
             self.F["small"],DIM,44,SH-30,False)

    def run(self):
        while True:
            dt=self.clock.tick(FPS)/1000.0
            self.tod=(self.tod+dt*0.014)%1.0
            self.tick+=1
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