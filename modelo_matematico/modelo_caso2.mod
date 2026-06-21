# ============================================================
# Caso 2: Reasignacion Penitenciaria
# Modelo de optimizacion (MILP) -- AMPL / CPLEX
#
# Traduce 1:1 el modelo matematico de modelo_caso2.tex
# Objetivo: minimizar el numero de celdas utilizadas
#           respetando separaciones por causa, companeros
#           de celda de origen y tatuajes similares (>=70%).
# ============================================================

# ------------------------------------------------------------
# CONJUNTOS
# ------------------------------------------------------------
set R;                       # Reclusos
set J;                       # Celdas  (J = {1,...,P*Q})
set C;                       # Causas judiciales

# Pares en conflicto, almacenados con r < r' para no duplicar.
set P_TAT within {R,R};      # Pares con tatuajes similares >= 70%   (conjunto P del .tex)
set K_COMP within {R,R};     # Pares que fueron companeros de celda   (conjunto K del .tex)

# ------------------------------------------------------------
# PARAMETROS
# ------------------------------------------------------------
param Cap {J} >= 0 integer;          # Capacidad maxima de la celda j  (Cq)
param b {R,C} binary, default 0;     # b[r,c] = 1 si el recluso r tiene la causa c

# ------------------------------------------------------------
# VARIABLES DE DECISION
# ------------------------------------------------------------
var x {R,J} binary;          # 1 si el recluso r va en la celda j
var y {J}   binary;          # 1 si se utiliza la celda j

# ------------------------------------------------------------
# FUNCION OBJETIVO
# ------------------------------------------------------------
minimize Z:
    sum {j in J} y[j];

# ------------------------------------------------------------
# RESTRICCIONES
# ------------------------------------------------------------

# (1) Cada recluso es asignado a exactamente una celda.
s.t. Asignacion {r in R}:
    sum {j in J} x[r,j] = 1;

# (2) Capacidad de la celda y activacion de la variable y_j.
#     Si y_j = 0 la celda queda vacia; si y_j = 1 admite hasta Cap_j.
s.t. Capacidad {j in J}:
    sum {r in R} x[r,j] <= Cap[j] * y[j];

# (3) Companeros de celda de origen no pueden volver a coincidir.
s.t. Companeros {(r,rp) in K_COMP, j in J}:
    x[r,j] + x[rp,j] <= 1;

# (4) Dos reclusos con la misma causa no comparten celda.
s.t. Causas {c in C, j in J}:
    sum {r in R} b[r,c] * x[r,j] <= 1;

# (5) Reclusos con tatuajes similares (>=70%) quedan separados.
s.t. Tatuajes {(r,rp) in P_TAT, j in J}:
    x[r,j] + x[rp,j] <= 1;
