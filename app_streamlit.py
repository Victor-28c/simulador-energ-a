# =========================================================
#  INTERFAZ CON STREAMLIT — WE POWER
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


def millones(v):
    return "$ " + f"{v / 1_000_000:,.1f}".replace(".", ",") + " M"


# =========================================================
# LOS PLANES
# =========================================================
#  Un plan es una COBERTURA: qué parte del consumo del usuario pone
#  WE Power. El PDE sale de ahí, no al revés — así el usuario compara en
#  el idioma que entiende y los planes nunca se invierten entre sí.
#
#  Básico 30 %   equivale a un PDE del 3 % para un usuario de 15.000 kWh/mes,
#                que es el tamaño típico de los miembros de hoy.
#  Estándar 80 % es el TOPE_CONSUMO del modelo: el máximo estable por usuario.
#  Premium 100 % solo es alcanzable por debajo de 14.850 kWh/mes; por encima
#                de eso el tope legal del 9,9 % muerde antes y la cobertura
#                real baja sola.

PLAN_BASICO = 0.30
PLAN_ESTANDAR = sim.TOPE_CONSUMO      # 0,80
PLAN_PREMIUM = 1.00


def pde_del_plan(cobertura_objetivo, consumo):
    """Traduce 'quiero cubrir X % de mi consumo' a un PDE legal."""
    return min(sim.PDE_MAXIMO_LEGAL,
               cobertura_objetivo * consumo / sim.GENERACION_MENSUAL_KWH)


# =========================================================
# LOS TEXTOS DE AYUDA  (el "?" de cada elemento)
# =========================================================

AYUDA = {
    "factura":
        "El total de tu última factura de energía. Si no la tienes a mano, "
        "un estimado sirve.",

    "consumo":
        "Tu consumo promedio de los últimos 6 a 12 meses.",

    "ahorro":
        "Lo que dejarías de pagar cada mes con el plan Estándar. Es tu factura "
        "de hoy menos lo que pagarías con WE Power.",

    "antes":
        "Lo que pagas hoy: todo tu consumo comprado a la red, con la "
        "contribución del 20 % incluida.",

    "despues":
        "Tu nueva factura: lo que le sigues comprando a la red, más el cargo "
        "del comercializador por la energía permutada, más lo que le pagas a "
        "WE Power.",

    "kwh":
        "El kWh de la red te cuesta el precio de la energía más el 20 % de "
        "contribución. El que pone WE Power no paga contribución y se te vende "
        "más barato: solo pagas el cargo del comercializador y el precio "
        "acordado.",

    "basico":
        "Ponemos alrededor de un tercio de tu energía."
        "es el minimo posible",

    "estandar":
        "Es el 80 % de tu consumo.",

    "premium":
        "Ponemos hasta el 100% de tu consumo (sujeto a la disponibilidad de la generación de la planta). "
        "Límite de Reparto (PDE): Máximo de 9.9%",

    "cu":
        "El valor por kWh de tu factura, antes de contribución.",

    "cv":
        "Comercialización. Ya está dentro del CU. El comercializador lo cobra "
        "por cada kWh permutado (Art. 26, Res. CREG 174/2021).",

    "contribuye":
        "Sí: estratos 5 y 6 y comerciales. No: industriales exentos por código "
        "CIIU (Ley 1430/2010, art. 2).",

    "cu_ce":
        "El precio al que WE Power te vende el kWh. Es lo que se negocia.",

    "anios":
        "Para la proyección. Se asume que la tarifa de red sube más rápido que "
        "el precio de WE Power, así que la brecha se abre con los años.",

    "pde":
        "Porcentaje de Distribución de Excedentes: la tajada de la generación "
        "de la planta que te corresponde. Los PDE de todos los miembros suman "
        "100 % y ninguno puede llegar al 10 % (Art. 20 num. 1, Res. CREG "
        "101 072 de 2025).",
}


# =========================================================
# LA PÁGINA
# =========================================================

st.set_page_config(page_title="WE Power · Ahorra en tu factura",
                   page_icon="⚡", layout="centered")

st.markdown("""
<style>
  .etiqueta  { font-size: .75rem; letter-spacing: .08em; text-transform: uppercase;
               color: #2E7D32; font-weight: 700; margin-bottom: .2rem; }
  .etiqueta-gris { font-size: .75rem; letter-spacing: .08em; text-transform: uppercase;
               color: #888; font-weight: 700; margin-bottom: .2rem; }
  .pilar     { font-size: .92rem; color: #444; }
  /* Imita el st.caption, pero admite HTML: lo necesitamos para el <abbr>. */
  .nota      { font-size: .875rem; color: rgba(49,51,63,.6); margin-top: -.5rem; }
  .nota abbr { text-decoration: underline dotted; cursor: help; }
  /* Las tarjetas de los planes son angostas: el número se corta con el
     tamaño que Streamlit le pone por defecto a st.metric. */
  div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMetricValue"] {
      font-size: 1.5rem;
  }
</style>
""", unsafe_allow_html=True)


# =========================================================
# SUPUESTOS  (lo técnico, fuera del camino)
# =========================================================

with st.sidebar:
    st.header("Ajustar supuestos")
    st.caption("Vienen con los valores de WE Power. Solo tócalos si sabes lo "
               "que estás cambiando.")

    cu = st.number_input("Costo unitario CU (COP/kWh)",
                         min_value=1.0, max_value=5000.0, value=915.0, step=1.0,
                         help=AYUDA["cu"])

    cv = st.number_input("Componente Cv (COP/kWh)",
                         min_value=0.0, max_value=5000.0, value=130.0, step=1.0,
                         help=AYUDA["cv"])

    contribuye = st.checkbox("Paga contribución del 20 %", value=True,
                             help=AYUDA["contribuye"])

    cu_ce = st.number_input("Precio acordado con WE Power (COP/kWh)",
                            min_value=1.0, value=693.5, step=1.0,
                            help=AYUDA["cu_ce"])

    anios = st.number_input("Período de proyección (años)",
                            min_value=1, max_value=25, value=5, step=1,
                            help=AYUDA["anios"])

    st.divider()
    st.caption(f"Planta: {num(sim.GENERACION_MENSUAL_KWH)} kWh/mes  ·  "
               f"{len(sim.USUARIOS_BASE)} miembros actuales")

contrib = sim.CONTRIBUCION if contribuye else 0.0


# =========================================================
# BLOQUE 1 — HERO
# =========================================================

st.title("Ahorra en tu factura con WE Power")
st.subheader("sin instalar un solo panel.")

por_kwh = st.toggle("Prefiero escribir mi consumo en kWh",
                    help="Por defecto te pedimos la factura porque es el número "
                         "que todo el mundo se sabe. El consumo se deduce solo.")

if por_kwh:
    consumo = st.number_input("¿Cuánto consumes al mes? (kWh)",
                              min_value=1.0, value=15000.0, step=100.0,
                              help=AYUDA["consumo"])
    factura_mes = consumo * cu * (1 + contrib)
    st.caption(esc(f"Eso equivale a una factura de unos {cop(factura_mes)} al mes."))
else:
    factura_mes = st.number_input("¿Cuánto pagas de luz al mes?",
                                  min_value=1000.0, value=16_470_000.0,
                                  step=100_000.0, format="%.0f",
                                  help=AYUDA["factura"])
    consumo = factura_mes / (cu * (1 + contrib))
    st.caption(f"Eso son unos {num(consumo)} kWh al mes.")

st.caption("✓ Sin inversión  ·  ✓ Sin obra  ·  ✓ Sigues con tu mismo comercializador")


# --- Validaciones ----------------------------------------------------------
if cv > cu:
    st.error("El Cv no puede ser mayor que el CU. Revisa los supuestos.")
    st.stop()

umb = sim.umbrales_precio(cu, cv, contrib)
au = sim.ahorro_unitario_tipo1(cu, cv, cu_ce, contrib)

if cu_ce >= umb["techo_absoluto"]:
    st.error(esc(f"Con un precio de {cop(cu_ce, 2)} por kWh no habría ahorro. "
                 f"El precio tendría que bajar de {cop(umb['techo_absoluto'], 2)}."))
    st.stop()


# --- Los tres planes, calculados ------------------------------------------
pde_bas = pde_del_plan(PLAN_BASICO, consumo)
pde_est = pde_del_plan(PLAN_ESTANDAR, consumo)
pde_pre = pde_del_plan(PLAN_PREMIUM, consumo)

r_bas = sim.balance_mensual(consumo, pde_bas, cu, cv, cu_ce, contrib)
r_est = sim.balance_mensual(consumo, pde_est, cu, cv, cu_ce, contrib)
r_pre = sim.balance_mensual(consumo, pde_pre, cu, cv, cu_ce, contrib)

#  El Estándar es el plan por defecto: alimenta el número grande y el
#  antes/después.
r = r_est
pde_actual = pde_est


# =========================================================
# BLOQUE 2 — EL NÚMERO
# =========================================================

st.divider()

c1, c2 = st.columns([3, 2])
with c1:
    st.metric("Tu ahorro estimado",
              cop(r["ahorro_mes"]) + " / mes",
              f"{cop(r['ahorro_anual'])} al año".replace("$ ", ""),
              delta_color="off", help=AYUDA["ahorro"])
with c2:
    st.metric("De tu factura", pct(r["ahorro_pct"], 1),
              help="Cuánto baja tu factura en porcentaje.")

st.progress(min(1.0, r["cobertura"]))
st.markdown(
    f"<div class='nota'>Con el <b>plan Estándar</b>: ponemos el "
    f"<b>{pct(r['cobertura'], 0)}</b> de tu energía, con un "
    f"<abbr title=\"{AYUDA['pde']}\">PDE</abbr> del <b>{pct(pde_actual, 2)}</b> "
    f"de nuestra generación. El resto sigue viniendo de la red.</div>",
    unsafe_allow_html=True)

st.info(f"**Es un estimado.** Está calculado con un consumo promedio de "
        f"{num(consumo)} kWh al mes. Tu consumo cambia mes a mes y tu ahorro "
        f"también: en un mes que consumas más, ahorras más; en uno que consumas "
        f"menos, ahorras menos.")


# =========================================================
# BLOQUE 3 — TU FACTURA, ANTES Y DESPUÉS
# =========================================================

st.divider()
st.subheader("Tu factura, antes y después")

a1, a2 = st.columns(2)
with a1:
    st.metric("Antes pagabas", cop(r["factura_sin"]), help=AYUDA["antes"])
    st.caption(f"Le comprabas a la red los {num(consumo)} kWh que consumes.")
with a2:
    #  El guion tiene que ser ASCII: Streamlit lo usa para saber que el delta
    #  es negativo. Con delta_color="inverse", bajar la factura sale en verde.
    st.metric("Ahora pagas", cop(r["factura_con"]),
              "-" + cop(r["ahorro_mes"]).replace("$ ", ""),
              delta_color="inverse", help=AYUDA["despues"])
    st.caption(f"Nosotros ponemos {num(r['asignada'])} kWh; el resto se lo "
               f"sigues comprando a la red.")

st.markdown("**¿De qué se compone la nueva factura?**")
st.dataframe(pd.DataFrame([
    {"Concepto": f"Energía que le sigues comprando a la red ({num(r['energia_red'])} kWh)",
     "Valor": cop(r["pago_red"])},
    {"Concepto": f"Cargo del comercializador por la energía que pusimos ({num(r['exc1'])} kWh)",
     "Valor": cop(r["cargo_cv"])},
    {"Concepto": f"Lo que le pagas a WE Power ({num(r['asignada'])} kWh)",
     "Valor": cop(r["pago_ce"])},
    {"Concepto": "TOTAL DE TU NUEVA FACTURA", "Valor": cop(r["factura_con"])},
]), hide_index=True, width='stretch')

st.caption(esc(f"Antes: {cop(r['factura_sin'])}.  Ahora: {cop(r['factura_con'])}.  "
               f"Te quedan {cop(r['ahorro_mes'])} en el bolsillo cada mes, "
               f"{cop(r['ahorro_anual'])} al año."))


# =========================================================
# BLOQUE 4 — POR CADA kWh
# =========================================================

st.divider()
st.subheader("Por cada kWh que te entregamos")

k1, k2, k3 = st.columns(3)
with k1:
    st.metric("Ese kWh en la red", cop(au["costo_red"], 2), help=AYUDA["kwh"])
    st.caption("Precio de la energía más el 20 % de contribución.")
with k2:
    st.metric("Ese kWh con WE Power", cop(cv + cu_ce, 2))
    st.caption("No paga contribución, y te lo vendemos más barato.")
with k3:
    st.metric("Te ahorras", cop(au["total"], 2),
              pct(au["descuento_efectivo"], 1) + " menos", delta_color="off")
    st.caption("En cada kWh que ponemos nosotros.")

st.caption(f"Tu factura no baja ese mismo {pct(au['descuento_efectivo'], 0)} porque "
           f"el descuento aplica solo a los kWh que ponemos nosotros, que son el "
           f"{pct(r['cobertura'], 0)} de tu consumo: "
           f"{pct(au['descuento_efectivo'], 0)} × {pct(r['cobertura'], 0)} = "
           f"{pct(r['ahorro_pct'], 1)} de tu factura.")


# =========================================================
# BLOQUE 5 — LOS PLANES
# =========================================================

st.divider()
st.subheader("Ahorros posibles")
st.caption("Lo único que cambia entre los tres es cuánta de tu energía ponemos "
           "nosotros. El descuento por kWh es el mismo en los tres.")

p1, p2, p3 = st.columns(3)

PLANES = [
    (p1, "Básico", r_bas, AYUDA["basico"], False, "Siempre disponible."),
    (p2, "Estándar", r_est, AYUDA["estandar"], True, "El más pedido."),
    (p3, "Premium", r_pre, AYUDA["premium"], False, "Cupo limitado."),
]

for col, nombre, res, ayuda, destacado, pie in PLANES:
    with col:
        with st.container(border=True):
            st.metric(nombre, cop(res["ahorro_mes"]), help=ayuda)
            st.caption(esc(f"al mes  ·  {millones(res['ahorro_anual'])} al año  ·  "
                           f"{pct(res['ahorro_pct'], 1)} de tu factura"))
            st.progress(min(1.0, res["cobertura"]))
            st.caption(f"Ponemos el {pct(res['cobertura'], 0)} de tu energía")
            st.caption(f":gray[{pie}]")

st.info("**¿Te interesa el plan Premium?**  "
        "**Comunícate con nosotros** y lo revisamos contigo.")

#  Avisos honestos cuando un plan no puede dar lo que promete. Ningún usuario
#  puede recibir más de 14.850 kWh/mes (el 9,9 % de la generación), así que por
#  encima de cierto consumo los planes se van igualando entre sí.
TOPE_KWH = sim.PDE_MAXIMO_LEGAL * sim.GENERACION_MENSUAL_KWH

if abs(pde_bas - pde_pre) < 1e-9:
    st.warning(f"Tu consumo es tan alto frente a la planta que los tres planes "
               f"te dan lo mismo: la ley no permite asignarle a un solo usuario "
               f"más de {num(TOPE_KWH)} kWh al mes, que es el "
               f"{pct(r_pre['cobertura'], 0)} de lo que consumes. "
               f"**Comunícate con nosotros** para revisar tu caso.")
elif abs(pde_est - pde_pre) < 1e-9:
    st.caption(f"Con tu consumo, los planes Estándar y Premium te dan lo mismo: "
               f"ambos chocan con el tope legal de {num(TOPE_KWH)} kWh al mes "
               f"por usuario.")
elif r_pre["cobertura"] < 0.995:
    st.caption(f"Con tu consumo el Premium no alcanza a cubrir el 100 %: el tope "
               f"legal de {num(TOPE_KWH)} kWh al mes por usuario limita tu "
               f"asignación al {pct(r_pre['cobertura'], 0)} de lo que consumes.")


# =========================================================
# BLOQUE 6 — DE DÓNDE SALE
# =========================================================

st.divider()
st.subheader("¿De dónde sale el ahorro?")

q1, q2, q3 = st.columns(3)
with q1:
    st.markdown("**⚡ Energía más barata**")
    st.markdown("<div class='pilar'>Te vendemos el kWh por debajo de lo que te "
                "cobra la red.</div>", unsafe_allow_html=True)
with q2:
    st.markdown("**🧾 Sin contribución**")
    st.markdown("<div class='pilar'>Los kWh que te entregamos no pagan el 20 % "
                "de contribución de solidaridad.</div>", unsafe_allow_html=True)
with q3:
    st.markdown("**📄 Tu factura de siempre**")
    st.markdown("<div class='pilar'>El comercializador te descuenta la energía "
                "que pusimos nosotros. No cambias de operador.</div>",
                unsafe_allow_html=True)


# =========================================================
# BLOQUE 7 — CONFIANZA
# =========================================================

st.divider()
st.caption(f"{len(sim.USUARIOS_BASE)} miembros activos  ·  "
           f"{num(sim.GENERACION_ANUAL_KWH)} kWh/año  ·  100 % solar  ·  "
           f"Amparado por las Resoluciones CREG 174 de 2021 y 101 072 de 2025.")


# =========================================================
# BLOQUE 8 — PROYECCIÓN
# =========================================================
#  Se quitaron la tabla de reparto por contrato y la tabla de escenarios en
#  PDE: son asuntos de la comunidad, no del usuario que está decidiendo.

with st.expander("Ver cómo crece tu ahorro con los años"):

    st.caption(f"Con el plan Estándar. La tarifa de red sube "
               f"{pct(sim.INFLACION_RED_ANUAL, 1)} al año y el precio de WE Power "
               f"{pct(sim.INFLACION_CE_ANUAL, 1)}: como la red sube más rápido, "
               f"la brecha se abre y tu ahorro crece.")

    proy = sim.proyectar(consumo, pde_actual, cu, cv, cu_ce, contrib, int(anios))

    st.dataframe(pd.DataFrame([{
        "Año":               p["anio"],
        "Ahorro del año":    cop(p["ahorro_anual"]),
        "% de tu factura":   pct(p["ahorro_pct"], 1),
        "Ahorro acumulado":  cop(p["acumulado"]),
    } for p in proy]), hide_index=True, width='stretch')

    st.line_chart(pd.DataFrame({"Ahorro acumulado": [p["acumulado"] for p in proy]},
                               index=[f"Año {p['anio']}" for p in proy]))

    st.caption("El acumulado son pesos corrientes, sin traer a valor presente.")

st.caption(":gray[Estimación basada en tu consumo promedio y en las tarifas "
           "vigentes. El ahorro real depende de tu consumo mes a mes y de la "
           "tarifa de tu comercializador. No constituye una oferta vinculante.]")
