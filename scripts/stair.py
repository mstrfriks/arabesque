"""Escalier béton quart tournant (principe, à relever) : géométrie en m, repère plan."""
FOOT = [(.3, 2.3), (1.2, 2.3), (1.2, 3.1), (1.95, 3.1), (1.95, 4.0), (.3, 4.0)]
PIV = (1.2, 3.1)
def treads():
    t = [((.3, y), (1.2, y)) for y in (2.55, 2.8)]                         # volée 1 (monte vers le nord)
    t += [(PIV, (.3, 3.1)), (PIV, (.3, 3.45)), (PIV, (.3, 3.8)), (PIV, (.55, 4.0)), (PIV, (.9, 4.0)), (PIV, (1.2, 4.0))]  # balancement
    t += [((x, 3.1), (x, 4.0)) for x in (1.45, 1.7)]                      # volée 2 (vers l'est)
    return t
ARROW = [(.75, 2.4), (.75, 3.55), (1.85, 3.55)]
CUT = [(.3, 2.95), (.62, 2.95), (.72, 3.04), (.82, 2.86), (.92, 2.95), (1.2, 2.95)]
