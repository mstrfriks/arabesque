"""Planche « plan habité » A3, RDC + étage, scénario Alex – trait fin, poché noir, annotations manuscrites.
Usage : python3 bowwow.py scenarios.json areas.json out.svg
"""
import json, sys, math

S = json.load(open(sys.argv[1])); AR = json.load(open(sys.argv[2])); OUT = sys.argv[3]
D, W, K = 5.9, 8.2, 20.0  # K : mm par m (1/50)
HAND = "Caveat, 'Architects Daughter', sans-serif"

ST = {
 'rdc': dict(walls=[[0,0,8.2,.21],[7.9,.21,8.2,5.69],[0,5.69,8.2,5.9],[0,.21,.3,5.69]], por=[[2.71,.21,2.91,5.69]],
   fixed=[[.3,2.16,2.71,2.26],[.3,4.13,2.71,4.23]],
   win=[[1.14,0,2.51,.21],[3.05,0,5.09,.21],[5.45,0,7.6,.21],[5.5,5.69,7.88,5.9],[2.92,5.69,5.25,5.9]],
   gaps=[[.95,5.69,1.9,5.9],[2.71,1.16,2.91,1.86],[2.71,4.25,2.91,5.05],[1.75,4.13,2.58,4.23]], sw=[[0,0,0],[1,0,0]]),
 'etage': dict(walls=[[0,0,8.2,.1],[7.96,.1,8.2,5.8],[0,5.8,8.2,5.9],[0,.1,.24,5.8]], por=[[2.71,2.86,2.91,5.8]],
   fixed=[[.24,2.1,2.06,2.17],[1.99,2.17,2.06,3.46]],
   win=[[1.15,0,2.77,.1],[3.01,0,4.64,.1],[5.31,0,7.36,.1],[5.32,5.8,7.6,5.9],[3.22,5.8,5.15,5.9],[0,4.65,.24,5.35],[0,2.86,.24,3.57],[0,1.16,.24,2.11]],
   gaps=[[2.71,3.07,2.91,3.86]], sw=[]),
}
# corrections de calepinage pour la planche (chevauchements de quelques cm du scénario)
NUDGE = {'opt9u2z': dict(x=1.115, w=1.75), 'omanuy5': dict(x=2.63), 'oqau6ix': dict(x=3.905, w=1.29), 'omcl3qq': dict(x=4.08)}

hor = lambda r: (r[2]-r[0]) >= (r[3]-r[1])
esc = lambda s: s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
fr = lambda v: f'{v:.2f}'.replace('.', ',')
out = []; A = out.append

A(f'''<svg xmlns="http://www.w3.org/2000/svg" width="420mm" height="297mm" viewBox="0 0 420 297">
<defs>
<pattern id="parquet" width="2.6" height="12" patternUnits="userSpaceOnUse"><path d="M0 0V12M0 5H2.6" stroke="#c9c3b8" stroke-width=".09"/></pattern>
<pattern id="parquet2" width="12" height="2.6" patternUnits="userSpaceOnUse"><path d="M0 0H12M5 0V2.6" stroke="#c9c3b8" stroke-width=".09"/></pattern>
<pattern id="tiles" width="4" height="4" patternUnits="userSpaceOnUse"><path d="M0 0H4M0 0V4" stroke="#cfcfcf" stroke-width=".09"/></pattern>
<pattern id="stone" width="6" height="6" patternUnits="userSpaceOnUse"><path d="M0 0H6M0 3H6M0 0V3M3 3V6" stroke="#d4cec4" stroke-width=".09"/></pattern>
</defs>
<style>
.w{{fill:#111}}.l{{fill:none;stroke:#111;stroke-width:.18;stroke-linecap:round;stroke-linejoin:round}}.lf{{fill:#fff;stroke:#111;stroke-width:.18;stroke-linejoin:round}}
.t{{fill:none;stroke:#111;stroke-width:.1;stroke-linecap:round}}.g{{fill:none;stroke:#8f8f8f;stroke-width:.1}}.d{{fill:none;stroke:#111;stroke-width:.1;stroke-dasharray:.8 .6}}
.h{{font-family:{HAND};fill:#111}}.lab{{paint-order:stroke;stroke:#fff;stroke-width:1.6px;stroke-linejoin:round}}.ha{{font-family:{HAND};fill:#555}}
.leaf{{fill:#fff;stroke:#111;stroke-width:.12}}
</style><rect width="420" height="297" fill="#fff"/>''')

# ---------------------------------------------------------------- objets (repère local en mm, dos/tête vers le haut)
def r_(x, y, w, h, c='lf', rx=0):
    return f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="{rx}" class="{c}"/>'

def bed(w, l, seed=0):
    s = r_(-w/2, -l/2, w, l, 'lf', .6) + r_(-w/2+.5, -l/2+.5, w-1, l-1, 't', .5)
    n = 2 if w > 24 else 1; pw = (w-1.6-(n-1)*1)/n
    for i in range(n):
        x0 = -w/2+.8+i*(pw+1)
        s += r_(x0, -l/2+1, pw, 6, 'lf', 1.6) + f'<path d="M{x0+1.5:.2f} {-l/2+4:.2f}q{pw/2-1.5:.2f} -1.2 {pw-3:.2f} 0" class="t"/>'
    y0 = -l/2+l*.36
    s += f'<path d="M{-w/2+.5:.2f} {y0:.2f}H{w/2-.5:.2f}M{-w/2+.5:.2f} {y0+2.2:.2f}H{w/2-.5:.2f}" class="t"/>'
    s += f'<path d="M{w/2-.5:.2f} {y0+2.2:.2f}L{w/2-7:.2f} {y0+9:.2f}L{w/2-.5:.2f} {y0+11:.2f}" class="l" style="fill:#fff"/>'
    for k in range(3):
        yy = y0+14+k*7
        if yy < l/2-3: s += f'<path d="M{-w/2+3:.2f} {yy:.2f}q{w/4:.2f} 1.5 {w/2-6:.2f} 0" class="g"/>'
    if seed % 2 == 0 and w > 24:  # livre ouvert
        s += f'<g transform="translate({-w/4:.2f} {y0+16:.2f}) rotate(-12)"><path d="M-3 0L0 .6L3 0V-3.6L0 -3L-3 -3.6Z" class="lf"/><path d="M0 .6V-3" class="t"/></g>'
    return s

def dressing(w, l):
    s = r_(-w/2, -l/2, w, l, 'lf') + f'<path d="M{-w/2:.2f} {l/2-1.2:.2f}H{w/2:.2f}M{-w/2:.2f} {l/2-.6:.2f}H{w/2:.2f}" class="t"/>'
    s += f'<path d="M{-w/2+.8:.2f} {-1:.2f}H{w/2-.8:.2f}" class="t"/>'
    x = -w/2+1.6; k = 0
    while x < w/2-1.2:
        a = 3.6 + (k % 3)*.6
        s += f'<path d="M{x:.2f} {-1-a:.2f}V{-1+a:.2f}" class="t"/>'
        x += 1.4 + (k % 4)*.25; k += 1
    return s

def desk(w, l):
    s = r_(-w/2, -l/2, w, l, 'lf') + r_(-5, -l/2+2, 10, 6.5, 't', .5) + r_(-4.2, -l/2+8.6, 8.4, 1.2, 't', .3)
    s += f'<circle cx="{w/2-4:.2f}" cy="{-l/2+4:.2f}" r="2.4" class="lf"/><circle cx="{w/2-4:.2f}" cy="{-l/2+4:.2f}" r=".6" class="t"/>'
    s += f'<g transform="translate(0 {l/2+5.5:.2f})">' + r_(-4.5, -3.5, 9, 8, 'lf', 2) + r_(-4.5, 3.2, 9, 1.4, 'lf', .7) + '</g>'
    return s

def sofa(w, l):
    s = r_(-w/2, -l/2, w, l, 'lf', 1.5) + r_(-w/2+3, -l/2+.8, w-6, 4.5, 't', 1) + r_(-w/2, -l/2, 3, l, 't', 1.2) + r_(w/2-3, -l/2, 3, l, 't', 1.2)
    n = 3; cw = (w-6)/n
    for i in range(n): s += r_(-w/2+3+i*cw+.3, -l/2+5.6, cw-.6, l-6.4, 't', 1)
    s += f'<g transform="translate({-w/2+7:.2f} {-l/2+3:.2f}) rotate(20)">' + r_(-2.4, -2.4, 4.8, 4.8, 'lf', 1.2) + '</g>'
    return s

def table(w, l, chairs=True):
    s = ''
    if chairs:
        for cx in (-w/4, w/4):
            for sgn in (-1, 1):
                s += f'<g transform="translate({cx:.2f} {sgn*(l/2+3):.2f}) rotate({0 if sgn < 0 else 180})">' + r_(-4, -3.2, 8, 6.4, 'lf', 1.5) + r_(-4, -3.2, 8, 1.3, 'lf', .6) + '</g>'
    s += r_(-w/2, -l/2, w, l, 'lf', .8)
    if chairs:
        for cx in (-w/4, w/4):
            for sgn in (-1, 1): s += f'<circle cx="{cx:.2f}" cy="{sgn*(l/2-4):.2f}" r="2.6" class="t"/><circle cx="{cx:.2f}" cy="{sgn*(l/2-4):.2f}" r="1.7" class="t"/>'
        s += f'<circle cx="0" cy="0" r="2.2" class="t"/><path d="M-1.4 -.8q1.4 -1.6 2.8 0" class="t"/>'
    else:
        s += r_(-w/2+3, -l/2+3, 9, 6.5, 't', .4) + r_(-w/2+4, -l/2+4.2, 9, 6.5, 'lf', .4) + f'<circle cx="{w/2-6:.2f}" cy="0" r="2.4" class="lf"/>'
    return s

def kitchen(w, l):
    s = r_(-w/2, -l/2, w, l, 'lf') + f'<path d="M{-w/2:.2f} {l/2-1.2:.2f}H{w/2:.2f}" class="t"/>'
    for i in range(1, int(w//12)+1): s += f'<path d="M{-w/2+i*12:.2f} {l/2-1.2:.2f}V{l/2:.2f}" class="t"/>'
    if w > 40:
        s += r_(-w/2+6, -l/2+2.5, 7, 7, 't', 1.2) + r_(-w/2+14, -l/2+2.5, 5, 7, 't', 1.2) + f'<path d="M{-w/2+13.5:.2f} {-l/2+.8:.2f}v2.6" class="l"/>'
        for dx, dy, rr in ((0, -2.5, 2.2), (6, -2.5, 1.6), (0, 3, 1.6), (6, 3, 2.2)):
            s += f'<circle cx="{w/2-22+dx:.2f}" cy="{dy:.2f}" r="{rr}" class="t"/><circle cx="{w/2-22+dx:.2f}" cy="{dy:.2f}" r="{rr*.45:.2f}" class="t"/>'
        s += f'<circle cx="{w/2-8:.2f}" cy="-2" r="2" class="lf"/>'
    else:
        s += r_(-4, -l/2+2.5, 8, 7, 't', .6) + f'<circle cx="{w/2-6:.2f}" cy="0" r="1.6" class="lf"/>'
    return s

def commode(w, l):
    s = r_(-w/2, -l/2, w, l, 'lf') + f'<path d="M{-w/2:.2f} {l/2-1:.2f}H{w/2:.2f}" class="t"/>'
    s += f'<circle cx="{-w/4:.2f}" cy="0" r="2" class="lf"/>' + leaves(-w/4, 0, 3.4, 5)
    s += r_(w/8, -2, 5, 3.4, 't', .3)
    return s

def leaves(cx, cy, r, n, rot0=0):
    s = ''
    for i in range(n):
        a = rot0 + i*360/n
        s += f'<ellipse cx="{cx+r*.55*math.cos(math.radians(a)):.2f}" cy="{cy+r*.55*math.sin(math.radians(a)):.2f}" rx="{r*.55:.2f}" ry="{r*.22:.2f}" transform="rotate({a:.1f} {cx+r*.55*math.cos(math.radians(a)):.2f} {cy+r*.55*math.sin(math.radians(a)):.2f})" class="leaf"/>'
    return s

def plant(cx, cy, r=4.5, n=7, rot0=10):
    return f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r*.42:.2f}" class="lf"/>' + leaves(cx, cy, r, n, rot0) + f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r=".5" class="t"/>'

def person(cx, cy, ang=0, scale=1.0, sit=False):
    s = f'<g transform="translate({cx:.2f} {cy:.2f}) rotate({ang}) scale({scale})">'
    s += '<ellipse cx="0" cy="0" rx="4.6" ry="2.3" class="lf"/>'
    s += '<path d="M-4 .6q-1 2.4 .2 3.4M4 .6q1 2.4 -.2 3.4" class="l"/>' if not sit else '<path d="M-3 1.6v3.4M3 1.6v3.4" class="l"/>'
    s += '<circle cx="0" cy="-.3" r="1.9" class="lf"/><path d="M-1.6 -1.2q1.6 -1.6 3.2 0" class="t"/></g>'
    return s

OBJ = {'bed': bed, 'dr': dressing, 'bureau': desk, 'canape': sofa, 'table': table, 'cuisine': kitchen, 'commode': commode}

# ---------------------------------------------------------------- un niveau
def level(lv, ox, oy):
    st = ST[lv]; sc = next(s for s in S[lv] if s['name'] == 'Alex')
    X = lambda x: ox + x*K; Y = lambda y: oy + (D-y)*K
    R = lambda r, c, extra='': A(f'<rect x="{X(r[0]):.2f}" y="{Y(r[3]):.2f}" width="{(r[2]-r[0])*K:.2f}" height="{(r[3]-r[1])*K:.2f}" class="{c}" {extra}/>')
    # sols
    if lv == 'rdc':
        R([2.91, .21, 7.9, 5.69], '', 'fill="url(#parquet)"'); R([.3, .21, 2.71, 2.16], '', 'fill="url(#tiles)"'); R([.3, 4.23, 2.71, 5.69], '', 'fill="url(#stone)"')
    else:
        R([.24, .1, 2.71, 2.065], '', 'fill="url(#parquet2)"'); R([2.91, .1, 4.59, 2.79], '', 'fill="url(#parquet2)"')
        R([2.91, .1, 7.96, 5.8], '', 'fill="url(#parquet)" opacity=".55"'); R([.24, 4.17, 2.71, 5.8], '', 'fill="url(#tiles)"')
    # tapis
    if lv == 'rdc':
        A(f'<g>{r_(X(5.55), Y(2.95), 2.1*K, 1.55*K, "lf", .4)}{r_(X(5.55)+1.2, Y(2.95)+1.2, 2.1*K-2.4, 1.55*K-2.4, "t", .4)}</g>')
        for i in range(10): A(f'<path d="M{X(5.55)+2+i*4:.2f} {Y(1.4)-.2:.2f}v1.2M{X(5.55)+2+i*4:.2f} {Y(2.95):.2f}v-1.2" class="t"/>')
    else:
        A(r_(X(4.6), Y(5.35), 2.0*K, 1.25*K, 'lf', .4)); A(f'<path d="M{X(4.6)+3:.2f} {Y(5.35)+3:.2f}h{2.0*K-6:.2f}v{1.25*K-6:.2f}h{-(2.0*K-6):.2f}z" class="d"/>')
    # escalier / trémie
    cx, cy, rr = 1.145, 3.115, .8
    if lv == 'rdc':
        A(f'<circle cx="{X(cx):.2f}" cy="{Y(cy):.2f}" r="{rr*K:.2f}" class="lf"/><circle cx="{X(cx):.2f}" cy="{Y(cy):.2f}" r="{.08*K:.2f}" class="lf"/>')
        for i in range(14):
            a = math.radians(-90 + i*360/14)
            A(f'<path d="M{X(cx)+.08*K*math.cos(a):.2f} {Y(cy)-.08*K*math.sin(a):.2f}L{X(cx)+rr*K*math.cos(a):.2f} {Y(cy)-rr*K*math.sin(a):.2f}" class="l"/>')
        A(f'<path d="M{X(cx)+.52*K:.2f} {Y(cy):.2f}A{.52*K:.2f} {.52*K:.2f} 0 1 0 {X(cx):.2f} {Y(cy)+.52*K:.2f}" class="t"/><path d="M{X(cx)-1.2:.2f} {Y(cy)+.52*K-1.1:.2f}L{X(cx):.2f} {Y(cy)+.52*K:.2f}L{X(cx)-1.2:.2f} {Y(cy)+.52*K+1.1:.2f}" class="t"/>')
    else:
        A(f'<circle cx="{X(cx):.2f}" cy="{Y(cy):.2f}" r="{rr*K:.2f}" class="t"/><circle cx="{X(cx):.2f}" cy="{Y(cy):.2f}" r="{.08*K:.2f}" class="lf"/>')
        for i in range(10, 14):
            a = math.radians(-90 + i*360/14)
            A(f'<path d="M{X(cx)+.08*K*math.cos(a):.2f} {Y(cy)-.08*K*math.sin(a):.2f}L{X(cx)+rr*K*math.cos(a):.2f} {Y(cy)-rr*K*math.sin(a):.2f}" class="l"/>')
        A(f'<path d="M{X(cx)-rr*K*.7:.2f} {Y(cy)-rr*K*.7:.2f}L{X(cx)+rr*K*.7:.2f} {Y(cy)+rr*K*.7:.2f}" class="g"/>')
    # sanitaires
    def tub(x0, y0, x1, y1):
        A(r_(X(x0), Y(y1), (x1-x0)*K, (y1-y0)*K, 'lf', 1.5)); A(r_(X(x0)+1.4, Y(y1)+1.4, (x1-x0)*K-2.8, (y1-y0)*K-2.8, 't', 4))
        A(f'<circle cx="{X((x0+x1)/2):.2f}" cy="{Y(y0)-4:.2f}" r=".8" class="t"/>')
    def basin(cx, cy, rot):
        A(f'<g transform="translate({X(cx):.2f} {Y(cy):.2f}) rotate({rot})">{r_(-6, -2.5, 12, 5.5, "lf", .6)}<ellipse cx="0" cy=".6" rx="4" ry="2.1" class="t"/><path d="M0 -2.5v1.4" class="l"/></g>')
    def wc(cx, cy, rot):
        A(f'<g transform="translate({X(cx):.2f} {Y(cy):.2f}) rotate({rot})">{r_(-4, -6, 8, 3.6, "lf", .5)}<ellipse cx="0" cy="1.6" rx="3.6" ry="4.8" class="lf"/><ellipse cx="0" cy="2.2" rx="2.3" ry="3.4" class="t"/></g>')
    if lv == 'rdc':
        tub(.32, .25, 1.02, 1.95); basin(2.38, 1.92, 0); wc(2.4, .55, 180)
        A(f'<path d="M{X(.3):.2f} {Y(4.95):.2f}h{1.3*K:.2f}" class="l"/>')
        for i in range(6): A(f'<circle cx="{X(.42+i*.22):.2f}" cy="{Y(4.95)+1.1:.2f}" r=".5" class="t"/>')
        A(f'<path d="M{X(.4):.2f} {Y(4.95)+2.2:.2f}q1 3 2.5 3.2" class="t"/><path d="M{X(.85):.2f} {Y(4.95)+2.2:.2f}q-.6 3.6 1.2 4.4" class="t"/>')
        A(r_(X(.33), Y(4.85), .38*K, .58*K, 'lf', .3))
    else:
        tub(.27, 4.22, .97, 5.77); basin(1.65, 5.55, 180); wc(2.42, 5.42, 180)
    # mobilier du scénario
    for o in sc.get('beds', []):
        o = dict(o, **NUDGE.get(o['id'], {}))
        f = OBJ.get(o['k'] if o['k'] != 'box' else o['p'])
        if not f: continue
        w, l = o['w']*K, o['l']*K
        body = f(w, l) if o['k'] != 'bed' else bed(w, l, hash(o['id']) % 3)
        if o['p'] == 'table' and o['rot'] == 0 and lv == 'etage': body = table(w, l, chairs=False)
        A(f'<g transform="translate({X(o["x"]):.2f} {Y(o["y"]):.2f}) rotate({90*o["rot"]})">{body}</g>')
    # tables de nuit
    if lv == 'rdc':
        for cx in (5.45, 7.75): A(r_(X(cx)-4, Y(2.95), 8, 8, 'lf', .5) + f'<circle cx="{X(cx):.2f}" cy="{Y(2.95)+4:.2f}" r="2.4" class="t"/><circle cx="{X(cx):.2f}" cy="{Y(2.95)+4:.2f}" r=".7" class="t"/>')
        A(r_(X(6.6), Y(5.67), 8, 8, 'lf', .5) + f'<circle cx="{X(6.6)+4:.2f}" cy="{Y(5.67)+4:.2f}" r="2.4" class="t"/>')
    # murs
    for r in st['walls'] + st['por'] + st['fixed'] + [w['r'] for w in sc['walls']]: R(r, 'w')
    for g in st['win']:
        R(g, '', 'fill="#fff"'); Hh = g[2]-g[0] > g[3]-g[1]
        if Hh:
            for f in (g[1], g[3], (g[1]+g[3])/2): A(f'<path d="M{X(g[0]):.2f} {Y(f):.2f}H{X(g[2]):.2f}" class="t"/>')
        else:
            for f in (g[0], g[2], (g[0]+g[2])/2): A(f'<path d="M{X(f):.2f} {Y(g[1]):.2f}V{Y(g[3]):.2f}" class="t"/>')
    def door(r, c, wd, h, s, cut=True):
        Hh = hor(r); a, b = c-wd/2, c+wd/2
        if cut: R([a, r[1], b, r[3]] if Hh else [r[0], a, r[2], b], '', 'fill="#fff"')
        if Hh:
            hx, ox_ = (b, a) if h else (a, b); yy = r[3] if s else r[1]; ly = yy+(1 if s else -1)*wd
            A(f'<path d="M{X(hx):.2f} {Y(yy):.2f}V{Y(ly):.2f}" class="l"/><path d="M{X(hx):.2f} {Y(ly):.2f}A{wd*K:.2f} {wd*K:.2f} 0 0 {1 if h ^ s else 0} {X(ox_):.2f} {Y(yy):.2f}" class="t"/>')
        else:
            hy, oy_ = (b, a) if h else (a, b); xx = r[2] if s else r[0]; lx = xx+(1 if s else -1)*wd
            A(f'<path d="M{X(xx):.2f} {Y(hy):.2f}H{X(lx):.2f}" class="l"/><path d="M{X(lx):.2f} {Y(hy):.2f}A{wd*K:.2f} {wd*K:.2f} 0 0 {0 if h ^ s else 1} {X(xx):.2f} {Y(oy_):.2f}" class="t"/>')
    for g in st['gaps']: R(g, '', 'fill="#fff"')
    for i, h, s in st['sw']:
        g = st['gaps'][i]; Hh = g[2]-g[0] > g[3]-g[1]
        door(g, (g[0]+g[2])/2 if Hh else (g[1]+g[3])/2, (g[2]-g[0]) if Hh else (g[3]-g[1]), h, s, cut=False)
    for d in sc['doors']:
        w = next(x for x in sc['walls'] if x['id'] == d['wall']); door(w['r'], d['c'], d['w'], d['h'], d['s'])
    # pièces
    ar = AR.get(lv, {})
    for l in sc['labels']:
        a = ar.get(l['id'])
        A(f'<text x="{X(l["x"]):.2f}" y="{Y(l["y"]):.2f}" class="h lab" font-size="5.2" text-anchor="middle">{esc(l["t"])}</text>')
        if a: A(f'<text x="{X(l["x"]):.2f}" y="{Y(l["y"])+4.2:.2f}" class="ha lab" font-size="3.8" text-anchor="middle">{fr(a)} m²</text>')
    for (lx, ly, t, a) in ar.get('_extra', []):
        A(f'<text x="{X(lx):.2f}" y="{Y(ly):.2f}" class="h lab" font-size="4.6" text-anchor="middle">{esc(t)}</text>')
    return X, Y

def note(x, y, tx, ty, txt, anchor='start', size=4.2):
    ex = tx - 1.8 if anchor == 'start' else tx + 1.8
    ey = ty - size*.35
    A(f'<path d="M{x:.2f} {y:.2f}C{x:.2f} {(y+ey)/2:.2f} {ex:.2f} {(y+ey)/2:.2f} {ex:.2f} {ey:.2f}" class="t"/><circle cx="{x:.2f}" cy="{y:.2f}" r=".5" fill="#111"/>')
    for i, line in enumerate(txt.split('\n')):
        A(f'<text x="{tx:.2f}" y="{ty+i*size*1.05:.2f}" class="h" font-size="{size}" text-anchor="{anchor}">{esc(line)}</text>')

OXR, OXE, OY = 30, 232, 66
XR, YR = level('rdc', OXR, OY)
XE, YE = level('etage', OXE, OY)

# habitants et plantes
A(plant(XR(7.62), YR(.55), 5)); A(plant(XR(.62), YR(5.42), 3.6, 6))

A(plant(XE(7.6), YE(3.55), 6, 8)); A(plant(XE(3.1), YE(5.5), 4.4, 7, 30)); A(plant(XE(5.0), YE(3.3), 3.6, 6))

# annotations manuscrites
note(XR(4.05), YR(4.9), XR(3.6), YR(6.55), 'un dressing de 3,55 m\nqui longe tout le couloir')
note(XR(6.7), YR(5.75), XR(6.3), YR(6.55), 'lumière du matin, côté rue')
note(XR(2.81), YR(4.65), XR(.35), YR(6.55), 'le sas s\'ouvre en grand\nsur le couloir et l\'escalier')
note(XR(7.0), YR(.9), XR(5.4), YR(-.75), 'option : remonter le plancher, la marche\nentre le sas et les chambres disparaît')
note(XR(.7), YR(1.1), XR(.35), YR(-.75), 'SDB partagée,\naccès par le couloir')
note(XE(2.4), YE(.6), XE(1.6), YE(-.75), 'un coin bureau sous la fenêtre')
note(XE(.12), YE(5.0), XE(.35), YE(6.55), 'fenêtre conservée dans la SDB')
note(XE(6.05), YE(.4), XE(5.4), YE(-.75), 'cuisine en L, la table\nau soleil de l\'après-midi')
note(XE(7.6), YE(3.55), XE(6.0), YE(6.55), 'un coin vert près des fenêtres')

# titres
for ox, t in ((OXR, 'rez-de-chaussée'), (OXE, 'étage')):
    A(f'<text x="{ox+82:.2f}" y="{OY+D*K+27:.2f}" class="h" font-size="8" text-anchor="middle">{t}</text>')
# carnet
pts = ['deux chambres de plus de 9 m² au rez-de-chaussée, chacune avec sa fenêtre',
       'cinq dressings, un peu plus de 10 mètres de rangement',
       'les murs porteurs et les façades ne bougent pas',
       'à l\'étage, la chambre se ferme sur le palier',
       'en option : un seul niveau de sol au rez-de-chaussée']
A('<text x="232" y="232" class="h" font-size="6">ce qui change</text>')
for i, t in enumerate(pts): A(f'<text x="232" y="{240+i*6.2:.1f}" class="h" font-size="4.6">– {esc(t)}</text>')
A('<text x="30" y="20" dy="0" class="ha" font-size="4" text-anchor="start"> </text>')
# échelle graphique
sx, sy = 30, 272
for i in range(4):
    A(f'<rect x="{sx+i*K:.2f}" y="{sy}" width="{K}" height="1.6" fill="{"#111" if i % 2 == 0 else "#fff"}" stroke="#111" stroke-width=".15"/>')
    A(f'<text x="{sx+i*K:.2f}" y="{sy+6}" class="ha" font-size="3.4" text-anchor="middle">{i}</text>')
A(f'<text x="{sx+4*K:.2f}" y="{sy+6}" class="ha" font-size="3.4" text-anchor="middle">4 m</text>')
A(f'<text x="420" y="285" dx="-20" class="ha" font-size="3.6" text-anchor="end">Mobilier indicatif – cotes à vérifier sur site</text>')
A('</svg>')
open(OUT, 'w').write('\n'.join(out))
