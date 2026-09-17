# =========================================================
#  INTERFAZ CON STREAMLIT — WE POWER
# =========================================================

import os
import base64
import datetime
import importlib.util
import pandas as pd
import streamlit as st

# --- Cargar el modelo desde la carpeta de este archivo ---------------------
AQUI = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "simulador_ce", os.path.join(AQUI, "simulador_ce.py"))
sim = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sim)


def _cargar(nombre):
    """Carga un módulo vecino por ruta, sin depender de sys.path.

    Un `import informe_pdf` a secas falla en algunos despliegues porque la
    carpeta del script no siempre queda en la ruta de búsqueda de Python.
    Devuelve (módulo, error). Si algo falla, el error se guarda COMPLETO en
    vez de tragárselo: sin eso no hay forma de saber si el archivo no está
    o si está pero no carga.
    """
    ruta = os.path.join(AQUI, nombre + ".py")
    if not os.path.exists(ruta):
        return None, "no-existe"
    try:
        e = importlib.util.spec_from_file_location(nombre, ruta)
        m = importlib.util.module_from_spec(e)
        e.loader.exec_module(m)
        return m, None
    except Exception as err:
        import traceback
        return None, traceback.format_exc()


informe_pdf, _error_informe = _cargar("informe_pdf")


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


def _logo_b64():
    """Igual que en informe_pdf.py: mete el logo en base64 para no
    depender de la ruta del archivo."""
    ruta = os.path.join(AQUI, "logo.png")
    if os.path.exists(ruta):
        with open(ruta, "rb") as f:
            return "data:image/png;base64," + base64.b64encode(f.read()).decode()
    return ""


# =========================================================
# LOS PLANES
# =========================================================
DESCUENTOS = ("10 %", "Otro")
DESCUENTO_INICIAL = "10 %"

ASESOR_NOMBRE = "Ricardo Orozco"
ASESOR_TEL = "3017877074"
ASESOR_MAIL = "colombia@wepower.com.co"

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
        "Tu nueva factura: lo que tu comercializador te sigue cobrando por la "
        "energía, más lo que le pagas a WE Power por la parte que cubrimos.",
    "kwh":
        "Toda tu energía sigue llegando por la red. Lo que cambia es el precio: "
        "los kWh que cubrimos salen de tu consumo facturado, así que no pagan "
        "contribución, y sobre ellos solo pagas el cargo del comercializador "
        "más el precio acordado con WE Power.",
    "basico":
        "El ahorro mínimo que podrías recibir.",
    "estandar":
        "Es el 80 % de tu consumo.",
    "premium":
        "Cubrimos hasta el 100 % de tu consumo, sujeto a la energía disponible "
        "en la planta.",
    "cu":
        "El valor por kWh de tu factura, antes de contribución.",
    "cv":
        "Comercialización. Ya está dentro del CU. El comercializador lo cobra "
        "por cada kWh permutado (Art. 26, Res. CREG 174/2021).",
    "contribuye":
        "Sí: estratos 5 y 6 y comerciales. No: industriales exentos por código "
        "CIIU (Ley 1430/2010, art. 2).",
    "descuento_cu":
        "Sirve para calcular el valor del kWh que entrega la comunidad. Se le "
        "aplica este descuento al CU asignado y se le resta el Cv.",
    "anios":
        "Para la proyección. Se asume que la tarifa de red sube más rápido que "
        "el precio de WE Power, así que la brecha se abre con los años.",
    "pde":
        "Porcentaje de Distribución de Excedentes: la tajada de la generación "
        "de la planta que te corresponde. Los PDE de todos los miembros suman "
        "100 % y ninguno puede llegar al 10 % (Art. 20 num. 1, Res. CREG "
        "101 072 de 2025).",
}

st.set_page_config(page_title="WE Power · Ahorra en tu factura",
                   page_icon="⚡", layout="centered")

_logo = _logo_b64()

# Logo estándar de Streamlit (esquina superior y sidebar).
if _logo:
    st.logo(_logo, size="large")

st.markdown(f"""
<style>
  .etiqueta  {{ font-size: .75rem; letter-spacing: .08em; text-transform: uppercase;
               color: #2E7D32; font-weight: 700; margin-bottom: .2rem; }}
  .etiqueta-gris {{ font-size: .75rem; letter-spacing: .08em; text-transform: uppercase;
               color: #888; font-weight: 700; margin-bottom: .2rem; }}
  .pilar     {{ font-size: .92rem; color: #444; }}
  .nota      {{ font-size: .875rem; color: rgba(49,51,63,.6); margin-top: -.5rem; }}
  .nota abbr {{ text-decoration: underline dotted; cursor: help; }}
  div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMetricValue"] {{
      font-size: 1.5rem;
  }}

  /* ---- Identidad WE Power ---------------------------------------- */

  .we-masthead {{
      display: flex; align-items: center; gap: .9rem;
      background: linear-gradient(135deg, #004191 0%, #00305F 100%);
      margin: -1rem -1rem 1.8rem -1rem; padding: 1.15rem 1.6rem;
      border-radius: 0 0 14px 14px;
  }}
  .we-masthead img {{ height: 38px; }}
  .we-masthead .we-marca {{ color: #fff; font-weight: 800; font-size: 1.05rem;
      letter-spacing: .01em; line-height: 1.15; }}
  .we-masthead .we-tag {{ color: rgba(255,255,255,.82); font-size: .78rem; }}

  /* Separadores en el color de acento, no el gris por defecto */
  div[data-testid="stDivider"] hr, hr {{ border-color: #E2A03C33; }}

  /* Insignia sobre la tarjeta del plan recomendado */
  .we-badge {{
      display: inline-block; background: #E2A03C; color: #fff;
      font-size: .68rem; font-weight: 700; letter-spacing: .03em;
      padding: .15rem .55rem; border-radius: 999px; margin-bottom: .5rem;
  }}

  /* Resalta la tarjeta del plan Estándar (2da columna) frente al Básico */
  div[data-testid="column"]:nth-of-type(2)
      div[data-testid="stVerticalBlockBorderWrapper"] {{
      border-color: #E2A03C; border-width: 1.5px;
  }}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="we-masthead">
  {'<img src="' + _logo + '">' if _logo else ''}
  <div>
    <div class="we-marca">WE POWER</div>
    <div class="we-tag">Comunidades energéticas · We Club</div>
  </div>
</div>
""", unsafe_allow_html=True)

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

    opcion = st.segmented_control(
        "Descuento sobre CU asignado", DESCUENTOS,
        default=DESCUENTO_INICIAL, help=AYUDA["descuento_cu"])

    sin_descuento = opcion is None
    if sin_descuento:
        descuento = 0.0

    if opcion == "Otro":
        descuento = st.number_input("¿Cuánto?  (%)", min_value=0.0, max_value=60.0,
                                    value=10.0, step=0.5,
                                    help="Para un descuento pactado por fuera de "
                                         "los valores de siempre.") / 100.0
    elif not sin_descuento:
        descuento = float(opcion.replace(" %", "")) / 100.0

    cu_ce = sim.precio_por_descuento(cu, cv, descuento)

    st.text_input("Valor del kWh de la comunidad (COP/kWh)",
                  value=cop(cu_ce, 2), disabled=True,
                  help="Resulta del descuento seleccionado y de los valores "
                       "de CU y Cv.")

    if sin_descuento:
        st.caption("Calculado **sin descuento comercial**: el ahorro viene solo "
                   "de la contribución evitada. Escoge un descuento para la "
                   "oferta real.")

    anios = st.number_input("Período de proyección (años)",
                            min_value=1, max_value=25, value=5, step=1,
                            help=AYUDA["anios"])

    st.divider()
    st.caption(f"Planta: {num(sim.GENERACION_MENSUAL_KWH)} kWh/mes  ·  "
               f"{sim.MIEMBROS_ACTUALES} miembros actuales")

contrib = sim.CONTRIBUCION if contribuye else 0.0

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

if consumo < sim.CONSUMO_MINIMO_KWH:
    st.warning(f"Nuestro servicio está pensado para empresas con un consumo "
               f"desde **{num(sim.CONSUMO_MINIMO_KWH)} kWh al mes** — unos "
               f"{cop(sim.CONSUMO_MINIMO_KWH * cu * (1 + contrib))} de factura. "
               f"Con {num(consumo)} kWh al mes todavía no podemos hacerte una "
               f"propuesta.\n\n**Escríbenos** y revisamos tu caso.")
    st.stop()

if cv > cu:
    st.error("El Cv no puede ser mayor que el CU. Revisa los supuestos.")
    st.stop()

umb = sim.umbrales_precio(cu, cv, contrib)
au = sim.ahorro_unitario_tipo1(cu, cv, cu_ce, contrib)

if cu_ce >= umb["techo_absoluto"]:
    st.error(esc(f"Con un precio de {cop(cu_ce, 2)} por kWh no habría ahorro. "
                 f"El precio tendría que bajar de {cop(umb['techo_absoluto'], 2)}."))
    st.stop()

pde_bas = sim.pde_escenario_minimo(consumo)
pde_est = sim.pde_por_cobertura(sim.PLAN_ESTANDAR, consumo)

r_bas = sim.balance_mensual(consumo, pde_bas, cu, cv, cu_ce, contrib)
r_est = sim.balance_mensual(consumo, pde_est, cu, cv, cu_ce, contrib)

r = r_est
pde_actual = pde_est

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
    f"<div class='nota'>Con el <b>plan Estándar</b> cubrimos el "
    f"<b>{pct(r['cobertura'], 0)}</b> de tu consumo, con un "
    f"<abbr title=\"{AYUDA['pde']}\">PDE</abbr> del <b>{pct(pde_actual, 2)}</b> "
    f"de nuestra generación. El resto lo sigues pagando a tu comercializador "
    f"al precio de siempre.</div>",
    unsafe_allow_html=True)

st.info(f"**Es un estimado.** Está calculado con un consumo promedio de "
        f"{num(consumo)} kWh al mes. Tu consumo cambia mes a mes y tu ahorro "
        f"también: en un mes que consumas más, ahorras más; en uno que consumas "
        f"menos, ahorras menos.")

st.divider()
st.subheader("Tu factura, antes y después")

a1, a2 = st.columns(2)
with a1:
    st.metric("Antes pagabas", cop(r["factura_sin"]), help=AYUDA["antes"])
    st.caption(f"Le comprabas a la red los {num(consumo)} kWh que consumes.")
with a2:
    st.metric("Ahora pagas (entre las dos)", cop(r["factura_con"]),
              "-" + cop(r["ahorro_mes"]).replace("$ ", ""),
              delta_color="inverse", help=AYUDA["despues"])
    st.caption(f"{num(r['asignada'])} kWh se te descuentan de la factura; el "
               f"resto lo pagas al precio de siempre.")

st.markdown("**¿De qué se compone lo que vas a pagar?**")
pago_comercializador = r["pago_red"] + r["cargo_cv"]

st.dataframe(pd.DataFrame([
    {"Concepto": "Lo que le sigues pagando a tu comercializador",
     "Valor": cop(pago_comercializador)},
    {"Concepto": "Lo que le pagas a WE Power",
     "Valor": cop(r["pago_ce"])},
    {"Concepto": "TOTAL, ENTRE LAS DOS FACTURAS", "Valor": cop(r["factura_con"])},
]), hide_index=True, width='stretch')

st.caption(f"Recibirás **dos facturas**: la de tu comercializador, como siempre, "
           f"y la de la comunidad. "
           f"Tu comercializador te sigue facturando toda la energía; ese cobro "
           f"junta dos cosas: los {num(r['energia_red'])} kWh que no alcanzamos a "
           f"cubrir, al precio de siempre, y el cargo que te hace por los "
           f"{num(r['exc1'])} kWh que sí cubrimos.")

st.caption(esc(f"Antes: {cop(r['factura_sin'])}.  Ahora: {cop(r['factura_con'])}.  "
               f"Te quedan {cop(r['ahorro_mes'])} en el bolsillo cada mes, "
               f"{cop(r['ahorro_anual'])} al año."))

st.divider()
st.subheader("Por cada kWh que te cubrimos")

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
    st.caption("En cada kWh que alcanzamos a cubrir.")

st.caption(f"Tu factura no baja ese mismo {pct(au['descuento_efectivo'], 0)} porque "
           f"el descuento aplica solo a los kWh que cubrimos, que son el "
           f"{pct(r['cobertura'], 0)} de tu consumo: "
           f"{pct(au['descuento_efectivo'], 0)} × {pct(r['cobertura'], 0)} = "
           f"{pct(r['ahorro_pct'], 1)} de tu factura.")

st.divider()
st.subheader("Ahorros posibles")
st.caption("Lo único que cambia entre los tres es qué parte de tu consumo "
           "cubrimos. El descuento por kWh es el mismo en los tres.")

p1, p2, p3 = st.columns(3)

PLANES = [
    (p1, "Básico", r_bas, AYUDA["basico"], "Siempre disponible."),
    (p2, "Estándar", r_est, AYUDA["estandar"], "El más pedido."),
]

for col, nombre, res, ayuda, pie in PLANES:
    with col:
        with st.container(border=True):
            if nombre == "Estándar":
                st.markdown(f'<span class="we-badge">{pie}</span>',
                            unsafe_allow_html=True)
            st.metric(nombre, cop(res["ahorro_mes"]), help=ayuda)
            st.caption(esc(f"al mes  ·  {millones(res['ahorro_anual'])} al año  ·  "
                           f"{pct(res['ahorro_pct'], 1)} de tu factura"))
            st.progress(min(1.0, res["cobertura"]))
            st.caption(f"Cubrimos el {pct(res['cobertura'], 0)} de tu consumo")
            if nombre != "Estándar":
                st.caption(f":gray[{pie}]")

with p3:
    with st.container(border=True):
        st.metric("Premium", "A tu medida", help=AYUDA["premium"])
        st.caption("Cubrimos hasta el 100 % de tu consumo.")
        st.progress(1.0)
        st.caption("Se cotiza contigo")
        st.caption(":gray[Cupo limitado.]")

st.info("**¿Te interesa el plan Premium?** Es a la medida: revisamos tu consumo "
        "mes a mes y te pasamos la cifra. **Comunícate con nosotros.**")

if abs(pde_bas - pde_est) < 1e-9:
    st.warning("Con tu consumo, el Básico y el Estándar te dan lo mismo: ya "
               "estarías recibiendo el máximo que le podemos asignar a un solo "
               "usuario. **Comunícate con nosotros** para revisar tu caso.")

st.divider()
st.subheader("¿De dónde sale el ahorro?")

q1, q2, q3 = st.columns(3)
with q1:
    st.markdown("**⚡ Energía más barata**")
    st.markdown("<div class='pilar'>El kWh que cubrimos te sale más barato que "
                "el que te cobra tu comercializador.</div>", unsafe_allow_html=True)
with q2:
    st.markdown("**🧾 Sin contribución**")
    st.markdown("<div class='pilar'>Los kWh que cubrimos salen de tu consumo "
                "facturado, así que no pagan el 20 % de contribución.</div>",
                unsafe_allow_html=True)
with q3:
    st.markdown("**📄 Tu factura de siempre**")
    st.markdown("<div class='pilar'>El comercializador te descuenta la energía "
                "que pusimos nosotros. No cambias de operador.</div>",
                unsafe_allow_html=True)

st.divider()
st.caption(f"{sim.MIEMBROS_ACTUALES} miembros activos  ·  "
           f"{num(sim.GENERACION_ANUAL_KWH)} kWh/año  ·  100 % solar  ·  "
           f"Amparado por las Resoluciones CREG 174 de 2021 y 101 072 de 2025.")

proy = sim.proyectar(consumo, pde_actual, cu, cv, cu_ce, contrib, int(anios))

with st.expander("Ver cómo crece tu ahorro con los años"):

    st.caption(f"Con el plan Estándar. La tarifa de red sube "
               f"{pct(sim.INFLACION_RED_ANUAL, 1)} al año y el precio de WE Power "
               f"{pct(sim.INFLACION_CE_ANUAL, 1)}: como la red sube más rápido, "
               f"la brecha se abre y tu ahorro crece.")

    st.dataframe(pd.DataFrame([{
        "Año":               p["anio"],
        "Ahorro del año":    cop(p["ahorro_anual"]),
        "% de tu factura":   pct(p["ahorro_pct"], 1),
        "Ahorro acumulado":  cop(p["acumulado"]),
    } for p in proy]), hide_index=True, width='stretch')

    st.line_chart(pd.DataFrame({"Ahorro acumulado": [p["acumulado"] for p in proy]},
                               index=[f"Año {p['anio']}" for p in proy]))

    st.caption("El acumulado son pesos corrientes, sin traer a valor presente.")

st.divider()

if informe_pdf is None:
    if _error_informe == "no-existe":
        st.warning("Para generar el informe en PDF falta el archivo "
                   "**informe_pdf.py** en la misma carpeta que esta app.")
    else:
        st.error("El archivo **informe_pdf.py** está, pero no cargó.")

    with st.expander("Ver el diagnóstico"):
        st.write("**Carpeta donde está buscando:**")
        st.code(AQUI)
        try:
            archivos = sorted(os.listdir(AQUI))
        except Exception as e:
            archivos = [f"(no se pudo leer la carpeta: {e})"]
        st.write("**Archivos que hay ahí:**")
        st.code("\n".join(archivos) or "(vacía)")
        if _error_informe and _error_informe != "no-existe":
            st.write("**Error al cargar:**")
            st.code(_error_informe)
    st.stop()

st.subheader("¿Quieres llevarte este cálculo?")
st.caption("Completa los datos y te generamos el informe en PDF, con tus números "
           "y la información de WE Power.")

with st.form("datos_informe"):
    f1, f2 = st.columns(2)
    with f1:
        nombre = st.text_input("Nombre completo", placeholder="Nombre y apellido")
        telefono = st.text_input("Teléfono", placeholder="0000000000")
        ciudad = st.text_input("Ciudad", placeholder="Ciudad")
    with f2:
        direccion = st.text_input("Dirección", placeholder="Dirección del predio")
        correo = st.text_input("Correo electrónico",
                               placeholder="nombre@empresa.com",
                               help="A este correo te llega la oferta.")
        fecha = st.date_input("Fecha del informe", value=datetime.date.today())

    st.caption(f"Tu asesor: **{ASESOR_NOMBRE}** · {ASESOR_TEL} · {ASESOR_MAIL}")

    st.caption("Al continuar autorizas a WE Power a usar estos datos para "
               "contactarte sobre esta cotización.  *(texto provisional: falta "
               "redactar la autorización de tratamiento de datos)*")

    generar = st.form_submit_button("Generar informe", type="primary")

if generar:
    if not nombre.strip():
        st.error("Escribe al menos el nombre para generar el informe.")
    else:
        datos = informe_pdf.armar_datos(
            {"nombre": nombre, "telefono": telefono, "direccion": direccion,
             "ciudad": ciudad, "correo": correo,
             "fecha": fecha.strftime("%d/%m/%Y"),
             "asesor_nombre": ASESOR_NOMBRE, "asesor_tel": ASESOR_TEL,
             "asesor_mail": ASESOR_MAIL},
            sim, r, au, proy, consumo, cu, cv, cu_ce)
        base = "Informe WE Club - " + (nombre.strip() or "cliente")
        st.session_state["html"] = informe_pdf.construir_html(datos).encode("utf-8")
        st.session_state["html_nombre"] = base + ".html"
        st.session_state["archivo_nombre"] = base + ".pdf"
        try:
            st.session_state["pdf"] = informe_pdf.generar_pdf(datos)
            st.session_state.pop("pdf_error", None)
        except Exception as err:
            import traceback
            st.session_state.pop("pdf", None)
            st.session_state["pdf_error"] = traceback.format_exc()

if st.session_state.get("pdf"):
    st.success("Informe listo.")
    st.download_button("Descargar informe en PDF", st.session_state["pdf"],
                       file_name=st.session_state["archivo_nombre"],
                       mime="application/pdf", type="primary")

elif st.session_state.get("html"):
    st.success("Informe listo.")
    st.download_button("Descargar informe", st.session_state["html"],
                       file_name=st.session_state["html_nombre"],
                       mime="text/html", type="primary")
    st.caption("Se descarga en HTML. Ábrelo con doble clic y usa **Imprimir → "
               "Guardar como PDF** para tenerlo en PDF. Sale igual: es la misma "
               "plantilla.")
    with st.expander("¿Por qué no salió directo en PDF?"):
        st.write("La librería que convierte a PDF (WeasyPrint) no está "
                 "disponible en este despliegue. Revisa que el repositorio "
                 "tenga `weasyprint` dentro de **requirements.txt** y el "
                 "archivo **packages.txt** con las librerías del sistema; "
                 "después entra a *Manage app* y dale **Reboot**.")
        st.write("**Error exacto:**")
        st.code(st.session_state.get("pdf_error", "(sin detalle)"))

st.caption(":gray[Estimación basada en tu consumo promedio y en las tarifas "
           "vigentes. El ahorro real depende de tu consumo mes a mes y de la "
           "tarifa de tu comercializador. No constituye una oferta vinculante.]")
