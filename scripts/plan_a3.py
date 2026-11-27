import json, math, sys

S = json.load(open(sys.argv[1]))
OUT = sys.argv[2]
D, W = 5.9, 8.2
SC = 20.0  # mm papier par m (1/50)

ST = {
 'rdc': dict(h=2.6, walls=[[0,0,8.2,.21],[7.9,.21,8.2,5.69],[0,5.69,8.2,5.9],[0,.21,.3,5.69]], por=[[2.71,.21,2.91,5.69]],
   fixed=[[.3,2.16,2.71,2.26],[.3,4.13,2.71,4.23]],
   win=[[1.14,0,2.51,.21],[3.05,0,5.09,.21],[5.45,0,7.6,.21],[5.5,5.69,7.88,5.9],[2.92,5.69,5.25,5.9]],
   gaps=[[.95,5.69,1.9,5.9],[2.71,1.16,2.91,1.86],[2.71,4.25,2.91,5.05],[1.75,4.13,2.58,4.23]], sw=[[0,0,0],[1,0,0],[2,1,0],[3,0,0]],
   stair=[.3,2.26,1.99,3.97], beam=None, inner=[.3,.21,7.9,5.69]),
 'etage': dict(h=2.5, walls=[[0,0,8.2,.1],[7.96,.1,8.2,5.8],[0,5.8,8.2,5.9],[0,.1,.24,5.8]], por=[[2.71,2.86,2.91,5.8]],
   fixed=[[.24,2.1,2.06,2.17],[1.99,2.17,2.06,3.46]],
   win=[[1.15,0,2.77,.1],[3.01,0,4.64,.1],[5.31,0,7.36,.1],[5.32,5.8,7.6,5.9],[3.22,5.8,5.15,5.9],[0,4.65,.24,5.35],[0,2.86,.24,3.57],[0,1.16,.24,2.11]],
   gaps=[[2.71,3.07,2.91,3.86]], sw=[], stair=[.24,2.17,1.99,3.97], beam=[2.71,.1,2.91,2.86], inner=[.24,.1,7.96,5.8]),
}
AREAS = {'rdc': {}, 'etage': {}}  # complétées par argv[3]
if len(sys.argv) > 3:
    AREAS = json.load(open(sys.argv[3]))

hor = lambda r: (r[2]-r[0]) >= (r[3]-r[1])
wkey = lambda w: ','.join('%.2f' % v for v in w['r'])

def clip(r, b):
    return [max(r[0], b[0]), max(r[1], b[1]), min(r[2], b[2]), min(r[3], b[3])]

def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

svg = []
REPS = {}
A = svg.append

def plan(lv, ox, oy, chains):
    st = ST[lv]; ref = S[lv][0]; sc = next(s for s in S[lv] if s['name'] == 'Alex')
    X = lambda x: ox + x*SC
    Y = lambda y: oy + (D - y)*SC
    def rect(r, **kw):
        a = ' '.join(f'{k.rstrip("_").replace("_","-")}="{v}"' for k, v in kw.items())
        A(f'<rect x="{X(r[0]):.2f}" y="{Y(r[3]):.2f}" width="{(r[2]-r[0])*SC:.2f}" height="{(r[3]-r[1])*SC:.2f}" {a}/>')
    def line(a, b, c, d, cls):
        A(f'<line x1="{X(a):.2f}" y1="{Y(b):.2f}" x2="{X(c):.2f}" y2="{Y(d):.2f}" class="{cls}"/>')
    # escalier / trémie
    s0 = st['stair']
    rect(s0, fill='none', class_='fin')
    if lv == 'rdc':
        n = 10
        for i in range(1, n):
            y = s0[1] + (s0[3]-s0[1])*i/n
            line(s0[0], y, s0[2], y, 'fin')
    else:
        line(s0[0], s0[1], s0[2], s0[3], 'fin'); line(s0[0], s0[3], s0[2], s0[1], 'fin')
        A(f'<text x="{X((s0[0]+s0[2])/2):.2f}" y="{Y((s0[1]+s0[3])/2)-1.5:.2f}" class="t2" text-anchor="middle" fill="#fff" stroke="#fff" stroke-width="1.2">Trémie</text>')
        A(f'<text x="{X((s0[0]+s0[2])/2):.2f}" y="{Y((s0[1]+s0[3])/2)-1.5:.2f}" class="t2" text-anchor="middle">Trémie</text>')
    # mobilier indicatif
    for o in sc.get('beds', []):
        a_ = o['l'] if o['rot'] % 2 else o['w']; c_ = o['w'] if o['rot'] % 2 else o['l']
        r = [o['x']-a_/2, o['y']-c_/2, o['x']+a_/2, o['y']+c_/2]
        rect(r, class_='mob')
    # structure
    for r in st['walls']: rect(r, class_='ex')
    for r in st['por']: rect(r, class_='por')
    if st['beam']:
        b = st['beam']; line(b[0], b[1], b[0], b[3], 'cache'); line(b[2], b[1], b[2], b[3], 'cache')
    for r in st['fixed']: rect(r, class_='ex')
    # démolitions (cloisons de l'existant absentes du scénario)
    sk = {wkey(w) for w in sc['walls']}
    for w in ref['walls']:
        if wkey(w) not in sk: rect(clip(w['r'], st['inner']), class_='demo')
    # cloisons du scénario
    rk = {wkey(w) for w in ref['walls']}
    for w in sc['walls']:
        r = clip(w['r'], st['inner'])
        rect(r, class_='neuf' if wkey(w) not in rk else 'ex')
    # ouvertures
    for g in st['win']:
        rect(g, fill='#fff', stroke='none')
        Hh = g[2]-g[0] > g[3]-g[1]
        if Hh:
            for f in (g[1], g[3], (g[1]+g[3])/2): line(g[0], f, g[2], f, 'fin')
            line(g[0], g[1], g[0], g[3], 'trait'); line(g[2], g[1], g[2], g[3], 'trait')
        else:
            for f in (g[0], g[2], (g[0]+g[2])/2): line(f, g[1], f, g[3], 'fin')
            line(g[0], g[1], g[2], g[1], 'trait'); line(g[0], g[3], g[2], g[3], 'trait')
    def door(r, c, wd, h, s, cut=True):
        Hh = hor(r); a, b = c-wd/2, c+wd/2
        gap = [a, r[1], b, r[3]] if Hh else [r[0], a, r[2], b]
        if cut:
            rect(gap, fill='#fff', stroke='none')
            if Hh: line(a, r[1], a, r[3], 'trait'); line(b, r[1], b, r[3], 'trait')
            else: line(r[0], a, r[2], a, 'trait'); line(r[0], b, r[2], b, 'trait')
        if Hh:
            hx, ox_ = (b, a) if h else (a, b); yy = r[3] if s else r[1]; ly = yy + (1 if s else -1)*wd
            line(hx, yy, hx, ly, 'trait')
            sweep = 1 if (h ^ s) else 0
            A(f'<path d="M{X(hx):.2f} {Y(ly):.2f} A{wd*SC:.2f} {wd*SC:.2f} 0 0 {sweep} {X(ox_):.2f} {Y(yy):.2f}" class="fin"/>')
        else:
            hy, oy_ = (b, a) if h else (a, b); xx = r[2] if s else r[0]; lx = xx + (1 if s else -1)*wd
            line(xx, hy, lx, hy, 'trait')
            sweep = 0 if (h ^ s) else 1
            A(f'<path d="M{X(lx):.2f} {Y(hy):.2f} A{wd*SC:.2f} {wd*SC:.2f} 0 0 {sweep} {X(xx):.2f} {Y(oy_):.2f}" class="fin"/>')
        return gap
    for g in st['gaps']: rect(g, fill='#fff', stroke='none')
    for i, h, s in st['sw']:
        g = st['gaps'][i]; Hh = g[2]-g[0] > g[3]-g[1]
        c = (g[0]+g[2])/2 if Hh else (g[1]+g[3])/2; wd = (g[2]-g[0]) if Hh else (g[3]-g[1])
        door(g, c, wd, h, s, cut=False)
    reps = []
    REPS[lv] = []
    for d in sc['doors']:
        w = next(x for x in sc['walls'] if x['id'] == d['wall'])
        gap = door(w['r'], d['c'], d['w'], d['h'], d['s'])
        reps.append((d, w, gap))
    rkd = {(wkey(next(x for x in ref['walls'] if x['id']==d['wall'])), round(d['c'],2), d['w']) for d in ref['doors']}
    def bubble(x, y, txt):
        A(f'<circle cx="{X(x):.2f}" cy="{Y(y):.2f}" r="3.3" fill="#fff" stroke="#000" stroke-width=".25"/><text x="{X(x):.2f}" y="{Y(y)+.8:.2f}" class="t2 b" style="font-size:2.3px" text-anchor="middle">{txt}</text>')
    H_ = st['h']; pre = 'R' if lv == 'rdc' else 'E'
    n = 0
    for w in sc['walls']:
        if wkey(w) in rk: continue
        n += 1; r = clip(w['r'], st['inner']); Hh = hor(r)
        L = (r[2]-r[0]) if Hh else (r[3]-r[1]); ep = min(r[2]-r[0], r[3]-r[1])
        ds = [d for d in sc['doors'] if d['wall'] == w['id']]
        surf = L*H_ - sum(d['w']*2.04 for d in ds)
        # position de la bulle : au tiers de la cloison, hors des portes
        cands = [(r[0]+(r[2]-r[0])*f, (r[1]+r[3])/2) if Hh else ((r[0]+r[2])/2, r[1]+(r[3]-r[1])*f) for f in (.5, .3, .7, .15, .85)]
        def free(pt):
            v = pt[0] if Hh else pt[1]
            return all(abs(v-d['c']) > d['w']/2+.2 for d in ds)
        pt = next((c for c in cands if free(c)), cands[0])
        bubble(pt[0], pt[1], f'{pre}C{n}')
        REPS[lv].append(dict(rep=f'{pre}C{n}', kind='cloison', ep=round(ep,3), L=round(L,2), h=H_, surf=round(surf,2), portes=len(ds)))
    n = 0
    for d, w, gap in reps:
        k = (wkey(w), round(d['c'],2), d['w'])
        if k in rkd: continue
        n += 1; r = w['r']; Hh = hor(r); o = .42*(1 if d['s'] else -1)
        x, y = ((d['c'], (r[3] if d['s'] else r[1]) + o) if Hh else ((r[2] if d['s'] else r[0]) + o, d['c']))
        bubble(x, y, f'{pre}P{n}')
        REPS[lv].append(dict(rep=f'{pre}P{n}', kind='porte', w=d['w'], ty=d.get('ty','b'), neuve_cloison=wkey(w) not in rk))
    n = 0
    for w in ref['walls']:
        if wkey(w) in sk: continue
        n += 1; r = clip(w['r'], st['inner']); Hh = hor(r); L = (r[2]-r[0]) if Hh else (r[3]-r[1])
        ds = [d for d in ref['doors'] if d['wall'] == w['id']]
        pt = ((r[0]+r[2])/2, (r[1]+r[3])/2)
        cands = [(r[0]+(r[2]-r[0])*f, (r[1]+r[3])/2) if Hh else ((r[0]+r[2])/2, r[1]+(r[3]-r[1])*f) for f in (.5, .3, .7, .15, .85)]
        cands = [(r[0]+(r[2]-r[0])*f, (r[1]+r[3])/2) if Hh else ((r[0]+r[2])/2, r[1]+(r[3]-r[1])*f) for f in (.22, .78, .1, .9, .5)]
        pt = next((c for c in cands if all(abs((c[0] if Hh else c[1])-d['c']) > d['w']/2+.2 for d in ds)), cands[0])
        bubble(pt[0], pt[1], f'{pre}D{n}')
        REPS[lv].append(dict(rep=f'{pre}D{n}', kind='depose', L=round(L,2), h=H_, surf=round(L*H_,2), portes=len(ds)))
    # pièces
    ar = AREAS.get(lv, {})
    for l in sc['labels']:
        x, y = X(l['x']), Y(l['y'])
        a = ar.get(l['id'])
        A(f'<text x="{x:.2f}" y="{y:.2f}" class="t3 b" text-anchor="middle">{esc(l["t"])}</text>')
        if a: A(f'<text x="{x:.2f}" y="{y+3.6:.2f}" class="t2" text-anchor="middle">{a:.2f} m²'.replace('.', ',') + '</text>')
    for (lx, ly, t, a) in ar.get('_extra', []):
        A(f'<text x="{X(lx):.2f}" y="{Y(ly):.2f}" class="t3 b" text-anchor="middle">{esc(t)}</text>')
        A(f'<text x="{X(lx):.2f}" y="{Y(ly)+3.6:.2f}" class="t2" text-anchor="middle">{a:.2f} m²'.replace('.', ',') + '</text>')
    # chaînes de cotes (mm)
    def chain(pts, axis, off):
        pts = sorted(set(round(p, 3) for p in pts))
        if axis == 'x':
            yy = Y(0) + off if off > 0 else Y(D) + off
            A(f'<line x1="{X(pts[0]):.2f}" y1="{yy:.2f}" x2="{X(pts[-1]):.2f}" y2="{yy:.2f}" class="cote"/>')
            for p in pts:
                A(f'<line x1="{X(p):.2f}" y1="{yy-1.2:.2f}" x2="{X(p):.2f}" y2="{yy+1.2:.2f}" class="cote"/>')
                A(f'<line x1="{X(p)-.9:.2f}" y1="{yy+.9:.2f}" x2="{X(p)+.9:.2f}" y2="{yy-.9:.2f}" class="trait"/>')
            for a, b in zip(pts, pts[1:]):
                v = round((b-a)*1000)
                small = (b-a)*SC < 6
                A(f'<text x="{X((a+b)/2):.2f}" y="{yy-(4.2 if small else 1):.2f}" class="t2" text-anchor="middle">{v}</text>')
        else:
            xx = X(W) + off if off > 0 else X(0) + off
            A(f'<line x1="{xx:.2f}" y1="{Y(pts[0]):.2f}" x2="{xx:.2f}" y2="{Y(pts[-1]):.2f}" class="cote"/>')
            for p in pts:
                A(f'<line x1="{xx-1.2:.2f}" y1="{Y(p):.2f}" x2="{xx+1.2:.2f}" y2="{Y(p):.2f}" class="cote"/>')
                A(f'<line x1="{xx-.9:.2f}" y1="{Y(p)+.9:.2f}" x2="{xx+.9:.2f}" y2="{Y(p)-.9:.2f}" class="trait"/>')
            for i, (a, b) in enumerate(zip(pts, pts[1:])):
                v = round((b-a)*1000)
                small = (b-a)*SC < 6
                tx = xx + (1.6 if off > 0 else -1.6) + ((5 if off > 0 else -5) if small and i % 2 else 0)
                A(f'<text x="{tx:.2f}" y="{Y((a+b)/2)+1:.2f}" class="t2" text-anchor="{"start" if off > 0 else "end"}">{v}</text>')
    for pts, axis, off in chains: chain(pts, axis, off)
    return sc, reps

# ---------- page A3 paysage ----------
PW, PH = 420, 297
A(f'<svg xmlns="http://www.w3.org/2000/svg" width="{PW}mm" height="{PH}mm" viewBox="0 0 {PW} {PH}" font-family="DejaVu Sans, Arial, sans-serif">')
A('''<defs><pattern id="hn" width="1.2" height="1.2" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="1.2" height="1.2" fill="#dbe6ff"/><line x1="0" y1="0" x2="0" y2="1.2" stroke="#1240e0" stroke-width="0.22"/></pattern><pattern id="hd" width="1.2" height="1.2" patternUnits="userSpaceOnUse" patternTransform="rotate(-45)"><rect width="1.2" height="1.2" fill="#ffe1dc"/><line x1="0" y1="0" x2="0" y2="1.2" stroke="#d02f1c" stroke-width="0.18"/></pattern></defs>
<style>
.ex{fill:#9a9a9a;stroke:#000;stroke-width:.25}.por{fill:#4d4d4d;stroke:#000;stroke-width:.25}
.neuf{fill:url(#hn);stroke:#1240e0;stroke-width:.45}.demo{fill:url(#hd);stroke:#d02f1c;stroke-width:.3;stroke-dasharray:1.2 .8}
.trait{stroke:#000;stroke-width:.35;fill:none}.fin{stroke:#000;stroke-width:.13;fill:none}.cache{stroke:#000;stroke-width:.18;stroke-dasharray:1.5 1;fill:none}
.cote{stroke:#000;stroke-width:.13}.mob{fill:none;stroke:#8c8c8c;stroke-width:.13;stroke-dasharray:.8 .6}
.t2{font-size:2.5px}.t3{font-size:3px}.t4{font-size:4.2px}.b{font-weight:bold}
</style><rect width="420" height="297" fill="#fff"/>''')

OXR, OXE, OY = 34, 236, 34
rdc_chains = [
  ([0, 8.2], 'x', -12), ([0, 5.9], 'y', -16),
  ([2.91, 4.365, 4.435, 7.9], 'x', 8),
  ([.21, 1.115, 1.185, 3.005, 3.075, 5.69], 'y', -7),
]
et_chains = [
  ([0, 8.2], 'x', -12), ([0, 5.9], 'y', -16),
  ([.24, 2.875, 2.945, 4.59, 4.66, 7.96], 'x', 8),
  ([.1, 2.065, 2.135, 2.79, 2.86, 4.1, 4.17, 5.8], 'y', -7),
]
sc_r, reps_r = plan('rdc', OXR, OY, rdc_chains)
sc_e, reps_e = plan('etage', OXE, OY, et_chains)
for ox, t in ((OXR, 'REZ-DE-CHAUSSÉE'), (OXE, 'ÉTAGE')):
    A(f'<text x="{ox + 82:.2f}" y="{OY + 118 + 24:.2f}" class="t4 b" text-anchor="middle">{t}</text>')
    A(f'<text x="{ox + 82:.2f}" y="{OY + 118 + 29:.2f}" class="t2" text-anchor="middle">Échelle 1/50 – cotes en mm</text>')
# nord / repère façade
A(f'<text x="{OXR+82:.2f}" y="{OY-17:.2f}" class="t2" text-anchor="middle">Façade est (rue)</text>')
A(f'<text x="{OXE+82:.2f}" y="{OY-17:.2f}" class="t2" text-anchor="middle">Façade est (rue)</text>')

# ---------- légende ----------
lx, ly = 34, 192
A(f'<text x="{lx}" y="{ly}" class="t3 b">Légende</text>')
items = [('ex', 'Existant conservé'), ('por', 'Mur porteur conservé'), ('neuf', 'Cloison neuve (plaques de plâtre) – bleu'), ('demo', 'Démolition / dépose – rouge'), ('mob', 'Mobilier indicatif (non compris)')]
for i, (c, t) in enumerate(items):
    y = ly + 5 + i*6
    A(f'<rect x="{lx}" y="{y}" width="9" height="3.5" class="{c}"/>')
    A(f'<text x="{lx+12}" y="{y+3}" class="t2">{t}</text>')
y = ly + 5 + len(items)*6
A(f'<line x1="{lx}" y1="{y+1.7}" x2="{lx+9}" y2="{y+1.7}" class="cache"/><text x="{lx+12}" y="{y+3}" class="t2">Poutre existante (étage)</text>')
A(f'<text x="{lx}" y="{y+11}" class="t2">Surfaces habitables indicatives, calculées entre cloisons.</text>')
A(f'<text x="{lx}" y="{y+15}" class="t2">Cotes non relevées sur site : à vérifier avant exécution.</text>')

nx, ny = 150, 192
A(f'<text x="{nx}" y="{ny}" class="t3 b">Nomenclature des travaux</text>')
cols = [(0,'Rep.'),(14,'Niveau'),(32,'Désignation'),(200,'Qté'),(222,'U')]
ny += 5
for cx, t in cols: A(f'<text x="{nx+cx}" y="{ny}" class="t2 b">{t}</text>')
A(f'<line x1="{nx}" y1="{ny+1.2}" x2="{nx+235}" y2="{ny+1.2}" class="fin"/>')
rows = []
for lv, nm in (('rdc','RDC'),('etage','Étage')):
    for e in REPS[lv]:
        if e['kind']=='cloison':
            typ = '72/48' if e['ep'] < .085 else '98/48'
            rows.append((e['rep'], nm, f"Cloison plaques de plâtre {typ} + laine minérale, L {e['L']:.2f} m × h {e['h']:.2f} m (baies déduites)".replace('.', ','), f"{e['surf']:.2f}".replace('.', ','), 'm²'))
        elif e['kind']=='porte':
            rows.append((e['rep'], nm, f"Bloc-porte {'battant' if e['ty']=='b' else 'coulissant' if e['ty']=='c' else 'à galandage'}, vantail {round(e['w']*100)} × 204"+('' if e['neuve_cloison'] else ', baie à créer dans cloison existante'), '1', 'u'))
        else:
            rows.append((e['rep'], nm, f"Dépose cloison existante, L {e['L']:.2f} m × h {e['h']:.2f} m".replace('.', ',')+(f", y compris {e['portes']} bloc-porte" if e['portes'] else ''), f"{e['surf']:.2f}".replace('.', ','), 'm²'))
for i, r in enumerate(rows):
    y = ny + 5 + i*4.3
    for (cx, _), v in zip(cols, r): A(f'<text x="{nx+cx}" y="{y}" class="t2">{esc(v)}</text>')
json.dump(REPS, open(OUT.replace('.svg', '_reps.json'), 'w'), ensure_ascii=False, indent=1)
open(OUT, 'w').write('\n'.join(svg) + '</svg>')
