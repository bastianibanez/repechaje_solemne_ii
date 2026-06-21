#!/usr/bin/env python3
# Barrido de tamanos: genera instancia, corre AMPL/CPLEX, cronometra.
import subprocess, time, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
AMPL = "/Users/bastianibanez/sem1-2026/optimizacion/ampl_env/lib/python3.12/site-packages/ampl_module_base/bin/ampl"

# (N, P, Q, Cq, NCAUSAS, SEED, G_TAT, G_COMP)
# capacidad apretada (|J|*Cq apenas > N) + conflictos densos -> MILP no trivial
# caps APRETADA (|J|*Cq ~ 1.1*N) + densidad alta -> conflictos obligan Z>ceil(N/Cq)
CONFIGS = [
    (400, 28, 4, 4, 12, 1, 3.0, 2.5),
    (500, 35, 4, 4, 14, 1, 3.0, 2.5),
    (600, 42, 4, 4, 16, 1, 3.5, 3.0),
    (700, 49, 4, 4, 18, 1, 3.5, 3.0),
    (800, 56, 4, 4, 20, 1, 4.0, 3.5),
]

def run(cfg):
    N,P,Q,Cq,NC,SEED,GT,GC = cfg
    dat = os.path.join(HERE, "bench_tmp.dat")
    subprocess.run([sys.executable, os.path.join(HERE,"gen_instancia.py"),
                    str(N),str(P),str(Q),str(Cq),str(NC),str(SEED),dat,str(GT),str(GC)],
                   check=True, capture_output=True)
    run_txt = f"""reset;
model {HERE}/modelo_caso2.mod;
data {dat};
option solver cplex;
option cplex_options 'timelimit=30';
solve;
printf "ZZZ %d\\n", Z;
printf "STAT %s\\n", solve_result;
"""
    runf = os.path.join(HERE, "bench_tmp.run")
    open(runf,"w").write(run_txt)
    t0 = time.time()
    r = subprocess.run([AMPL, runf], capture_output=True, text=True)
    dt = time.time() - t0
    out = r.stdout + r.stderr
    z = re.search(r"ZZZ (\d+)", out)
    st = re.search(r"STAT (\S+)", out)
    z = z.group(1) if z else "?"
    st = st.group(1) if st else "?"
    return dt, z, st, out

print(f"{'N':>4} {'PxQ':>7} {'|J|':>4} {'Cq':>3} {'caps':>5} {'Z':>4} {'estado':>10} {'seg':>7}")
for cfg in CONFIGS:
    N,P,Q,Cq,NC,SEED,GT,GC = cfg
    J = P*Q
    dt,z,st,out = run(cfg)
    print(f"{N:>4} {f'{P}x{Q}':>7} {J:>4} {Cq:>3} {J*Cq:>5} {z:>4} {st:>10} {dt:>7.2f}")
    if dt > 12:
        print("   (supera ~10s, freno barrido)")
        break

# limpieza
for f in ["bench_tmp.dat","bench_tmp.run"]:
    p = os.path.join(HERE,f)
    if os.path.exists(p): os.remove(p)
