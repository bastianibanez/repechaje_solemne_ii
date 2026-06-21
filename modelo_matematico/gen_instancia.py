#!/usr/bin/env python3
# ============================================================
# Generador de instancias para modelo_caso2.mod
# Uso:
#   python gen_instancia.py N P Q Cq NCAUSAS SEED [out.dat]
#
#   N        = numero de reclusos
#   P        = numero de modulos
#   Q        = celdas por modulo   (|J| = P*Q)
#   Cq       = capacidad por celda
#   NCAUSAS  = numero de causas distintas
#   SEED     = semilla aleatoria (reproducible)
#
# Genera conflictos con densidad moderada y capacidad holgada
# para mantener la instancia FACTIBLE.
# ============================================================
import sys, random

def main():
    if len(sys.argv) < 7:
        print("uso: gen_instancia.py N P Q Cq NCAUSAS SEED [out.dat]")
        sys.exit(1)

    N   = int(sys.argv[1])
    P   = int(sys.argv[2])
    Q   = int(sys.argv[3])
    Cq  = int(sys.argv[4])
    NC  = int(sys.argv[5])
    SEED= int(sys.argv[6])
    out = sys.argv[7] if len(sys.argv) > 7 and not sys.argv[7].replace('.','',1).isdigit() else None
    # densidades opcionales (grado promedio de pares por recluso)
    G_TAT  = float(sys.argv[8]) if len(sys.argv) > 8 else 1.2
    G_COMP = float(sys.argv[9]) if len(sys.argv) > 9 else 1.0

    J = P * Q
    rnd = random.Random(SEED)

    reclusos = list(range(1, N + 1))
    celdas   = list(range(1, J + 1))
    causas   = [f"CAU{c}" for c in range(1, NC + 1)]

    # ---- causas por recluso: 1 a 2 causas c/u ----
    # se limita la frecuencia de cada causa para no exigir mas celdas que J
    max_por_causa = J            # ninguna causa puede aparecer mas que # celdas
    cuenta = {c: 0 for c in causas}
    b = {r: set() for r in reclusos}
    for r in reclusos:
        k = rnd.randint(1, 2)
        opciones = [c for c in causas if cuenta[c] < max_por_causa]
        rnd.shuffle(opciones)
        for c in opciones[:k]:
            b[r].add(c)
            cuenta[c] += 1

    # ---- pares de conflicto (r < r') con densidad controlada ----
    # densidad como fraccion de N (no de N^2) -> grado promedio acotado
    def pares(grado_prom):
        objetivo = int(grado_prom * N / 2)
        s = set()
        intentos = 0
        while len(s) < objetivo and intentos < objetivo * 50:
            a = rnd.randint(1, N); c = rnd.randint(1, N)
            intentos += 1
            if a == c:
                continue
            par = (min(a, c), max(a, c))
            s.add(par)
        return sorted(s)

    tatuajes   = pares(G_TAT)    # grado promedio de pares por tatuajes
    companeros = pares(G_COMP)   # grado promedio de pares por companeros

    # ---- emitir .dat ----
    L = []
    L.append(f"# Instancia generada: N={N} P={P} Q={Q} (|J|={J}) Cq={Cq} "
             f"NCAUSAS={NC} SEED={SEED}")
    L.append(f"# capacidad total = {J*Cq}  (reclusos = {N})")
    L.append(f"# pares tatuaje = {len(tatuajes)}  pares companeros = {len(companeros)}")
    L.append("")
    L.append("set R := " + " ".join(map(str, reclusos)) + " ;")
    L.append("set J := " + " ".join(map(str, celdas)) + " ;")
    L.append("set C := " + " ".join(causas) + " ;")
    L.append("")
    L.append(f"param Cap default {Cq} ;")
    L.append("")
    # tabla b transpuesta
    L.append("param b : " + " ".join(causas) + " :=")
    for r in reclusos:
        fila = " ".join("1" if c in b[r] else "0" for c in causas)
        L.append(f" {r:>3} {fila}")
    L.append(";")
    L.append("")
    L.append("set P_TAT :=")
    L.append("  " + " ".join(f"({a},{c})" for a, c in tatuajes))
    L.append(";")
    L.append("")
    L.append("set K_COMP :=")
    L.append("  " + " ".join(f"({a},{c})" for a, c in companeros))
    L.append(";")
    txt = "\n".join(L) + "\n"

    if out:
        with open(out, "w") as f:
            f.write(txt)
        print(f"escrito {out}")
    else:
        sys.stdout.write(txt)

if __name__ == "__main__":
    main()
