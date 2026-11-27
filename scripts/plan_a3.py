"""Plans A3 au 1/50 (RDC + étage) : page 1 cloisonnement, page 2 électricité / VMC / points d'eau.
Usage : python3 plan_a3.py scenarios.json areas.json out_dir
"""
import json, sys, os

S = json.load(open(sys.argv[1]))
AREAS = json.load(open(sys.argv[2]))
OUTD = sys.argv[3]
D, W, SC = 5.9, 8.2, 20.0  # SC : mm papier par m (1/50)

ST = {
 'rdc': dict(h=2.6, walls=[[0,0,8.2,.21],[7.9,.21,8.2,5.69],[0,5.69,8.2,5.9],[0,.21,.3,5.69]], por=[[2.71,.21,2.91,5.69]],
   fixed=[[.3,2.16,2.71,2.26],[.3,4.13,2.71,4.23]],
   win=[[1.14,0,2.51,.21],[3.05,0,5.09,.21],[5.45,0,7.6,.21],[5.5,5.69,7.88,5.9],[2.92,5.69,5.25,5.9]],
   gaps=[[.95,5.69,1.9,5.9],[2.71,1.16,2.91,1.86],[2.71,4.25,2.91,5.05],[1.75,4.13,2.58,4.23]],
   sw=[[0,0,0],[1,0,0]], swd=[[2,1,0,'porte sas / couloir (mur porteur)'],[3,0,0,'porte sas / escalier']],
   stair=[.3,2.26,1.99,3.97], beam=None, inner=[.3,.21,7.9,5.69], opt=[2.91,.21,7.9,5.69]),
 'etage': dict(h=2.5, walls=[[0,0,8.2,.1],[7.96,.1,8.2,5.8],[0,5.8,8.2,5.9],[0,.1,.24,5.8]], por=[[2.71,2.86,2.91,5.8]],
   fixed=[[.24,2.1,2.06,2.17],[1.99,2.17,2.06,3.46]],
   win=[[1.15,0,2.77,.1],[3.01,0,4.64,.1],[5.31,0,7.36,.1],[5.32,5.8,7.6,5.9],[3.22,5.8,5.15,5.9],[0,4.65,.24,5.35],[0,2.86,.24,3.57],[0,1.16,.24,2.11]],
   gaps=[[2.71,3.07,2.91,3.86]], sw=[], swd=[], stair=[.24,2.17,1.99,3.97], beam=[2.71,.1,2.91,2.86], inner=[.24,.1,7.96,5.8], opt=None),
}

# Électricité / VMC / eau : [type, x, y]
# pc, pl, int, vv, ext_ex (bouche existante), ea (entrée d'air), eau (point d'eau conservé), eau_x (à neutraliser)
ELEC = {
 'rdc': [
  ['int', 4.52, 5.55], ['pl', 6.75, 3.95], ['pc', 6.9, 5.62], ['pc', 7.83, 3.4], ['pc', 5.6, 3.15], ['ea', 6.7, 5.79],
  ['int', 3.85, 1.04], ['pl', 6.4, 1.55], ['pc', 5.55, 2.93], ['pc', 7.65, 2.93], ['pc', 4.6, .28], ['ea', 6.5, .1],
  ['vv', 2.98, 4.05], ['vv', 2.98, 1.95], ['pl', 3.3, 3.75], ['pc', 2.98, 2.6],
  ['ext_ex', 1.25, 1.95],
  ['eau', .65, 1.2], ['eau', 2.35, 1.95], ['eau', 2.35, .45], ['eau_x', 3.65, .42],
 ],
 'etage': [
  ['int', 2.95, 1.98], ['pl', 2.3, 1.05], ['pc', .31, 1.5], ['pc', 3.6, 2.72], ['pc', 4.52, 2.72], ['ea', 1.9, .05],
  ['pl', 2.45, 3.25],
  ['ext_ex', 1.0, 5.55], ['ext_ex', 7.45, .45],
  ['eau', .6, 4.45], ['eau', 1.6, 5.6], ['eau', 2.4, 5.45], ['eau', 6.4, .45],
 ],
}
LINKS = {'rdc': [[0, 1], [6, 7], [12, 14], [13, 14]], 'etage': [[0, 1]]}

hor = lambda r: (r[2]-r[0]) >= (r[3]-r[1])
wkey = lambda w: ','.join('%.2f' % v for v in w['r'])
clip = lambda r, b: [max(r[0], b[0]), max(r[1], b[1]), min(r[2], b[2]), min(r[3], b[3])]
esc = lambda s: s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
fr = lambda v: f'{v:.2f}'.replace('.', ',')

HEAD = '''<svg xmlns="http://www.w3.org/2000/svg" width="420mm" height="297mm" viewBox="0 0 420 297" font-family="DejaVu Sans, Arial, sans-serif">
<defs><pattern id="hn" width="1.2" height="1.2" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="1.2" height="1.2" fill="#dbe6ff"/><line x1="0" y1="0" x2="0" y2="1.2" stroke="#1240e0" stroke-width="0.22"/></pattern>
<pattern id="hd" width="1.2" height="1.2" patternUnits="userSpaceOnUse" patternTransform="rotate(-45)"><rect width="1.2" height="1.2" fill="#ffe1dc"/><line x1="0" y1="0" x2="0" y2="1.2" stroke="#d02f1c" stroke-width="0.18"/></pattern></defs>
<style>
.ex{fill:#9a9a9a;stroke:#000;stroke-width:.25}.por{fill:#4d4d4d;stroke:#000;stroke-width:.25}
.neuf{fill:url(#hn);stroke:#1240e0;stroke-width:.45}.demo{fill:url(#hd);stroke:#d02f1c;stroke-width:.3;stroke-dasharray:1.2 .8}
.demol{stroke:#d02f1c;stroke-width:.3;fill:none;stroke-dasharray:1 .7}.opt{fill:none;stroke:#7a3fb5;stroke-width:.35;stroke-dasharray:3 1 .6 1}
.trait{stroke:#000;stroke-width:.35;fill:none}.fin{stroke:#000;stroke-width:.13;fill:none}.cache{stroke:#000;stroke-width:.18;stroke-dasharray:1.5 1;fill:none}
.cote{stroke:#000;stroke-width:.13}.mob{fill:none;stroke:#8c8c8c;stroke-width:.13;stroke-dasharray:.8 .6}
.agt{fill:#f6efe2;stroke:#000;stroke-width:.3}.agl{stroke:#7a6a52;stroke-width:.13}
.el{stroke:#d96a00;stroke-width:.3;fill:#fff}.elf{fill:#d96a00}.elw{stroke:#d96a00;stroke-width:.2;fill:none;stroke-dasharray:1 .6}
.vm{stroke:#0a8a6a;stroke-width:.3;fill:#fff}.eau{stroke:#1f6fd1;stroke-width:.3;fill:#fff}.eauf{fill:#1f6fd1}.x{stroke:#d02f1c;stroke-width:.45}
.t2{font-size:2.5px}.t3{font-size:3px}.t4{font-size:4.2px}.b{font-weight:bold}
</style><rect width="420" height="297" fill="#fff"/>'''


def symbol(A, t, cx, cy):
    if t == 'pl':
        A(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="1.7" class="el"/><path d="M{cx-1.2:.2f} {cy-1.2:.2f}L{cx+1.2:.2f} {cy+1.2:.2f}M{cx-1.2:.2f} {cy+1.2:.2f}L{cx+1.2:.2f} {cy-1.2:.2f}" class="el"/>')
    elif t == 'pc':
        A(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="1.3" class="el"/><path d="M{cx-1.3:.2f} {cy:.2f}H{cx+1.3:.2f}" class="el"/><circle cx="{cx:.2f}" cy="{cy-.5:.2f}" r=".35" class="elf"/>')
    elif t in ('int', 'vv'):
        A(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r=".9" class="el"/><path d="M{cx+.6:.2f} {cy-.6:.2f}L{cx+2:.2f} {cy-2:.2f}" class="el"/>')
        if t == 'vv': A(f'<path d="M{cx-.6:.2f} {cy+.6:.2f}L{cx-2:.2f} {cy+2:.2f}" class="el"/>')
    elif t == 'ext_ex':
        A(f'<rect x="{cx-1.6:.2f}" y="{cy-1.6:.2f}" width="3.2" height="3.2" class="vm" stroke-dasharray=".8 .5"/><text x="{cx:.2f}" y="{cy+.9:.2f}" class="t2 b" text-anchor="middle" style="fill:#0a8a6a">E</text>')
    elif t == 'ea':
        A(f'<rect x="{cx-2.2:.2f}" y="{cy-.7:.2f}" width="4.4" height="1.4" class="vm"/><path d="M{cx:.2f} {cy-.7:.2f}V{cy+.7:.2f}" class="vm"/>')
    elif t in ('eau', 'eau_x'):
        A(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="1.5" class="eau"/><circle cx="{cx:.2f}" cy="{cy:.2f}" r=".6" class="eauf"/>')
        if t == 'eau_x': A(f'<path d="M{cx-2:.2f} {cy-2:.2f}L{cx+2:.2f} {cy+2:.2f}M{cx-2:.2f} {cy+2:.2f}L{cx+2:.2f} {cy-2:.2f}" class="x"/>')


def page(mode):
    svg = []; A = svg.append
    A(HEAD)

    def chain(X, Y, pts, axis, off):
        pts = sorted(set(round(p, 3) for p in pts))
        if axis == 'x':
            yy = Y(0) + off if off > 0 else Y(D) + off
            A(f'<line x1="{X(pts[0]):.2f}" y1="{yy:.2f}" x2="{X(pts[-1]):.2f}" y2="{yy:.2f}" class="cote"/>')
            for p in pts:
                A(f'<line x1="{X(p):.2f}" y1="{yy-1.2:.2f}" x2="{X(p):.2f}" y2="{yy+1.2:.2f}" class="cote"/><line x1="{X(p)-.9:.2f}" y1="{yy+.9:.2f}" x2="{X(p)+.9:.2f}" y2="{yy-.9:.2f}" class="trait"/>')
            for a, b in zip(pts, pts[1:]):
                A(f'<text x="{X((a+b)/2):.2f}" y="{yy-(4.2 if (b-a)*SC < 6 else 1):.2f}" class="t2" text-anchor="middle">{round((b-a)*1000)}</text>')
        else:
            xx = X(W) + off if off > 0 else X(0) + off
            A(f'<line x1="{xx:.2f}" y1="{Y(pts[0]):.2f}" x2="{xx:.2f}" y2="{Y(pts[-1]):.2f}" class="cote"/>')
            for p in pts:
                A(f'<line x1="{xx-1.2:.2f}" y1="{Y(p):.2f}" x2="{xx+1.2:.2f}" y2="{Y(p):.2f}" class="cote"/><line x1="{xx-.9:.2f}" y1="{Y(p)+.9:.2f}" x2="{xx+.9:.2f}" y2="{Y(p)-.9:.2f}" class="trait"/>')
            for i, (a, b) in enumerate(zip(pts, pts[1:])):
                small = (b-a)*SC < 6
                tx = xx + (1.6 if off > 0 else -1.6) + ((5 if off > 0 else -5) if small and i % 2 else 0)
                A(f'<text x="{tx:.2f}" y="{Y((a+b)/2)+1:.2f}" class="t2" text-anchor="{"start" if off > 0 else "end"}">{round((b-a)*1000)}</text>')

    def plan(lv, ox, oy, chains):
        st = ST[lv]; ref = S[lv][0]; sc = next(s for s in S[lv] if s['name'] == 'Alex')
        X = lambda x: ox + x*SC
        Y = lambda y: oy + (D - y)*SC
        reps = []
        def rect(r, **kw):
            a = ' '.join(f'{k.rstrip("_").replace("_","-")}="{v}"' for k, v in kw.items())
            A(f'<rect x="{X(r[0]):.2f}" y="{Y(r[3]):.2f}" width="{(r[2]-r[0])*SC:.2f}" height="{(r[3]-r[1])*SC:.2f}" {a}/>')
        def line(a, b, c, d, cls):
            A(f'<line x1="{X(a):.2f}" y1="{Y(b):.2f}" x2="{X(c):.2f}" y2="{Y(d):.2f}" class="{cls}"/>')
        def bubble(x, y, txt, col='#000'):
            A(f'<circle cx="{X(x):.2f}" cy="{Y(y):.2f}" r="3.3" fill="#fff" stroke="{col}" stroke-width=".28"/><text x="{X(x):.2f}" y="{Y(y)+.8:.2f}" class="t2 b" style="font-size:2.3px" text-anchor="middle">{txt}</text>')
        pre = 'R' if lv == 'rdc' else 'E'
        s0 = st['stair']; rect(s0, fill='none', class_='fin')
        if lv == 'rdc':
            for i in range(1, 10):
                y = s0[1] + (s0[3]-s0[1])*i/10; line(s0[0], y, s0[2], y, 'fin')
        else:
            line(s0[0], s0[1], s0[2], s0[3], 'fin'); line(s0[0], s0[3], s0[2], s0[1], 'fin')
            A(f'<text x="{X((s0[0]+s0[2])/2):.2f}" y="{Y((s0[1]+s0[3])/2)-1.5:.2f}" class="t2" text-anchor="middle" fill="#fff" stroke="#fff" stroke-width="1.2">Trémie</text>')
            A(f'<text x="{X((s0[0]+s0[2])/2):.2f}" y="{Y((s0[1]+s0[3])/2)-1.5:.2f}" class="t2" text-anchor="middle">Trémie</text>')
        na = 0; dress = []
        for o in sc.get('beds', []):
            a_ = o['l'] if o['rot'] % 2 else o['w']; c_ = o['w'] if o['rot'] % 2 else o['l']
            r = [o['x']-a_/2, o['y']-c_/2, o['x']+a_/2, o['y']+c_/2]
            if o.get('k') == 'dr':
                na += 1
                rect(r, class_='agt')
                if o['rot'] % 2:
                    xm = (r[0]+r[2])/2; line(xm, r[1]+.05, xm, r[3]-.05, 'agl')
                else:
                    ym = (r[1]+r[3])/2; line(r[0]+.05, ym, r[2]-.05, ym, 'agl')
                dress.append((o, f'{pre}A{na}'))
                reps.append(dict(rep=f'{pre}A{na}', kind='dressing', L=round(o['w'], 2), p=round(o['l'], 2)))
            else:
                rect(r, class_='mob')
        for r in st['walls']: rect(r, class_='ex')
        for r in st['por']: rect(r, class_='por')
        if st['beam']:
            b = st['beam']; line(b[0], b[1], b[0], b[3], 'cache'); line(b[2], b[1], b[2], b[3], 'cache')
        for r in st['fixed']: rect(r, class_='ex')
        sk = {wkey(w) for w in sc['walls']}; rk = {wkey(w) for w in ref['walls']}
        if mode == 'trav':
            for w in ref['walls']:
                if wkey(w) not in sk: rect(clip(w['r'], st['inner']), class_='demo')
        for w in sc['walls']:
            rect(clip(w['r'], st['inner']), class_='neuf' if (wkey(w) not in rk and mode == 'trav') else 'ex')
        for g in st['win']:
            rect(g, fill='#fff', stroke='none')
            if g[2]-g[0] > g[3]-g[1]:
                for f in (g[1], g[3], (g[1]+g[3])/2): line(g[0], f, g[2], f, 'fin')
                line(g[0], g[1], g[0], g[3], 'trait'); line(g[2], g[1], g[2], g[3], 'trait')
            else:
                for f in (g[0], g[2], (g[0]+g[2])/2): line(f, g[1], f, g[3], 'fin')
                line(g[0], g[1], g[2], g[1], 'trait'); line(g[0], g[3], g[2], g[3], 'trait')
        def door(r, c, wd, h, s, cut=True, cls=('trait', 'fin')):
            Hh = hor(r); a, b = c-wd/2, c+wd/2
            gap = [a, r[1], b, r[3]] if Hh else [r[0], a, r[2], b]
            if cut:
                rect(gap, fill='#fff', stroke='none')
                if Hh: line(a, r[1], a, r[3], 'trait'); line(b, r[1], b, r[3], 'trait')
                else: line(r[0], a, r[2], a, 'trait'); line(r[0], b, r[2], b, 'trait')
            if Hh:
                hx, ox_ = (b, a) if h else (a, b); yy = r[3] if s else r[1]; ly = yy + (1 if s else -1)*wd
                line(hx, yy, hx, ly, cls[0]); sweep = 1 if (h ^ s) else 0
                A(f'<path d="M{X(hx):.2f} {Y(ly):.2f} A{wd*SC:.2f} {wd*SC:.2f} 0 0 {sweep} {X(ox_):.2f} {Y(yy):.2f}" class="{cls[1]}"/>')
            else:
                hy, oy_ = (b, a) if h else (a, b); xx = r[2] if s else r[0]; lx = xx + (1 if s else -1)*wd
                line(xx, hy, lx, hy, cls[0]); sweep = 0 if (h ^ s) else 1
                A(f'<path d="M{X(lx):.2f} {Y(hy):.2f} A{wd*SC:.2f} {wd*SC:.2f} 0 0 {sweep} {X(xx):.2f} {Y(oy_):.2f}" class="{cls[1]}"/>')
        for g in st['gaps']: rect(g, fill='#fff', stroke='none')
        for i, h, s in st['sw']:
            g = st['gaps'][i]; Hh = g[2]-g[0] > g[3]-g[1]
            door(g, (g[0]+g[2])/2 if Hh else (g[1]+g[3])/2, (g[2]-g[0]) if Hh else (g[3]-g[1]), h, s, cut=False)
        if mode == 'trav':
            for i, h, s, nm in st['swd']:
                g = st['gaps'][i]; Hh = g[2]-g[0] > g[3]-g[1]
                door(g, (g[0]+g[2])/2 if Hh else (g[1]+g[3])/2, (g[2]-g[0]) if Hh else (g[3]-g[1]), h, s, cut=False, cls=('demol', 'demol'))
        for d in sc['doors']:
            w = next(x for x in sc['walls'] if x['id'] == d['wall'])
            door(w['r'], d['c'], d['w'], d['h'], d['s'])
        ar = AREAS.get(lv, {})
        for l in sc['labels']:
            x, y = X(l['x']), Y(l['y'])
            A(f'<text x="{x:.2f}" y="{y:.2f}" class="t3 b" text-anchor="middle">{esc(l["t"])}</text>')
            if ar.get(l['id']): A(f'<text x="{x:.2f}" y="{y+3.6:.2f}" class="t2" text-anchor="middle">{fr(ar[l["id"]])} m²</text>')
        for (lx, ly, t, a) in ar.get('_extra', []):
            A(f'<text x="{X(lx):.2f}" y="{Y(ly):.2f}" class="t3 b" text-anchor="middle">{esc(t)}</text>')
            if a: A(f'<text x="{X(lx):.2f}" y="{Y(ly)+3.6:.2f}" class="t2" text-anchor="middle">{fr(a)} m²</text>')
        if mode == 'trav':
            for o, rp in dress: bubble(o['x'], o['y'], rp, '#7a6a52')
            n = 0
            for w in sc['walls']:
                if wkey(w) in rk: continue
                n += 1; r = clip(w['r'], st['inner']); Hh = hor(r)
                L = (r[2]-r[0]) if Hh else (r[3]-r[1]); ep = min(r[2]-r[0], r[3]-r[1])
                ds = [d for d in sc['doors'] if d['wall'] == w['id']]
                cands = [(r[0]+(r[2]-r[0])*f, (r[1]+r[3])/2) if Hh else ((r[0]+r[2])/2, r[1]+(r[3]-r[1])*f) for f in (.5, .3, .7, .15, .85)]
                pt = next((c for c in cands if all(abs((c[0] if Hh else c[1])-d['c']) > d['w']/2+.2 for d in ds)), cands[0])
                bubble(*pt, f'{pre}C{n}', '#1240e0')
                reps.append(dict(rep=f'{pre}C{n}', kind='cloison', ep=round(ep, 3), L=round(L, 2), h=st['h'], surf=round(L*st['h']-sum(d['w']*2.04 for d in ds), 2)))
            rkd = {(wkey(next(x for x in ref['walls'] if x['id'] == d['wall'])), round(d['c'], 2), d['w']) for d in ref['doors']}
            n = 0
            for d in sc['doors']:
                w = next(x for x in sc['walls'] if x['id'] == d['wall'])
                if (wkey(w), round(d['c'], 2), d['w']) in rkd: continue
                n += 1; r = w['r']; o = .42*(1 if d['s'] else -1)
                x, y = ((d['c'], (r[3] if d['s'] else r[1]) + o) if hor(r) else ((r[2] if d['s'] else r[0]) + o, d['c']))
                bubble(x, y, f'{pre}P{n}')
                reps.append(dict(rep=f'{pre}P{n}', kind='porte', w=d['w']))
            n = 0
            for w in ref['walls']:
                if wkey(w) in sk: continue
                n += 1; r = clip(w['r'], st['inner']); Hh = hor(r); L = (r[2]-r[0]) if Hh else (r[3]-r[1])
                ds = [d for d in ref['doors'] if d['wall'] == w['id']]
                cands = [(r[0]+(r[2]-r[0])*f, (r[1]+r[3])/2) if Hh else ((r[0]+r[2])/2, r[1]+(r[3]-r[1])*f) for f in (.22, .78, .1, .9, .5)]
                pt = next((c for c in cands if all(abs((c[0] if Hh else c[1])-d['c']) > d['w']/2+.2 for d in ds)), cands[0])
                bubble(*pt, f'{pre}D{n}', '#d02f1c')
                reps.append(dict(rep=f'{pre}D{n}', kind='depose', L=round(L, 2), h=st['h'], surf=round(L*st['h'], 2), portes=len(ds)))
            for i, h, s, nm in st['swd']:
                n += 1; g = st['gaps'][i]; Hh = g[2]-g[0] > g[3]-g[1]; c = (g[0]+g[2])/2 if Hh else (g[1]+g[3])/2
                x, y = ((c, g[1]-.42) if Hh else (g[2]+.42, c))
                bubble(x, y, f'{pre}D{n}', '#d02f1c')
                reps.append(dict(rep=f'{pre}D{n}', kind='depose_porte', nom=nm))
            if st['opt']:
                o = st['opt']; e = .07
                rect([o[0]+e, o[1]+e, o[2]-e, o[3]-e], class_='opt')
                A(f'<text x="{X(o[2]-.15):.2f}" y="{Y(o[3]-.32):.2f}" class="t2" text-anchor="end" style="fill:#7a3fb5">Option : rehausse du plancher</text>')
            for pts, axis, off in chains: chain(X, Y, pts, axis, off)
        else:
            E = ELEC[lv]
            for a, b in LINKS[lv]:
                (_, x1, y1), (_, x2, y2) = E[a], E[b]
                mx, my = (X(x1)+X(x2))/2, (Y(y1)+Y(y2))/2 - 6
                A(f'<path d="M{X(x1):.2f} {Y(y1):.2f} Q{mx:.2f} {my:.2f} {X(x2):.2f} {Y(y2):.2f}" class="elw"/>')
            for t, x, y in E: symbol(A, t, X(x), Y(y))
        return reps

    OXR, OXE, OY = 34, 236, 34
    ch_r = [([0, 8.2], 'x', -12), ([0, 5.9], 'y', -16), ([2.91, 4.365, 4.435, 7.9], 'x', 8), ([.21, 1.115, 1.185, 3.005, 3.075, 5.69], 'y', -7)]
    ch_e = [([0, 8.2], 'x', -12), ([0, 5.9], 'y', -16), ([.24, 2.875, 2.945, 4.59, 4.66, 7.96], 'x', 8), ([.1, 2.065, 2.135, 2.79, 2.86, 4.1, 4.17, 5.8], 'y', -7)]
    REPS = {'rdc': plan('rdc', OXR, OY, ch_r), 'etage': plan('etage', OXE, OY, ch_e)}
    sub = 'Cloisonnement – échelle 1/50, cotes en mm' if mode == 'trav' else 'Électricité, VMC, points d\'eau – échelle 1/50, principe'
    for ox, t in ((OXR, 'REZ-DE-CHAUSSÉE'), (OXE, 'ÉTAGE')):
        A(f'<text x="{ox+82:.2f}" y="{OY+142:.2f}" class="t4 b" text-anchor="middle">{t}</text>')
        A(f'<text x="{ox+82:.2f}" y="{OY+147:.2f}" class="t2" text-anchor="middle">{sub}</text>')
        A(f'<text x="{ox+82:.2f}" y="{OY-17:.2f}" class="t2" text-anchor="middle">Façade est (rue)</text>')
    lx, ly = 34, 192
    A(f'<text x="{lx}" y="{ly}" class="t3 b">Légende</text>')
    if mode == 'trav':
        items = [('ex', 'Existant conservé'), ('por', 'Mur porteur conservé'), ('neuf', 'Cloison neuve (plaques de plâtre)'),
                 ('demo', 'Démolition / dépose'), ('agt', 'Dressing sur mesure (compris)'), ('mob', 'Mobilier indicatif (non compris)'), ('opt', 'Option : rehausse du plancher RDC')]
        for i, (c, t) in enumerate(items):
            y = ly + 5 + i*6; A(f'<rect x="{lx}" y="{y}" width="9" height="3.5" class="{c}"/><text x="{lx+12}" y="{y+3}" class="t2">{t}</text>')
        y = ly + 5 + len(items)*6
        A(f'<line x1="{lx}" y1="{y+1.7}" x2="{lx+9}" y2="{y+1.7}" class="demol"/><text x="{lx+12}" y="{y+3}" class="t2">Bloc-porte existant déposé (baie conservée)</text>')
        A(f'<text x="{lx}" y="{y+11}" class="t2">Surfaces indicatives, calculées entre cloisons.</text>')
        A(f'<text x="{lx}" y="{y+15}" class="t2">Cotes non relevées sur site : à vérifier avant exécution.</text>')
        nx, ny = 150, 192
        A(f'<text x="{nx}" y="{ny}" class="t3 b">Nomenclature des travaux</text>')
        cols = [(0, 'Rep.'), (14, 'Niveau'), (32, 'Désignation'), (200, 'Qté'), (222, 'U')]
        ny += 5
        for cx, t in cols: A(f'<text x="{nx+cx}" y="{ny}" class="t2 b">{t}</text>')
        A(f'<line x1="{nx}" y1="{ny+1.2}" x2="{nx+235}" y2="{ny+1.2}" class="fin"/>')
        rows = []; order = {'depose': 0, 'depose_porte': 1, 'cloison': 2, 'porte': 3, 'dressing': 4}
        for lv, nm in (('rdc', 'RDC'), ('etage', 'Étage')):
            for e in sorted(REPS[lv], key=lambda e: order[e['kind']]):
                k = e['kind']
                if k == 'cloison':
                    rows.append((e['rep'], nm, f"Cloison plaques de plâtre {'72/48' if e['ep'] < .085 else '98/48'} + laine minérale, L {fr(e['L'])} m × h {fr(e['h'])} m (baies déduites)", fr(e['surf']), 'm²'))
                elif k == 'porte':
                    rows.append((e['rep'], nm, f"Bloc-porte battant, vantail {round(e['w']*100)} × 204", '1', 'u'))
                elif k == 'depose':
                    rows.append((e['rep'], nm, f"Dépose cloison existante, L {fr(e['L'])} m × h {fr(e['h'])} m" + (f", y compris {e['portes']} bloc-porte" if e['portes'] else ''), fr(e['surf']), 'm²'))
                elif k == 'depose_porte':
                    rows.append((e['rep'], nm, f"Dépose bloc-porte existant, baie conservée : {e['nom']}", '1', 'u'))
                else:
                    rows.append((e['rep'], nm, f"Dressing sur mesure, L {fr(e['L'])} m × prof. {fr(e['p'])} m", fr(e['L']), 'ml'))
        for i, r in enumerate(rows):
            y = ny + 4.6 + i*3.9
            for (cx, _), v in zip(cols, r): A(f'<text x="{nx+cx}" y="{y}" class="t2">{esc(v)}</text>')
    else:
        sym = [('pl', 'Point lumineux en plafond (DCL)'), ('pc', 'Prise de courant 16 A'), ('int', 'Interrupteur simple allumage'),
               ('vv', 'Interrupteur va-et-vient'), ('ext_ex', 'Bouche d\'extraction VMC existante (à vérifier)'), ('ea', 'Entrée d\'air hygroréglable sur menuiserie'),
               ('eau', 'Point d\'eau existant conservé (EF / EC / EU)'), ('eau_x', 'Point d\'eau existant à neutraliser')]
        for i, (t, lab) in enumerate(sym):
            cx, cy = lx + 4.5, ly + 6.8 + i*6
            symbol(A, t, cx, cy)
            A(f'<text x="{lx+12}" y="{cy+1}" class="t2">{lab}</text>')
        y = ly + 6.8 + len(sym)*6
        A(f'<path d="M{lx} {y+1}Q{lx+4.5} {y-2} {lx+9} {y+1}" class="elw"/><text x="{lx+12}" y="{y+2}" class="t2">Commande d\'éclairage</text>')
        notes = ['Principe d\'implantation, à valider par l\'électricien selon NF C 15-100 et l\'existant.',
                 'Chambres : 3 prises 16 A mini, 1 point lumineux commandé à l\'entrée de la pièce.',
                 'Couloir RDC : point lumineux en va-et-vient depuis les deux extrémités.',
                 'VMC : air neuf par les entrées d\'air des chambres, transit sous portes (détalonnage 1 cm),',
                 'extraction par les bouches existantes des pièces humides (SDB, cuisine), à contrôler.',
                 'Évier existant du RDC (zone Ch. parentale) : alimentations EF / EC et évacuation',
                 'à couper, bouchonner et neutraliser en amont ; positions des points d\'eau à relever.',
                 'Tableau électrique : capacité et protections différentielles à vérifier avant travaux.']
        A(f'<text x="150" y="{ly}" class="t3 b">Notes</text>')
        for i, t in enumerate(notes): A(f'<text x="150" y="{ly+6+i*4.6}" class="t2">{esc(t)}</text>')
        cnt = {}
        for lv in ELEC:
            for t, *_ in ELEC[lv]: cnt[(lv, t)] = cnt.get((lv, t), 0) + 1
        A(f'<text x="290" y="{ly}" class="t3 b">Quantités</text>')
        labs = [('pl', 'Points lumineux'), ('pc', 'Prises 16 A'), ('int', 'Interrupteurs simples'), ('vv', 'Va-et-vient'), ('ea', 'Entrées d\'air'),
                ('ext_ex', 'Bouches extraction existantes'), ('eau', 'Points d\'eau conservés'), ('eau_x', 'Points d\'eau à neutraliser')]
        A(f'<text x="290" y="{ly+6}" class="t2 b">Désignation</text><text x="350" y="{ly+6}" class="t2 b">RDC</text><text x="365" y="{ly+6}" class="t2 b">Étage</text><text x="382" y="{ly+6}" class="t2 b">Total</text>')
        for i, (t, l) in enumerate(labs):
            a, b = cnt.get(('rdc', t), 0), cnt.get(('etage', t), 0); y = ly + 10.5 + i*4.4
            A(f'<text x="290" y="{y}" class="t2">{l}</text><text x="352" y="{y}" class="t2">{a}</text><text x="367" y="{y}" class="t2">{b}</text><text x="384" y="{y}" class="t2 b">{a+b}</text>')
        REPS['elec'] = {f'{lv}:{t}': n for (lv, t), n in cnt.items()}
    A('</svg>')
    return '\n'.join(svg), REPS


os.makedirs(OUTD, exist_ok=True)
s1, r1 = page('trav'); s2, r2 = page('elec')
open(f'{OUTD}/p1.svg', 'w').write(s1); open(f'{OUTD}/p2.svg', 'w').write(s2)
r1['elec'] = r2['elec']
json.dump(r1, open(f'{OUTD}/reps.json', 'w'), ensure_ascii=False, indent=1)
