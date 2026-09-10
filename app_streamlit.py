# =========================================================
#  INTERFAZ CON STREAMLIT — SIMULADOR DE COMUNIDAD ENERGÉTICA
# =========================================================
#
#  Cómo usarla:
#      1. Instalar una sola vez:   pip install streamlit
#      2. Dejar este archivo junto a simulador_ce.py
#      3. Correr:                  streamlit run app_streamlit.py
#      4. Se abre solo en el navegador
#
#  IMPORTANTE: aquí NO se calcula nada. Toda la matemática vive en
#  simulador_ce.py; este archivo solo pide los datos, llama a esas
#  funciones y muestra el resultado. Si cambias una fórmula allá,
#  esta interfaz cambia sola.
#
#  Para entender Streamlit basta con saber tres cosas:
#      st.number_input(...)  ->  una casilla para escribir un número
#      st.metric(...)        ->  un número grande destacado
#      st.dataframe(...)     ->  una tabla
#  Todo lo demás es Python normal.
# =========================================================

import os
import importlib.util
import pandas as pd
import streamlit as st

# --- Cargar el modelo desde la carpeta de este archivo ---------------------
AQUI = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "simulador_ce", os.path.join(AQUI, "simulador_ce.py"))
sim = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sim)


# --- Formato colombiano ----------------------------------------------------

def cop(v, d=0):
    return "$ " + f"{v:,.{d}f}".replace(",", "@").replace(".", ",").replace("@", ".")


def pct(v, d=2):
    return f"{v * 100:,.{d}f}".replace(",", "@").replace(".", ",").replace("@", ".") + " %"


def num(v, d=0):
    return f"{v:,.{d}f}".replace(",", "@").replace(".", ",").replace("@", ".")


def esc(texto):
    """Streamlit lee $...$ como fórmula matemática. Hay que escapar el peso."""
    return texto.replace("$", "\\$")


# =========================================================
# LA PÁGINA
# =========================================================

st.set_page_config(page_title="Simulador · Comunidad Energética",
                   page_icon="⚡", layout="wide")

st.title("Simulador de ingreso · Comunidad Energética")
st.caption("Estimador de ahorro para un usuario que quiere entrar a la comunidad")


# --- Los datos que pide, todos de su factura ------------------------------
with st.sidebar:
    st.header("Datos de su factura")

    cu = st.number_input("Costo unitario CU (COP/kWh)",
                         min_value=1.0, max_value=5000.0, value=915.0, step=1.0,
                         help="El valor por kWh de su factura, antes de contribución")

    cv = st.number_input("Componente Cv (COP/kWh)",
                         min_value=0.0, max_value=5000.0, value=130.0, step=1.0,
                         help="Comercialización. Ya está dentro del CU; el comercializador "
                              "lo cobra por cada kWh permutado (Art. 26)")

    contribuye = st.checkbox("Paga contribución del 20 %", value=True,
                             help="Sí: estratos 5 y 6, comerciales. "
                                  "No: industriales exentos por CIIU (Ley 1430/2010)")

    consumo = st.number_input("Consumo promedio mensual (kWh)",
                              min_value=1.0, value=15000.0, step=100.0,
                              help="Promedio de los últimos 6 a 12 meses")

    cu_ce = st.number_input("Precio acordado con la CE (COP/kWh)",
                            min_value=1.0, value=693.5, step=1.0,
                            help="El precio al que la comunidad le venderá el kWh")

    anios = st.number_input("Período de análisis (años)",
                            min_value=1, max_value=25, value=5, step=1)

    st.divider()
    st.caption(f"Planta: {num(sim.GENERACION_MENSUAL_KWH)} kWh/mes  ·  "
               f"{len(sim.USUARIOS_BASE)} miembros actuales")


contrib = sim.CONTRIBUCION if contribuye else 0.0

# --- Validaciones de entrada ----------------------------------------------
if cv > cu:
    st.error("El Cv no puede ser mayor que el CU.")
    st.stop()

umb = sim.umbrales_precio(cu, cv, contrib)
au = sim.ahorro_unitario_tipo1(cu, cv, cu_ce, contrib)

if cu_ce >= umb["techo_absoluto"]:
    st.error(esc(f"Con un precio de {cop(cu_ce, 2)} por kWh el usuario **NO ahorra nada**. "
                 f"El CU_CE tendría que bajar de {cop(umb['techo_absoluto'], 2)}."))
    st.stop()


# --- El reparto: se recalculan TODOS los PDE incluyendo al nuevo -----------
usuarios = [dict(u) for u in sim.USUARIOS_BASE] + [
    {"contrato": "NUEVO", "promedio": consumo, "pde_actual": None}]

try:
    pdes, lam, topados = sim.repartir_por_consumo([u["promedio"] for u in usuarios])
except ValueError as e:
    st.error(str(e))
    st.stop()

pde_nuevo = pdes[-1]
r = sim.balance_mensual(consumo, pde_nuevo, cu, cv, cu_ce, contrib)

# Escenario máximo: el techo propio del usuario
pde_max = min(sim.PDE_MAXIMO_LEGAL,
              sim.TOPE_CONSUMO * consumo / sim.GENERACION_MENSUAL_KWH)
r_max = sim.balance_mensual(consumo, pde_max, cu, cv, cu_ce, contrib)


# =========================================================
# 1. EL AHORRO
# =========================================================
st.subheader("Su ahorro estimado")

c1, c2 = st.columns(2)
with c1:
    st.metric("Esperado", cop(r["ahorro_mes"]) + " / mes",
              f"{cop(r['ahorro_anual'])} al año".replace("$ ", ""), delta_color="off")
    st.caption(f"{pct(r['ahorro_pct'])} de su factura  ·  "
               f"{num(r['asignada'])} kWh/mes  ·  PDE {pct(pde_nuevo, 3)}")
with c2:
    st.metric("Máximo", cop(r_max["ahorro_mes"]) + " / mes",
              f"{cop(r_max['ahorro_anual'])} al año".replace("$ ", ""), delta_color="off")
    st.caption(f"{pct(r_max['ahorro_pct'])} de su factura  ·  "
               f"{num(r_max['asignada'])} kWh/mes  ·  PDE {pct(pde_max, 3)}")

st.info(
    f"**Esperado:** lo que le tocaría hoy, porque la planta se reparte entre todos los "
    f"miembros — hoy la cobertura común es {pct(lam * sim.GENERACION_MENSUAL_KWH, 1)} "
    f"del consumo de cada uno.  \n"
    f"**Máximo:** su techo propio, el {pct(sim.TOPE_CONSUMO, 0)} de su consumo "
    f"(o el {pct(sim.PDE_MAXIMO_LEGAL, 1)} legal si ese muerde primero). "
    f"Solo lo alcanzaría si la comunidad tuviera energía de sobra.")


# =========================================================
# 2. DE DÓNDE SALE EL AHORRO
# =========================================================
st.subheader("De dónde sale el ahorro")

c1, c2 = st.columns(2)

with c1:
    st.markdown("**Por cada kWh que entrega la comunidad**")
    st.dataframe(pd.DataFrame([
        {"Concepto": "Lo que ese kWh le cuesta hoy en la red", "Valor": cop(au["costo_red"], 2)},
        {"Concepto": "Ahorro por tarifa (CU − Cv − CU_CE)",    "Valor": cop(au["por_tarifa"], 2)},
        {"Concepto": "Ahorro por contribución evitada",        "Valor": cop(au["por_contribucion"], 2)},
        {"Concepto": "AHORRO POR kWh",                         "Valor": cop(au["total"], 2)},
    ]), hide_index=True, use_container_width=True)
    st.caption(f"Descuento efectivo sobre el costo real del kWh: **{pct(au['descuento_efectivo'])}**. "
               f"No es lo mismo que el ahorro de la factura: la comunidad solo cubre "
               f"{pct(r['cobertura'], 1)} de su consumo.")

with c2:
    st.markdown("**Su factura, antes y después**")
    st.dataframe(pd.DataFrame([
        {"Concepto": f"SIN comunidad ({num(consumo)} kWh a la red)", "Valor": cop(r["factura_sin"])},
        {"Concepto": f"Energía de la red ({num(r['energia_red'])} kWh)", "Valor": cop(r["pago_red"])},
        {"Concepto": f"Cargo Cv sobre lo permutado ({num(r['exc1'])} kWh)", "Valor": cop(r["cargo_cv"])},
        {"Concepto": f"Pago a la comunidad ({num(r['asignada'])} kWh)", "Valor": cop(r["pago_ce"])},
        {"Concepto": "CON comunidad", "Valor": cop(r["factura_con"])},
    ]), hide_index=True, use_container_width=True)
    st.caption(esc(f"Del ahorro mensual, {cop(r['exc1'] * au['por_contribucion'])} viene de la "
                   f"contribución evitada y {cop(r['exc1'] * au['por_tarifa'])} del diferencial tarifario."))


# =========================================================
# 3. EL REPARTO DEL PDE
# =========================================================
st.subheader("Reparto del PDE en la comunidad")

ok, hallazgos = sim.validar_comunidad(pdes, len(pdes))

if ok:
    st.success(f"Reparto válido: los PDE suman {pct(sum(pdes), 4)} y ninguno llega al 10 %.")
else:
    st.error(" ".join(h[1] for h in hallazgos if h[0] == "ERROR"))

for nivel, msg in hallazgos:
    if nivel == "AVISO" and "CAPACIDAD_INSTALADA" in msg:
        st.warning("Falta el dato de capacidad instalada de la planta: no se pudo verificar "
                   "el límite de 1 MW ni el de 100 kW por usuario. El reparto sí está validado.")
    elif nivel == "AVISO":
        st.warning(msg)

filas = []
for u, p in zip(usuarios, pdes):
    es_nuevo = u["pde_actual"] is None
    filas.append({
        "Contrato":  u["contrato"],
        "Consumo":   num(u["promedio"]),
        "PDE antes": "—" if es_nuevo else pct(u["pde_actual"], 3),
        "PDE nuevo": pct(p, 3),
        "Cambio":    "INGRESO" if es_nuevo else
                     ("+" if p > u["pde_actual"] else "") + pct(p - u["pde_actual"], 3),
        "kWh/mes":   num(sim.energia_asignada(p)),
        "Cobertura": pct(sim.energia_asignada(p) / u["promedio"], 1),
    })

st.dataframe(pd.DataFrame(filas), hide_index=True, use_container_width=True)
st.caption(f"Al entrar un usuario nuevo se recalculan todos los PDE. El reparto es "
           f"proporcional al consumo: todos quedan con la misma cobertura, salvo los "
           f"{len(topados)} que chocan contra su techo.")


# =========================================================
# 4. PROYECCIÓN
# =========================================================
st.subheader(f"Proyección a {anios} año(s)")

proy = sim.proyectar(consumo, pde_nuevo, cu, cv, cu_ce, contrib, int(anios))

st.dataframe(pd.DataFrame([{
    "Año":            p["anio"],
    "CU red":         cop(p["cu"], 2),
    "CU comunidad":   cop(p["cu_ce"], 2),
    "Ahorro del año": cop(p["ahorro_anual"]),
    "%":              pct(p["ahorro_pct"], 1),
    "Acumulado":      cop(p["acumulado"]),
} for p in proy]), hide_index=True, use_container_width=True)

st.line_chart(pd.DataFrame({"Ahorro acumulado": [p["acumulado"] for p in proy]},
                           index=[f"Año {p['anio']}" for p in proy]))

st.caption(f"Supuestos: la tarifa de red sube {pct(sim.INFLACION_RED_ANUAL, 1)} al año y el "
           f"precio de la comunidad {pct(sim.INFLACION_CE_ANUAL, 1)}. El PDE se mantiene. "
           f"El acumulado son pesos corrientes, sin traer a valor presente.")
