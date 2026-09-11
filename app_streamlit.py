# =========================================================
#  INTERFAZ CON STREAMLIT — SIMULADOR DE COMUNIDAD ENERGÉTICA
# =========================================================
#
#  Cómo usarla:
#      1. Instalar una sola vez:   pip install streamlit
#      2. Dejar este archivo junto a simulador_ce.py
#      3. Correr:                  streamlit run app_streamlit.py
#
#  IMPORTANTE: aquí NO se calcula nada. Toda la matemática vive en
#  simulador_ce.py; este archivo solo pide los datos, llama a esas
#  funciones y muestra el resultado.
#
#  La pantalla está partida en dos capas:
#      ARRIBA  -> lo que ve una persona común. Un solo dato de entrada,
#                 un número grande, tres escenarios. Cero jerga.
#      ABAJO   -> "Ver el detalle técnico", colapsado. Ahí vive todo lo
#                 que se necesita para sustentar el modelo.
#
#  Las explicaciones NO ocupan espacio: van en el signo de interrogación
#  de cada elemento (el parámetro help=). Se leen pasando el mouse.
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
    """Para las tarjetas: $ 32,9 M en vez de $ 32.888.363."""
    return "$ " + f"{v / 1_000_000:,.1f}".replace(".", ",") + " M"


# --- Regla de negocio que todavía vive aquí --------------------------------
# NOTA: esto es lógica regulatoria en la capa de presentación. Lo ideal es
# moverlo a simulador_ce.py como techo_individual(consumo). Se deja aquí
# mientras tanto para no tocar el modelo base.
PDE_PISO_CONSERVADOR = 0.03      # tajada más pequeña observada en la comunidad


def techo_individual(consumo):
    """El PDE más alto que puede recibir un usuario: el que muerda primero."""
    return min(sim.PDE_MAXIMO_LEGAL,
               sim.TOPE_CONSUMO * consumo / sim.GENERACION_MENSUAL_KWH)


# =========================================================
# LOS TEXTOS DE AYUDA  (el "?" de cada elemento)
# =========================================================
# Se agrupan aquí para poder ajustarlos sin buscar por todo el archivo.

AYUDA = {
    "factura":
        "El total de tu última factura de energía. Si no la tienes a mano, "
        "un estimado sirve.",

    "consumo":
        "Tu consumo promedio de los últimos 6 a 12 meses.",

    "ahorro":
        "Lo que dejarías de pagar cada mes. Es tu factura de hoy menos la suma "
        "de lo que le pagarías a la red por la energía que ella siga poniendo, "
        "más lo que le pagarías a la comunidad por la suya.",

    "cobertura":
        "Cuánta de tu energía pone la comunidad. El resto se lo sigues "
        "comprando a la red al precio de siempre. Por eso el ahorro de la "
        "factura es menor que el descuento por kWh.",

    "conservador":
        "El piso. Asume que la comunidad se llena de miembros y tu porción baja "
        "hasta la más pequeña que tiene alguien hoy. La regulación no fija un "
        "mínimo: este es el piso observado de esta comunidad.",

    "tucaso":
        "Lo que te tocaría si entraras este mes, con los miembros que hay hoy. "
        "La generación se reparte proporcional al consumo, así que todos quedan "
        "con la misma cobertura.",

    "optimo":
        "Tu techo: el 80 % de tu consumo, o el 9,9 % de la planta si ese muerde "
        "primero. Es lo máximo que la regulación y las reglas de la comunidad "
        "permiten asignarte.",

    "descuento":
        "Lo que te ahorras en cada kWh que te entrega la comunidad, comparado "
        "con lo que ese mismo kWh te cuesta hoy en la red con contribución "
        "incluida.",

    "cu":
        "El valor por kWh de tu factura, antes de contribución.",

    "cv":
        "Comercialización. Ya está dentro del CU. El comercializador lo cobra "
        "por cada kWh permutado (Art. 26, Res. CREG 174/2021).",

    "contribuye":
        "Sí: estratos 5 y 6 y comerciales. No: industriales exentos por código "
        "CIIU (Ley 1430/2010, art. 2).",

    "cu_ce":
        "El precio al que la comunidad te venderá el kWh. Es lo que se negocia.",

    "anios":
        "Para la proyección. Se asume que la tarifa de red sube más rápido que "
        "el precio de la comunidad, así que la brecha se abre con los años.",

    "pde":
        "Porcentaje de Distribución de Excedentes: la tajada de la generación de "
        "la planta que te corresponde. Los PDE de todos los miembros suman 100 % "
        "y ninguno puede llegar al 10 % (Art. 20 num. 1, Res. CREG 101 072/2025).",
}


# =========================================================
# LA PÁGINA
# =========================================================

st.set_page_config(page_title="WE Power · Ahorra en tu factura",
                   page_icon="⚡", layout="centered")

st.markdown("""
<style>
  .destacada { border: 2px solid #2E7D32 !important; }
  .etiqueta  { font-size: 0.75rem; letter-spacing: .08em; text-transform: uppercase;
               color: #2E7D32; font-weight: 700; margin-bottom: .2rem; }
  .etiqueta-gris { font-size: 0.75rem; letter-spacing: .08em; text-transform: uppercase;
               color: #888; font-weight: 700; margin-bottom: .2rem; }
  .grande    { font-size: 3.2rem; font-weight: 800; line-height: 1.05; margin: 0; }
  .bajo      { color: #666; margin-top: .2rem; }
  .pilar     { font-size: 0.92rem; color: #444; }
  /* Imita el st.caption, pero admite HTML: lo necesitamos para el <abbr>. */
  .nota      { font-size: 0.875rem; color: rgba(49,51,63,.6); margin-top: -.5rem; }
  .nota abbr { text-decoration: underline dotted; cursor: help; }
  /* Las tarjetas del rango son angostas: el número se corta con el tamaño
     que Streamlit le pone por defecto a st.metric. */
  div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMetricValue"] {
      font-size: 1.5rem;
  }
</style>
""", unsafe_allow_html=True)


# =========================================================
# SUPUESTOS  (todo lo técnico, fuera del camino)
# =========================================================

with st.sidebar:
    st.header("Ajustar supuestos")
    st.caption("Vienen con los valores de la comunidad. Solo tócalos si sabes "
               "lo que estás cambiando.")

    cu = st.number_input("Costo unitario CU (COP/kWh)",
                         min_value=1.0, max_value=5000.0, value=915.0, step=1.0,
                         help=AYUDA["cu"])

    cv = st.number_input("Componente Cv (COP/kWh)",
                         min_value=0.0, max_value=5000.0, value=130.0, step=1.0,
                         help=AYUDA["cv"])

    contribuye = st.checkbox("Paga contribución del 20 %", value=True,
                             help=AYUDA["contribuye"])

    cu_ce = st.number_input("Precio acordado con la CE (COP/kWh)",
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

#  El titular NO lleva porcentaje: cualquier cifra ahí arriba se lee como
#  promesa, y el ahorro depende del reparto. El número honesto aparece abajo,
#  ya calculado con los datos de quien pregunta.
st.title("Ahorra en tu factura con WE Power")

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



# --- Validaciones ----------------------------------------------------------
if cv > cu:
    st.error("El Cv no puede ser mayor que el CU. Revisa los supuestos.")
    st.stop()

umb = sim.umbrales_precio(cu, cv, contrib)
au = sim.ahorro_unitario_tipo1(cu, cv, cu_ce, contrib)

if cu_ce >= umb["techo_absoluto"]:
    st.error(esc(f"Con un precio de {cop(cu_ce, 2)} por kWh no habría ahorro. "
                 f"El precio de la comunidad tendría que bajar de "
                 f"{cop(umb['techo_absoluto'], 2)}."))
    st.stop()


# =========================================================
# LOS TRES ESCENARIOS
# =========================================================
#  Los tres son la MISMA función del modelo con tres PDE distintos.
#  Lo único que cambia entre ellos es la cobertura.

usuarios = [dict(u) for u in sim.USUARIOS_BASE] + [
    {"contrato": "NUEVO", "promedio": consumo, "pde_actual": None}]

try:
    pdes, lam, topados = sim.repartir_por_consumo([u["promedio"] for u in usuarios])
except ValueError as e:
    st.error(str(e))
    st.stop()

pde_medio = pdes[-1]
pde_max = techo_individual(consumo)

#  El piso se topa contra el escenario medio. Sin ese tope, un PDE fijo del 3 %
#  (4.500 kWh) supera el techo de cualquier usuario que consuma menos de 5.625
#  kWh/mes, y el "mínimo" quedaría por encima del "máximo".
pde_min = min(PDE_PISO_CONSERVADOR, pde_medio)

r_min = sim.balance_mensual(consumo, pde_min, cu, cv, cu_ce, contrib)
r = sim.balance_mensual(consumo, pde_medio, cu, cv, cu_ce, contrib)
r_max = sim.balance_mensual(consumo, pde_max, cu, cv, cu_ce, contrib)

piso_colapsa = abs(pde_min - pde_medio) < 1e-9
techo_colapsa = abs(pde_max - pde_medio) < 1e-9


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
              help="Cuánto baja tu factura en porcentaje. Es el descuento por "
                   "kWh multiplicado por la cobertura.")

st.progress(min(1.0, r["cobertura"]))

#  Aquí sí aparece el PDE, en letra chica y con su definición en el <abbr>:
#  es el dato que el usuario va a ver en el formulario de conexión, así que
#  conviene que lo reconozca, pero no es lo que le vende la idea.
st.markdown(
    f"<div class='nota'>La comunidad pone el <b>{pct(r['cobertura'], 1)}</b> de tu "
    f"energía, con un <abbr title=\"{AYUDA['pde']}\">PDE</abbr> del "
    f"<b>{pct(pde_medio, 2)}</b> de nuestra generación actual. "
    f"El resto sigue viniendo de la red.</div>",
    unsafe_allow_html=True)


# =========================================================
# BLOQUE 3 — RANGO DE AHORROS
# =========================================================

st.divider()
st.subheader("Tu rango de ahorro")
st.caption("Depende de cuánta energía te alcance a entregar la comunidad. "
           "El descuento por kWh es el mismo en los tres: lo que cambia es "
           "la cobertura.")

t1, t2, t3 = st.columns(3)

#  El detalle de cada escenario vive en el tooltip, no en la tarjeta. Abajo de
#  cada número va una sola línea: cuándo pasa ese escenario.
ESCENARIOS = [
    (t1, "Mínimo", r_min, AYUDA["conservador"], False,
     "Si la comunidad se llena de miembros."),
    (t2, "Tu caso hoy", r, AYUDA["tucaso"], True,
     "Con los miembros que hay hoy."),
    (t3, "Máximo", r_max, AYUDA["optimo"], False,
     "Si la comunidad tiene energía disponible para ti."),
]

for col, etiqueta, res, ayuda, destacada, pie in ESCENARIOS:
    with col:
        with st.container(border=True):
            #  Solo la tarjeta del medio lleva distintivo: es la única con un
            #  número real. Las otras dos son el marco.
            st.markdown(
                "<div class='etiqueta'>★ Tu escenario</div>" if destacada
                else "<div class='etiqueta-gris'>&nbsp;</div>",
                unsafe_allow_html=True)
            st.metric(etiqueta, cop(res["ahorro_mes"]), help=ayuda)
            st.caption(esc(f"al mes  ·  {millones(res['ahorro_anual'])} al año  ·  "
                           f"{pct(res['ahorro_pct'], 1)} de tu factura"))
            st.progress(min(1.0, res["cobertura"]))
            st.caption(f"Cubrimos el {pct(res['cobertura'], 1)} de tu energía")
            st.caption(f":gray[{pie}]")

if piso_colapsa:
    st.caption("Tu consumo es pequeño frente a la planta: ya estás en el piso, "
               "así que el mínimo y tu caso de hoy son el mismo.")
if techo_colapsa:
    st.caption("Ya estás en tu máximo: la comunidad te está dando todo lo que "
               "te puede dar.")


# =========================================================
# BLOQUE 4 — DE DÓNDE SALE
# =========================================================

st.divider()
st.subheader("¿De dónde sale el ahorro?")

p1, p2, p3 = st.columns(3)
with p1:
    st.markdown("**⚡ Energía más barata**")
    st.markdown("<div class='pilar'>Te vendemos el kWh por debajo de lo que te "
                "cobra la red.</div>", unsafe_allow_html=True)
with p2:
    st.markdown("**🧾 Sin contribución**")
    st.markdown("<div class='pilar'>Los kWh que te entregamos no pagan el 20 % "
                "de contribución de solidaridad.</div>", unsafe_allow_html=True)
with p3:
    st.markdown("**📄 Tu factura de siempre**")
    st.markdown("<div class='pilar'>El comercializador te descuenta la energía "
                "que pusimos nosotros. No cambias de operador.</div>",
                unsafe_allow_html=True)

with st.container(border=True):
    st.metric("En total, descuento sobre cada kWh que te entregamos",
              pct(au["descuento_efectivo"], 1), help=AYUDA["descuento"])


# =========================================================
# BLOQUE 5 — CONFIANZA
# =========================================================
#  Aquí iba el botón de registro. Se quitó: esto es un simulador, no el
#  portal de suscripción, y un botón que no lleva a ninguna parte resta
#  credibilidad en vez de sumarla.

st.divider()
st.caption(f"{len(sim.USUARIOS_BASE)} miembros activos  ·  "
           f"{num(sim.GENERACION_ANUAL_KWH)} kWh/año  ·  100 % solar  ·  "
           f"Amparado por las Resoluciones CREG 174 de 2021 y 101 072 de 2025.")


# =========================================================
# BLOQUE 7 — EL DETALLE TÉCNICO
# =========================================================

with st.expander("Ver el detalle técnico"):

    # ---------- Ahorro unitario ----------
    st.markdown("**Por cada kWh que entrega la comunidad**")
    st.dataframe(pd.DataFrame([
        {"Concepto": "Lo que ese kWh cuesta hoy en la red", "Valor": cop(au["costo_red"], 2)},
        {"Concepto": "Ahorro por tarifa (CU − Cv − CU_CE)", "Valor": cop(au["por_tarifa"], 2)},
        {"Concepto": "Ahorro por contribución evitada",     "Valor": cop(au["por_contribucion"], 2)},
        {"Concepto": "AHORRO POR kWh",                      "Valor": cop(au["total"], 2)},
    ]), hide_index=True, width='stretch')
    st.caption(f"Descuento efectivo: **{pct(au['descuento_efectivo'])}**. "
               f"El ahorro de la factura es menor porque la comunidad solo cubre "
               f"{pct(r['cobertura'], 1)} del consumo: "
               f"{pct(au['descuento_efectivo'], 1)} × {pct(r['cobertura'], 1)} = "
               f"{pct(r['ahorro_pct'], 1)}.")

    # ---------- Las dos facturas ----------
    st.markdown("**La factura, antes y después**")
    st.dataframe(pd.DataFrame([
        {"Concepto": f"SIN comunidad ({num(consumo)} kWh a la red)", "Valor": cop(r["factura_sin"])},
        {"Concepto": f"Energía de la red ({num(r['energia_red'])} kWh)", "Valor": cop(r["pago_red"])},
        {"Concepto": f"Cargo Cv sobre lo permutado ({num(r['exc1'])} kWh)", "Valor": cop(r["cargo_cv"])},
        {"Concepto": f"Pago a la comunidad ({num(r['asignada'])} kWh)", "Valor": cop(r["pago_ce"])},
        {"Concepto": "CON comunidad", "Valor": cop(r["factura_con"])},
    ]), hide_index=True, width='stretch')
    st.caption(esc(f"Del ahorro mensual, {cop(r['exc1'] * au['por_contribucion'])} viene de la "
                   f"contribución evitada y {cop(r['exc1'] * au['por_tarifa'])} del "
                   f"diferencial tarifario."))

    # ---------- Los tres escenarios en PDE ----------
    st.markdown("**Los tres escenarios, en PDE**")
    st.dataframe(pd.DataFrame([
        {"Escenario": "Mínimo", "PDE": pct(pde_min, 3),
         "kWh/mes": num(r_min["asignada"]), "Cobertura": pct(r_min["cobertura"], 1),
         "Ahorro/mes": cop(r_min["ahorro_mes"]), "% factura": pct(r_min["ahorro_pct"], 2)},
        {"Escenario": "Tu caso hoy", "PDE": pct(pde_medio, 3),
         "kWh/mes": num(r["asignada"]), "Cobertura": pct(r["cobertura"], 1),
         "Ahorro/mes": cop(r["ahorro_mes"]), "% factura": pct(r["ahorro_pct"], 2)},
        {"Escenario": "Máximo", "PDE": pct(pde_max, 3),
         "kWh/mes": num(r_max["asignada"]), "Cobertura": pct(r_max["cobertura"], 1),
         "Ahorro/mes": cop(r_max["ahorro_mes"]), "% factura": pct(r_max["ahorro_pct"], 2)},
    ]), hide_index=True, width='stretch')
    st.caption(f"Mínimo = min({pct(PDE_PISO_CONSERVADOR, 0)}, PDE del reparto). "
               f"El tope evita que un PDE fijo supere el techo individual en "
               f"consumos pequeños. Máximo = min({pct(sim.PDE_MAXIMO_LEGAL, 1)} legal, "
               f"{pct(sim.TOPE_CONSUMO, 0)} del consumo).")

    # ---------- Reparto ----------
    st.markdown("**Reparto del PDE en la comunidad**")

    ok, hallazgos = sim.validar_comunidad(pdes, len(pdes))
    if ok:
        st.success(f"Reparto válido: los PDE suman {pct(sum(pdes), 4)} y ninguno "
                   f"llega al 10 %.")
    else:
        st.error(" ".join(h[1] for h in hallazgos if h[0] == "ERROR"))

    # El aviso de capacidad instalada no se muestra: es una tarea pendiente del
    # modelo, no un hallazgo que le sirva a quien mira la pantalla.
    for nivel, msg in hallazgos:
        if nivel == "AVISO" and "CAPACIDAD_INSTALADA" not in msg:
            st.warning(msg)

    st.dataframe(pd.DataFrame([{
        "Contrato":  u["contrato"],
        "Consumo":   num(u["promedio"]),
        "PDE antes": "—" if u["pde_actual"] is None else pct(u["pde_actual"], 3),
        "PDE nuevo": pct(p, 3),
        "Cambio":    "INGRESO" if u["pde_actual"] is None else
                     ("+" if p > u["pde_actual"] else "") + pct(p - u["pde_actual"], 3),
        "kWh/mes":   num(sim.energia_asignada(p)),
        "Cobertura": pct(sim.energia_asignada(p) / u["promedio"], 1),
    } for u, p in zip(usuarios, pdes)]), hide_index=True, width='stretch')
    st.caption(f"Al entrar un usuario nuevo se recalculan todos los PDE. El reparto "
               f"es proporcional al consumo: todos quedan con la misma cobertura "
               f"({pct(lam * sim.GENERACION_MENSUAL_KWH, 2)}), salvo "
               + (f"el {len(topados)} que choca" if len(topados) == 1
                  else f"los {len(topados)} que chocan")
               + " contra su techo.")

    # ---------- Proyección ----------
    st.markdown(f"**Proyección a {int(anios)} año(s)**")
    proy = sim.proyectar(consumo, pde_medio, cu, cv, cu_ce, contrib, int(anios))
    st.dataframe(pd.DataFrame([{
        "Año":            p["anio"],
        "CU red":         cop(p["cu"], 2),
        "CU comunidad":   cop(p["cu_ce"], 2),
        "Ahorro del año": cop(p["ahorro_anual"]),
        "%":              pct(p["ahorro_pct"], 1),
        "Acumulado":      cop(p["acumulado"]),
    } for p in proy]), hide_index=True, width='stretch')

    st.line_chart(pd.DataFrame({"Ahorro acumulado": [p["acumulado"] for p in proy]},
                               index=[f"Año {p['anio']}" for p in proy]))

    st.caption(f"Supuestos: la tarifa de red sube {pct(sim.INFLACION_RED_ANUAL, 1)} "
               f"al año y el precio de la comunidad {pct(sim.INFLACION_CE_ANUAL, 1)}. "
               f"El PDE se mantiene. El acumulado son pesos corrientes.")

st.caption(":gray[Estimación basada en tu consumo promedio y en las tarifas "
           "vigentes. El ahorro real depende del reparto de energía entre los "
           "miembros de la comunidad y de la tarifa de tu comercializador. "
           "No constituye una oferta vinculante.]")
