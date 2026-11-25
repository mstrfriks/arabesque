# encoding: UTF-8
# =============================================================================
# Maquette RDC + étage – d'après les plans (2 niveaux) et la façade est projet 1/50
#
# Utilisation (SketchUp Pro, ou SketchUp Make 2017) :
#   Fenêtre > Console Ruby (ou Extensions > Developer > Ruby Console), puis :
#   load "C:/chemin/vers/maquette_rdc_etage.rb"
#
# Repère (en mètres) :
#   x = largeur de façade, 0 = bord gauche du plan
#   y = profondeur, 0 = façade bas du plan (arrière), D = façade haut du plan (façade est / rue)
#   z = 0 au sol fini du RDC
#
# Cotes reprises des plans ; ce qui n'est pas coté (épaisseurs, profondeur
# hors œuvre, allèges façade arrière et pignons) est estimé : à vérifier sur site.
# =============================================================================

module ADFPlan
  W        = 8.20   # largeur hors œuvre (cote façade)
  D        = 5.90   # profondeur hors œuvre (5,48 int. RDC / 5,70 int. étage + murs)
  Z_ETAGE  = 2.80   # niveau fini étage (estimé)
  H_RDC    = 2.60   # hauteur sous plafond RDC (dalle 20 cm)
  H_ETAGE  = 2.50   # hauteur cloisons étage
  H_MUR_ET = 2.83   # murs étage jusqu'au chéneau : 0,55+1,70+1,45+1,33+0,60 = 5,63
  EP_CL    = 0.07
  PORTE_H  = 2.04

  T_STRUCT = "00 Structure conservée"
  T_KEEP   = "01 RDC - cloisons conservées"
  T_EX     = "02 RDC - existant"
  T_SC1    = "03 RDC - scénario 1 (3 chambres)"
  T_ETAGE  = "04 Étage - existant"
  T_ESC    = "05 Escalier"

  # [nom, tag, x0,y0, x1,y1, z0, hauteur, épaisseur, ouvertures]
  # L'épaisseur part du trait x0,y0 -> x1,y1 vers sa GAUCHE.
  # Ouverture = [distance depuis x0,y0, largeur, allège, hauteur]
  MURS = [
    # --- RDC, murs extérieurs (façade est = cotes du PC) ---
    ["Façade arrière RDC", T_STRUCT, 0, 0, W, 0, 0, Z_ETAGE, 0.21,
     [[1.14, 1.37, 0.90, 1.35], [3.05, 2.04, 0.90, 1.35], [5.45, 2.15, 0.90, 1.35]]],
    ["Pignon droit RDC", T_STRUCT, W, 0.21, W, D - 0.21, 0, Z_ETAGE, 0.30, []],
    ["Façade est RDC", T_STRUCT, W, D, 0, D, 0, Z_ETAGE, 0.21,
     [[0.32, 2.38, 0.55, 1.70], [2.95, 2.33, 0.55, 1.70], [6.30, 0.95, 0.00, 2.20]]],
    ["Pignon gauche RDC", T_STRUCT, 0, D - 0.21, 0, 0.21, 0, Z_ETAGE, 0.30, []],
    ["Mur porteur RDC", T_STRUCT, 2.91, 0.21, 2.91, D - 0.21, 0, H_RDC, 0.20,
     [[0.95, 0.70, 0, PORTE_H], [4.04, 0.80, 0, PORTE_H]]],

    # --- Étage, murs extérieurs ---
    ["Façade arrière étage", T_STRUCT, 0, 0, W, 0, Z_ETAGE, H_MUR_ET, 0.10,
     [[1.15, 1.62, 0.90, 1.35], [3.01, 1.63, 0.90, 1.35], [5.31, 2.05, 0.90, 1.35]]],
    ["Pignon droit étage", T_STRUCT, W, 0.10, W, D - 0.10, Z_ETAGE, H_MUR_ET, 0.24, []],
    ["Façade est étage", T_STRUCT, W, D, 0, D, Z_ETAGE, H_MUR_ET, 0.10,
     [[0.60, 2.28, 0.90, 1.33], [3.05, 1.93, 0.90, 1.33]]],
    ["Pignon gauche étage", T_STRUCT, 0, D - 0.10, 0, 0.10, Z_ETAGE, H_MUR_ET, 0.24,
     [[2.23, 0.71, 0.90, 1.35], [3.69, 0.95, 0.90, 1.35]]],
    ["Mur porteur étage", T_STRUCT, 2.91, 0.10, 2.91, D - 0.10, Z_ETAGE, H_ETAGE, 0.20,
     [[0.00, 2.76, 0, 2.30], [2.97, 0.79, 0, PORTE_H]]],

    # --- RDC, cloisons conservées (entrée / escalier / SDB) ---
    ["Cloison SDB / escalier", T_KEEP, 0.30, 2.16, 2.71, 2.16, 0, H_RDC, 0.10, []],
    ["Cloison entrée / escalier", T_KEEP, 0.30, 4.13, 1.62, 4.13, 0, H_RDC, 0.10, []],

    # --- RDC existant : chambre 7,07 m² ---
    ["Chambre - cloison haute", T_EX, 5.15, 2.81, 7.90, 2.81, 0, H_RDC, EP_CL, []],
    ["Chambre - cloison gauche", T_EX, 5.22, 0.21, 5.22, 2.88, 0, H_RDC, EP_CL,
     [[1.24, 0.80, 0, PORTE_H]]],

    # --- RDC scénario 1 : couloir le long du mur porteur, 3 chambres ---
    ["Sc1 Ch.2 - cloison haute", T_SC1, 5.15, 2.81, 7.90, 2.81, 0, H_RDC, EP_CL,
     [[0.21, 0.80, 0, PORTE_H]]],
    ["Sc1 Ch.2 - cloison gauche", T_SC1, 5.22, 0.21, 5.22, 2.88, 0, H_RDC, EP_CL, []],
    ["Sc1 Ch.3 - cloison haute", T_SC1, 2.91, 2.81, 5.15, 2.81, 0, H_RDC, EP_CL,
     [[0.10, 0.80, 0, PORTE_H]]],
    ["Sc1 couloir / Ch.1", T_SC1, 3.91, 3.70, 3.91, 5.69, 0, H_RDC, 0.10,
     [[0.30, 0.83, 0, PORTE_H]]],
    ["Sc1 Ch.1 - cloison basse", T_SC1, 3.91, 3.70, 6.30, 3.70, 0, H_RDC, 0.10, []],
    ["Sc1 fond de couloir", T_SC1, 6.30, 2.88, 6.30, 3.70, 0, H_RDC, 0.10, []],

    # --- Étage existant ---
    ["Cloison SDB étage", T_ETAGE, 0.24, 4.10, 2.71, 4.10, Z_ETAGE, H_ETAGE, EP_CL,
     [[1.71, 0.70, 0, PORTE_H]]],
    ["Cloison chambre / séjour (vert.)", T_ETAGE, 4.66, 0.10, 4.66, 2.86, Z_ETAGE, H_ETAGE, EP_CL, []],
    ["Cloison chambre / séjour (horiz.)", T_ETAGE, 2.91, 2.79, 4.66, 2.79, Z_ETAGE, H_ETAGE, EP_CL, []],
    ["Garde-corps trémie (bas)", T_ETAGE, 0.24, 2.10, 2.06, 2.10, Z_ETAGE, 1.00, EP_CL, []],
    ["Garde-corps trémie (droite)", T_ETAGE, 2.06, 2.17, 2.06, 3.46, Z_ETAGE, 1.00, EP_CL, []]
  ]

  # [nom, tag, x0,y0, x1,y1, z0, épaisseur, trémies [[x0,y0,x1,y1]]]
  DALLES = [
    ["Dallage RDC", T_STRUCT, 0, 0, W, D, -0.20, 0.20, []],
    ["Plancher étage", T_STRUCT, 0.30, 0.21, 7.90, D - 0.21, H_RDC, Z_ETAGE - H_RDC,
     [[0.30, 2.26, 1.99, 3.97]]],
    ["Escalier 1/4 tournant (volume simplifié)", T_ESC, 0.30, 2.26, 1.99, 3.97, 0, H_RDC, []]
  ]

  # [texte, tag, x, y, z]
  TEXTES = [
    ["Entrée", T_KEEP, 1.4, 4.9, 0.05],
    ["SDB", T_KEEP, 1.4, 1.1, 0.05],
    ["Cuisine / séjour 20,00 m²", T_EX, 5.2, 4.3, 0.05],
    ["Chambre 7,07 m²", T_EX, 6.5, 1.5, 0.05],
    ["Ch.1 ≈ 9,0 m²", T_SC1, 5.8, 4.7, 0.05],
    ["Ch.2 7,07 m²", T_SC1, 6.5, 1.5, 0.05],
    ["Ch.3 ≈ 5,8 m² (+ SDB)", T_SC1, 4.0, 1.5, 0.05],
    ["Couloir ≈ 4,5 m²", T_SC1, 4.6, 3.3, 0.05],
    ["SDB 4,08 m²", T_ETAGE, 1.4, 4.9, Z_ETAGE + 0.05],
    ["Chambre 12,38 m²", T_ETAGE, 1.2, 1.0, Z_ETAGE + 0.05],
    ["Cuisine / séjour 23,66 m²", T_ETAGE, 6.0, 4.0, Z_ETAGE + 0.05]
  ]

  RACINE = "Maquette RDC + étage"

  # ------------------------------------------------------------------ outils
  def self.pt(x, y, z)
    Geom::Point3d.new(x.m, y.m, z.m)
  end

  def self.tag(nom)
    calques = Sketchup.active_model.layers
    calques[nom] || calques.add(nom)
  end

  def self.mat(nom, rgb, alpha = 1.0)
    mats = Sketchup.active_model.materials
    mt = mats[nom] || mats.add(nom)
    mt.color = Sketchup::Color.new(*rgb)
    mt.alpha = alpha
    mt
  end

  def self.nettoyer(ents)
    ents.grep(Sketchup::Edge).select { |ed| ed.faces.empty? }.each(&:erase!)
  end

  def self.mur(parent, nom, tg, x0, y0, x1, y1, z0, h, ep, ouv = [], materiau = nil)
    g = parent.add_group
    g.name = nom
    g.layer = tag(tg)
    e = g.entities
    l = Math.hypot(x1 - x0, y1 - y0)
    ux = (x1 - x0) / l
    uy = (y1 - y0) / l
    p = lambda { |s, z| pt(x0 + ux * s, y0 + uy * s, z0 + z) }
    e.add_face(p[0, 0], p[l, 0], p[l, h], p[0, h])
    ouv.each do |s, w, a, oh|
      haut = [a + oh, h].min
      f = e.add_face(p[s, a], p[s + w, a], p[s + w, haut], p[s, haut])
      f.erase! if f && f.valid?
    end
    nettoyer(e)
    face = e.grep(Sketchup::Face).max_by(&:area)
    gauche = Geom::Vector3d.new(-uy, ux, 0)
    face.reverse! if face.normal.dot(gauche) < 0
    face.pushpull(ep.m)
    g.material = materiau if materiau
    g
  end

  def self.dalle(parent, nom, tg, x0, y0, x1, y1, z0, ep, trous = [], materiau = nil)
    g = parent.add_group
    g.name = nom
    g.layer = tag(tg)
    e = g.entities
    e.add_face(pt(x0, y0, z0), pt(x1, y0, z0), pt(x1, y1, z0), pt(x0, y1, z0))
    trous.each do |a, b, c, d|
      f = e.add_face(pt(a, b, z0), pt(c, b, z0), pt(c, d, z0), pt(a, d, z0))
      f.erase! if f && f.valid?
    end
    nettoyer(e)
    face = e.grep(Sketchup::Face).max_by(&:area)
    face.reverse! if face.normal.z < 0
    face.pushpull(ep.m)
    g.material = materiau if materiau
    g
  end

  def self.racine
    ents = Sketchup.active_model.entities
    g = ents.grep(Sketchup::Group).find { |x| x.name == RACINE }
    g ? g.entities : ents
  end

  # --------------------------------------------------------------- maquette
  def self.construire
    m = Sketchup.active_model
    m.start_operation(RACINE, true)
    root = m.entities.add_group
    root.name = RACINE
    e = root.entities

    m_struct  = mat("Existant conservé", [200, 200, 195])
    m_porteur = mat("Mur porteur", [150, 110, 100])
    m_cloison = mat("Cloison existante", [235, 235, 230])
    m_neuf    = mat("Cloison neuve", [216, 90, 48])
    m_esc     = mat("Escalier", [120, 140, 170], 0.35)
    par_tag = { T_STRUCT => m_struct, T_KEEP => m_cloison, T_EX => m_cloison,
                T_SC1 => m_neuf, T_ETAGE => m_cloison }

    MURS.each do |a|
      materiau = a[0].start_with?("Mur porteur") ? m_porteur : par_tag[a[1]]
      mur(e, *a, materiau)
    end
    DALLES.each do |a|
      materiau = a[1] == T_ESC ? m_esc : m_struct
      dalle(e, *a, materiau)
    end
    TEXTES.each do |txt, tg, x, y, z|
      t = e.add_text(txt, pt(x, y, z))
      t.layer = tag(tg)
    end

    tag(T_SC1).visible = false
    m.commit_operation
    m.active_view.zoom_extents
    puts "Maquette créée. Balises : affiche « #{T_SC1} » et masque « #{T_EX} » pour comparer."
  rescue => err
    m.abort_operation
    raise err
  end

  # ------------------------------------------------- tester d'autres scénarios
  # Depuis la console Ruby, par exemple :
  #   ADFPlan.cloison("07 RDC - scénario 2", 2.91, 2.81, 5.15, 2.81, portes: [[0.10, 0.80]])
  #   ADFPlan.cloison("08 Étage - scénario A", 4.66, 0.10, 4.66, 2.86, niveau: 1)
  # Le trait va de (x0,y0) à (x1,y1), l'épaisseur part vers la gauche du trait.
  # portes : [[distance depuis x0,y0, largeur], ...]
  def self.cloison(tg, x0, y0, x1, y1, portes: [], ep: EP_CL, niveau: 0)
    m = Sketchup.active_model
    z0 = niveau.zero? ? 0 : Z_ETAGE
    h  = niveau.zero? ? H_RDC : H_ETAGE
    m.start_operation("Cloison", true)
    g = mur(racine, "Cloison #{tg}", tg, x0, y0, x1, y1, z0, h, ep,
            portes.map { |s, w| [s, w, 0, PORTE_H] }, mat("Cloison neuve", [216, 90, 48]))
    m.commit_operation
    g
  end
end

if defined?(Sketchup)
  ADFPlan.construire
else
  require "json"
  puts JSON.generate(murs: ADFPlan::MURS, dalles: ADFPlan::DALLES, textes: ADFPlan::TEXTES)
end
