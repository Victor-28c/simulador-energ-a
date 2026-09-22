# =========================================================
#  INTERFAZ CON STREAMLIT — WE POWER
# =========================================================

import os
import re
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


# =========================================================
# LOS PLANES
# =========================================================
#  Un plan es una COBERTURA: qué parte del consumo del usuario pone WE Power.
#  El PDE sale de ahí, no al revés — así el usuario compara en el idioma que
#  entiende y los planes nunca se invierten entre sí.
#
#  Los tres planes y la fórmula del PDE viven en simulador_ce.py:
#      sim.pde_escenario_minimo() / PLAN_ESTANDAR / PLAN_PREMIUM
#      sim.pde_por_cobertura(cobertura, consumo)
#  Esta interfaz no define ninguna regla de negocio: solo las usa.


# --- Opciones de descuento que se ofrecen ---------------------------------
#  "Otro" queda para un descuento pactado por fuera de estos valores: sin él,
#  un 7 % negociado obligaría a tocar el código.
#  DESCUENTO_INICIAL es solo cuál botón viene pulsado al abrir la página: la
#  calculadora trabaja siempre con el que esté seleccionado.
DESCUENTOS = ("10 %", "Otro")
DESCUENTO_INICIAL = "10 %"


# --- Hasta dónde puede llegar la proyección -------------------------------
#  Diez años es lo máximo que cabe en la página de la proyección del informe.
#  Con once la tabla se desborda y el PDF pasa de 8 a 9 páginas.
ANIOS_MAXIMOS = 10


# =========================================================
# QUÉ SE PUEDE ESCRIBIR EN CADA CASILLA
# =========================================================
#  El teléfono solo admite dígitos; el nombre y la ciudad, solo letras.
#  El correo y la dirección no se filtran: los dos llevan números y letras.
#
#  No sale ningún aviso de error: el carácter que no corresponde simplemente
#  no se queda. Streamlit revisa el texto cuando la casilla pierde el foco o
#  se pulsa Enter, así que el carácter alcanza a verse un instante y
#  desaparece. Para que esto funcione, las casillas NO pueden ir dentro de un
#  st.form: dentro de un formulario Streamlit no ejecuta estas revisiones
#  hasta que se envía todo.

#  Se admiten espacios y los signos que llevan los nombres de verdad:
#  "S.A.S.", "O'Brien", "María-José". Lo que no entra son los números.
NO_ES_LETRA = re.compile(r"[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ '.\-&]")
NO_ES_DIGITO = re.compile(r"[^0-9]")


def _filtrar(clave, patron):
    """Borra de la casilla `clave` todo lo que sobre, sin decir nada."""
    valor = st.session_state.get(clave, "")
    limpio = patron.sub("", valor)
    if limpio != valor:
        st.session_state[clave] = limpio


def solo_letras(clave):
    _filtrar(clave, NO_ES_LETRA)


def solo_digitos(clave):
    _filtrar(clave, NO_ES_DIGITO)


# --- Comercializadores que se pueden escoger ------------------------------
#  El cliente NO cambia de comercializador al entrar al club, así que el
#  informe lo nombra. Es solo un texto: no entra en ningún cálculo.
#
#  La lista sale del Boletín Tarifario de Energía Eléctrica de la
#  Superintendencia de Servicios Públicos (II trimestre de 2025), que agrupa a
#  los comercializadores del país por tamaño, más los comercializadores puros
#  que operan en el mercado no regulado. Se usa el nombre comercial, no el
#  razón social, porque es el que reconoce el cliente.
#
#  Igual hay que revisarla con Comercial de vez en cuando: el sector se mueve
#  (Electricaribe se partió en Air-e y Afinia, Codensa pasó a ser Enel). Está
#  aquí, en un solo sitio, para editarla sin tocar nada más. Y por eso existe
#  "Otro": ninguna lista los cubre a todos y no se puede dejar a un asesor
#  bloqueado porque su cliente no aparece.
COMERCIALIZADORES = [
    # Grandes
    "EPM",                      # Empresas Públicas de Medellín E.S.P.
    "Enel Colombia",            # antes Codensa · Bogotá y Cundinamarca
    "Celsia",                   # Celsia Colombia S.A. E.S.P.
    "Air-e",                    # Air-e S.A.S. E.S.P. · Caribe Sol
    "Afinia",                   # Caribemar de la Costa S.A.S. E.S.P. · Caribe Mar
    "ESSA",                     # Electrificadora de Santander S.A. E.S.P.
    "EMCALI",                   # Empresas Municipales de Cali E.S.P.
    # Medianos
    "EBSA",                     # Empresa de Energía de Boyacá S.A. E.S.P.
    "CHEC",                     # Central Hidroeléctrica de Caldas S.A. E.S.P.
    "CEDENAR",                  # Centrales Eléctricas de Nariño S.A. E.S.P.
    "EDEQ",                     # Empresa de Energía del Quindío S.A. E.S.P.
    "EMSA",                     # Electrificadora del Meta S.A. E.S.P.
    "CENS",                     # Centrales Eléctricas de Norte de Santander S.A. E.S.P.
    "Electrohuila",             # Electrificadora del Huila S.A. E.S.P.
    # Comercializadores puros, frecuentes en el mercado no regulado
    "Vatia",
    "Enertotal",
    "Enel X Colombia",
    "Bia Energy",
    "Enerbit",
    "QI Energy",
    "Ruitoque",
    "Otro",
]


# --- Asesor comercial por defecto -----------------------------------------
ASESOR_NOMBRE = "Ricardo Orozco"
ASESOR_TEL = "3017877074"
ASESOR_MAIL = "colombia@wepower.com.co"


# --- Los colores de WE Power ----------------------------------------------
#  Son los MISMOS del informe en PDF. Si algun dia cambia la marca, se cambia
#  aqui y en informe_pdf.py: la pantalla y el papel tienen que verse iguales.
AZUL = "#004191"
AZUL_OSCURO = "#00305F"
NARANJA = "#E2A03C"
NARANJA_TEXTO = "#C07B14"   # el naranja del logo aclara demasiado sobre blanco
GRIS = "#5A6472"
GRIS_CLARO = "#F2F6FB"


def _logo_data_uri():
    """El logo, metido dentro de la pagina como texto.

    Streamlit no sirve archivos sueltos de la carpeta, asi que apuntar a
    "logo_wepower.png" desde el CSS no funciona. Codificandolo en base64 viaja
    dentro del propio HTML y no depende de ninguna ruta.
    """
    import base64
    for nombre in ("logo_wepower.png", "logo.png"):
        ruta = os.path.join(AQUI, nombre)
        if os.path.exists(ruta):
            with open(ruta, "rb") as f:
                return "data:image/png;base64," + base64.b64encode(f.read()).decode()
    return ""


LOGO = _logo_data_uri()


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
        "en la planta. Se cotiza caso por caso porque depende de tu curva de "
        "consumo mes a mes, no solo de tu promedio.",

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
        "Para la proyección. Se asume que la tarifa de red y el precio de WE "
        "Power suben lo mismo cada año, así que el ahorro crece en pesos pero "
        "el porcentaje de tu factura se mantiene.",

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

ESTILOS = """
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>

/* ---------- Tipografia ----------
   Streamlit dibuja sus iconos (la flecha de cerrar la barra lateral, el "?"
   de las ayudas) con una fuente de iconos. Si se les cambia la letra, en vez
   del icono sale su nombre escrito. Por eso la regla no los toca. */
html, body, .stApp, button, input, textarea, select {
    font-family: Inter, "Source Sans Pro", -apple-system, sans-serif;
}
[data-testid="stIconMaterial"], .material-icons, .material-symbols-rounded,
span[class*="material"] { font-family: "Material Symbols Rounded" !important; }

/* ---------- Franja azul de arriba, de borde a borde ----------
   El bloque principal de Streamlit tiene un ancho maximo y padding propios.
   Los margenes negativos los cancelan para que la franja llegue hasta los
   bordes de la ventana, igual que la del informe en PDF. */
/* La barra de herramientas de Streamlit (el menu de arriba a la derecha) se
   pinta del mismo azul: si no, queda una franja blanca encima y la banda se
   ve como un recorte pegado en medio de la pagina. */
[data-testid="stHeader"] { background: AZUL; border: none; box-shadow: none; }
[data-testid="stHeader"] * { color: #fff !important; }
/* Esa barra mide 60px y flota encima del contenido; Streamlit deja 96px de
   aire debajo para que no tape nada. Bajandolo a esos mismos 60px, la banda
   arranca justo donde termina la barra y las dos se ven como una sola. */
[data-testid="stMainBlockContainer"] { padding-top: 60px !important; }
/* Streamlit separa un elemento de otro con 1rem de aire, y arriba de la banda
   hay un elemento invisible suyo. Ese aire dejaba una tira blanca entre la
   barra y la banda: se veian DOS franjas azules en vez de una. El margen
   negativo de arriba se lo come. */
.franja {
    background: AZUL;
    margin: -1rem -100rem 2.2rem -100rem;
    padding: 1.1rem 100rem 1.1rem 100rem;
    border-bottom: 3px solid NARANJA;
    display: flex; align-items: center; gap: 1rem;
    position: relative; overflow: hidden;
}
.franja img { height: 42px; position: relative; z-index: 1; }
.franja .lema {
    margin-left: auto; color: #fff; opacity: .82;
    font-size: .82rem; letter-spacing: .04em; text-transform: uppercase;
    position: relative; z-index: 1;
}

/* ---------- Titulos ---------- */
h1 { color: AZUL !important; font-weight: 800 !important;
     letter-spacing: -.03em; font-size: 2.6rem !important;
     line-height: 1.12; }
/* Los subtitulos de seccion en naranja, con una regla fina debajo: es el
   mismo tratamiento que tienen en el informe impreso. */
h2, h3 {
    color: NARANJA_TEXTO !important; font-weight: 700 !important;
    letter-spacing: -.01em;
}
[data-testid="stHeadingWithActionElements"] h3 {
    border-bottom: 1.5px solid #EFE2CA; padding-bottom: .45rem;
}

/* ---------- Las cifras ---------- */
[data-testid="stMetricValue"] { color: AZUL; font-weight: 700; }
[data-testid="stMetricLabel"] p {
    font-size: .78rem !important; letter-spacing: .06em;
    text-transform: uppercase; color: GRIS !important; font-weight: 600;
}

/* ---------- Tarjetas de los planes ---------- */
[class*="st-key-plan-"] {
    background: GRIS_CLARO; border: 1px solid #E3EAF4 !important;
    border-radius: 12px !important; padding: .3rem .9rem .5rem .9rem !important;
    transition: box-shadow .15s ease, transform .15s ease;
}
[class*="st-key-plan-"]:hover {
    box-shadow: 0 8px 22px rgba(0,65,145,.11); transform: translateY(-2px);
}
/* Las tarjetas son angostas: con el tamano que Streamlit le pone por defecto
   a st.metric, "A tu medida" se corta con puntos suspensivos. */
[class*="st-key-plan-"] [data-testid="stMetricValue"] {
    font-size: 1.45rem; white-space: normal; line-height: 1.2;
}

/* ---------- Barras de avance ----------
   La barra son dos capas: la pista, que es el fondo, y dentro un div que se
   corre hacia la izquierda para tapar la parte que falta. El color va en ese
   div de adentro. */
[data-testid="stProgressBarTrack"] { background: #DCE5F1 !important; }
/*  Con degradado la barra enganaba: el div de adentro se corre hacia la
    izquierda, asi que una cobertura del 30 % dejaba a la vista el extremo
    naranja y se veia "mas fuerte" que una del 80 %. Color plano. */
[data-testid="stProgressBarTrack"] > div { background: AZUL !important; }

/* ---------- Botones ---------- */
.stButton button, .stDownloadButton button, .stFormSubmitButton button {
    border-radius: 8px; font-weight: 600; letter-spacing: .01em;
}
button[kind="primary"], button[kind="primaryFormSubmit"] {
    background: AZUL !important; border-color: AZUL !important;
}
button[kind="primary"]:hover, button[kind="primaryFormSubmit"]:hover {
    background: NARANJA_TEXTO !important; border-color: NARANJA_TEXTO !important;
}

/* ---------- Barra lateral ---------- */
[data-testid="stSidebar"] {
    background: GRIS_CLARO; border-right: 1px solid #E3EAF4;
}
[data-testid="stSidebar"] h2 { color: AZUL !important; }

/* ---------- Separadores ---------- */
hr { border-top: 1px solid #E3EAF4 !important; }

/* ---------- Los textos de siempre ---------- */
.etiqueta  { font-size: .75rem; letter-spacing: .08em; text-transform: uppercase;
             color: #2E7D32; font-weight: 700; margin-bottom: .2rem; }
.etiqueta-gris { font-size: .75rem; letter-spacing: .08em; text-transform: uppercase;
             color: #888; font-weight: 700; margin-bottom: .2rem; }
.bajada    { font-size: 1.45rem; font-weight: 600; color: NARANJA_TEXTO;
             margin: -.6rem 0 1.4rem 0; letter-spacing: -.01em; }
.pilar     { font-size: .92rem; color: #444; }
/* Imita el st.caption, pero admite HTML: lo necesitamos para el <abbr>. */
.nota      { font-size: .875rem; color: rgba(49,51,63,.6); margin-top: -.5rem; }
.nota abbr { text-decoration: underline dotted; cursor: help; }

/* ---------- Los tres pilares, como tarjetas ---------- */
.pilar-caja {
    background: GRIS_CLARO; border: 1px solid #E3EAF4; border-radius: 12px;
    padding: 1rem 1.1rem; height: 100%;
}
.pilar-caja .tit {
    color: AZUL; font-weight: 700; margin-bottom: .35rem; font-size: 1rem;
}

/* ---------- Pie ---------- */
.pie {
    background: AZUL_OSCURO; color: #fff; border-radius: 12px;
    padding: 1.1rem 1.4rem; font-size: .82rem; opacity: .95;
    margin-top: 1rem;
}
.pie b { color: NARANJA; }
</style>
"""

#  Los colores se escriben una sola vez, arriba, y se sustituyen aqui: asi no
#  quedan veinte codigos de color regados por el CSS.
for _clave, _valor in (("AZUL_OSCURO", AZUL_OSCURO), ("AZUL", AZUL),
                       ("NARANJA_TEXTO", NARANJA_TEXTO), ("NARANJA", NARANJA),
                       ("GRIS_CLARO", GRIS_CLARO), ("GRIS", GRIS)):
    ESTILOS = ESTILOS.replace(_clave, _valor)

#  Una linea en blanco dentro del bloque HTML hace que Markdown lo dé por
#  terminado y pinte el resto del CSS como texto en la pagina. Se quitan aqui
#  para poder escribir el CSS de arriba con aire y que igual funcione.
st.markdown("\n".join(l for l in ESTILOS.splitlines() if l.strip()),
            unsafe_allow_html=True)

#  La franja con el logo, arriba del todo.
st.markdown(
    f"""<div class="franja">
          {'<img src="' + LOGO + '">' if LOGO else '<b style="color:#fff">WE POWER</b>'}
          <span class="lema">Comunidades energéticas</span>
        </div>""",
    unsafe_allow_html=True)


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

    #  Se escoge el DESCUENTO, no el precio: es el dato que se negocia. El
    #  precio sale de ahí y se muestra abajo, en una casilla bloqueada para
    #  que se vea que es un resultado y no algo que se escribe.
    opcion = st.segmented_control(
        "Descuento sobre CU asignado", DESCUENTOS,
        default=DESCUENTO_INICIAL, help=AYUDA["descuento_cu"])

    #  Sin descuento escogido se calcula con 0 %, no se bloquea la página ni se
    #  cae al valor inicial (eso último mostraba una cifra como si alguien la
    #  hubiera elegido). Con 0 % el precio es el "precio neutro": la comunidad
    #  no cede nada de tarifa y el ahorro viene solo de la contribución.
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

    #  El tope no es un capricho: con más de ANIOS_MAXIMOS la tabla de la
    #  proyección se pasa de la página 4 del informe y el PDF sale con una
    #  página extra medio vacía. Está medido, no estimado.
    anios = st.number_input("Período de proyección (años)",
                            min_value=1, max_value=ANIOS_MAXIMOS, value=5, step=1,
                            help=AYUDA["anios"])

    st.divider()
    st.caption(f"Planta: {num(sim.GENERACION_MENSUAL_KWH)} kWh/mes")

contrib = sim.CONTRIBUCION if contribuye else 0.0



# =========================================================
# BLOQUE 1 — HERO
# =========================================================

st.title("Ahorra en tu factura con WE Power")
#  Va como texto y no como st.subheader: no es una seccion de la pagina, es
#  la segunda linea del titulo, y con el estilo de seccion se leia como si
#  empezara un bloque nuevo.
st.markdown("<div class='bajada'>sin invertir un solo peso "
            "y sin instalar un solo panel.</div>",
            unsafe_allow_html=True)

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
#  El servicio está pensado para empresas. Por debajo del mínimo no se cotiza:
#  el reparto de la planta no da para consumos residenciales.
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


# --- Los tres planes, calculados ------------------------------------------
pde_bas = sim.pde_escenario_minimo(consumo)
pde_est = sim.pde_por_cobertura(sim.PLAN_ESTANDAR, consumo)

#  El Premium NO se calcula ni se muestra en cifra: se cotiza caso por caso.
#  Dos razones. (1) Al cubrir el 100 % del consumo promedio, en un mes flojo
#  sobra energía, y todavía no está definido si al usuario se le factura lo
#  asignado o solo lo que alcanzó a usar — la diferencia mueve millones.
#  (2) El cupo depende de la energía libre que tenga la planta ese momento.
#  Poner un número aquí sería prometer algo que no podemos sostener.

r_bas = sim.balance_mensual(consumo, pde_bas, cu, cv, cu_ce, contrib)
r_est = sim.balance_mensual(consumo, pde_est, cu, cv, cu_ce, contrib)

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
    st.metric("Ahora pagas (entre las dos)", cop(r["factura_con"]),
              "-" + cop(r["ahorro_mes"]).replace("$ ", ""),
              delta_color="inverse", help=AYUDA["despues"])
    st.caption(f"{num(r['asignada'])} kWh se te descuentan de la factura; el "
               f"resto lo pagas al precio de siempre.")

st.markdown("**¿De qué se compone lo que vas a pagar?**")
#  Los dos primeros renglones iban al MISMO destinatario —el comercializador—
#  y verlos separados confundía. Se juntan en uno solo: el usuario recibe dos
#  cobros, de dos empresas distintas. Así de simple.
pago_comercializador = r["pago_red"] + r["cargo_cv"]

st.dataframe(pd.DataFrame([
    {"Concepto": "Lo que le sigues pagando a tu comercializador",
     "Valor": cop(pago_comercializador)},
    {"Concepto": "Lo que le pagas a WE Power",
     "Valor": cop(r["pago_ce"])},
    {"Concepto": "TOTAL, ENTRE LAS DOS FACTURAS", "Valor": cop(r["factura_con"])},
]), hide_index=True, width='stretch')

st.caption(f"Recibirás **dos facturas**: la de tu comercializador, como siempre, "
           f"y la del club. "
           f"Tu comercializador te sigue facturando toda la energía; ese cobro "
           f"junta dos cosas: los {num(r['energia_red'])} kWh que no alcanzamos a "
           f"cubrir, al precio de siempre, y el cargo que te hace por los "
           f"{num(r['exc1'])} kWh que sí cubrimos.")

st.caption(esc(f"Antes: {cop(r['factura_sin'])}.  Ahora: {cop(r['factura_con'])}.  "
               f"Te quedan {cop(r['ahorro_mes'])} en el bolsillo cada mes, "
               f"{cop(r['ahorro_anual'])} al año."))


# =========================================================
# BLOQUE 4 — POR CADA kWh
# =========================================================

st.divider()
st.subheader("Por cada kWh que te cubrimos")

k1, k2, k3 = st.columns(3)
with k1:
    st.metric("Ese kWh en la red", cop(au["costo_red"], 2), help=AYUDA["kwh"])
    st.caption("Precio de la energía más el 20 % de contribución.")
with k2:
    st.metric("Ese kWh con WE Power", cop(cv + cu_ce, 2))
    st.caption("No paga contribución: es el valor del kWh del club más el "
               "componente de comercialización.")
with k3:
    st.metric("Te ahorras", cop(au["total"], 2),
              pct(au["descuento_efectivo"], 1) + " menos", delta_color="off")
    st.caption("En cada kWh que alcanzamos a cubrir.")



# =========================================================
# BLOQUE 5 — LOS PLANES
# =========================================================

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
        #  La "key" le pone a la tarjeta la clase CSS st-key-plan-...: es el
        #  unico enganche estable que da Streamlit para darle estilo a un
        #  contenedor concreto. Sin ella habria que adivinar nombres de clase
        #  que cambian en cada version.
        with st.container(border=True, key="plan-" + nombre.lower()):
            st.metric(nombre, cop(res["ahorro_mes"]), help=ayuda)
            st.caption(esc(f"al mes  ·  {millones(res['ahorro_anual'])} al año  ·  "
                           f"{pct(res['ahorro_pct'], 1)} de tu factura"))
            st.progress(min(1.0, res["cobertura"]))
            st.caption(f"Cubrimos el {pct(res['cobertura'], 0)} de tu consumo")
            st.caption(f":gray[{pie}]")

with p3:
    with st.container(border=True, key="plan-premium"):
        st.metric("Premium", "A tu medida", help=AYUDA["premium"])
        st.caption("Cubrimos hasta el 100 % de tu consumo.")
        st.progress(1.0)
        st.caption("Se cotiza contigo")
        st.caption(":gray[Cupo limitado.]")

st.info("**¿Te interesa el plan Premium?** Es a la medida: revisamos tu consumo "
        "mes a mes y te pasamos la cifra. **Comunícate con nosotros.**")

#  Ningún usuario puede recibir más de cierta energía al mes, así que con
#  consumos muy altos el Básico y el Estándar terminan dando lo mismo. Se le
#  explica sin nombrar el tope ni la norma.
if abs(pde_bas - pde_est) < 1e-9:
    st.warning("Con tu consumo, el Básico y el Estándar te dan lo mismo: ya "
               "estarías recibiendo el máximo que le podemos asignar a un solo "
               "usuario. **Comunícate con nosotros** para revisar tu caso.")


# =========================================================
# BLOQUE 6 — DE DÓNDE SALE
# =========================================================

st.divider()
st.subheader("¿De dónde sale el ahorro?")

PILARES = [
    ("⚡ Energía más barata",
     "El kWh que cubrimos te sale más barato que el que te cobra tu "
     "comercializador."),
    ("🧾 Sin contribución",
     "Los kWh que cubrimos salen de tu consumo facturado, así que no pagan "
     "el 20 % de contribución."),
    ("📄 Tu factura de siempre",
     "El comercializador te descuenta la energía que pusimos nosotros. No "
     "cambias de operador."),
]

for col, (titulo, texto) in zip(st.columns(3), PILARES):
    with col:
        st.markdown(f"<div class='pilar-caja'><div class='tit'>{titulo}</div>"
                    f"<div class='pilar'>{texto}</div></div>",
                    unsafe_allow_html=True)


# =========================================================
# BLOQUE 7 — CONFIANZA
# =========================================================

#  Cuantos miembros tiene hoy la comunidad no le dice nada al cliente y
#  ademas es un dato que envejece. Fuera.
st.markdown(
    f"<div class='pie'><b>{num(sim.GENERACION_ANUAL_KWH)} kWh/año</b> de "
    f"generación &nbsp;·&nbsp; <b>100 % solar</b><br>"
    f"Amparado por las Resoluciones CREG 174 de 2021 y 101 072 de 2025.</div>",
    unsafe_allow_html=True)


# =========================================================
# BLOQUE 8 — PROYECCIÓN
# =========================================================

#  Se calcula aquí afuera porque el informe en PDF también la necesita.
proy = sim.proyectar(consumo, pde_actual, cu, cv, cu_ce, contrib, int(anios))

with st.expander("Ver cómo crece tu ahorro con los años"):

    #  Los dos porcentajes de inflación se pueden cambiar en simulador_ce.py,
    #  así que el texto no puede dar por hecho que son iguales: tiene que
    #  seguir al dato. Hoy los dos están en 5 %.
    if abs(sim.INFLACION_RED_ANUAL - sim.INFLACION_CE_ANUAL) < 1e-9:
        efecto = ("como suben lo mismo, tu ahorro crece en pesos año tras año, "
                  "pero sigue siendo el mismo porcentaje de tu factura")
    elif sim.INFLACION_RED_ANUAL > sim.INFLACION_CE_ANUAL:
        efecto = ("como la red sube más rápido, la brecha se abre y tu ahorro "
                  "crece año tras año, también como porcentaje de tu factura")
    else:
        efecto = ("como el precio de la comunidad sube más rápido que la red, "
                  "la brecha se cierra y tu ahorro pierde terreno con los años")
    st.caption(f"Con el plan Estándar. La tarifa de red sube "
               f"{pct(sim.INFLACION_RED_ANUAL, 1)} al año y el precio de WE Power "
               f"{pct(sim.INFLACION_CE_ANUAL, 1)}: {efecto}.")

    st.dataframe(pd.DataFrame([{
        "Año":               p["anio"],
        "Ahorro del año":    cop(p["ahorro_anual"]),
        "% de tu factura":   pct(p["ahorro_pct"], 1),
        "Ahorro acumulado":  cop(p["acumulado"]),
    } for p in proy]), hide_index=True, width='stretch')

    st.line_chart(pd.DataFrame({"Ahorro acumulado": [p["acumulado"] for p in proy]},
                               index=[f"Año {p['anio']}" for p in proy]))

    st.caption("El acumulado son pesos corrientes, sin traer a valor presente.")

# =========================================================
# BLOQUE 9 — DATOS PARA IMPRIMIR EL INFORME   [ BORRADOR ]
# =========================================================
#  ESTO ES UN ESQUELETO, NO ESTÁ TERMINADO.
#
#  Lo que falta decidir antes de darle forma:
#    1. ¿Qué es "capacidad"? ¿La potencia contratada del usuario, la de su
#       frontera, o la de la planta? Cambia de dónde sale el dato.
#    2. ¿El informe se descarga (PDF/HTML) o se le envía a WE Power?
#    3. ¿Qué campos son obligatorios? Hoy no se valida ninguno.
#    4. Habeas data (Ley 1581 de 2012): recoger nombre, teléfono y dirección
#       es tratamiento de datos personales. Antes de que esto salga a
#       producción hace falta la autorización del titular, decir para qué se
#       usan y quién es el responsable. El aviso de abajo es un marcador.
#
#  Por ahora el botón no genera nada: solo muestra cómo quedaría la cabecera
#  del informe con lo que se escribió.

st.divider()

if informe_pdf is None:
    if _error_informe == "no-existe":
        st.warning("Para generar el informe en PDF falta el archivo "
                   "**informe_pdf.py** en la misma carpeta que esta app.")
    else:
        st.error("El archivo **informe_pdf.py** está, pero no cargó.")

    #  Diagnóstico: en vez de adivinar, que la app diga qué ve de verdad.
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

#  Las casillas van sueltas y no dentro de un st.form: es lo que permite que
#  el filtro de escritura actúe mientras se llena, y no solo al enviar.
#  Los placeholders son genéricos a propósito: un nombre de ejemplo se
#  confunde con un dato ya escrito.
with st.container(border=True):
    f1, f2 = st.columns(2)
    with f1:
        nombre = st.text_input("Nombre completo", placeholder="Nombre y apellido",
                               key="f_nombre",
                               on_change=solo_letras, args=("f_nombre",))
        telefono = st.text_input("Teléfono", placeholder="0000000000",
                                 key="f_telefono",
                                 on_change=solo_digitos, args=("f_telefono",))
        ciudad = st.text_input("Ciudad", placeholder="Ciudad",
                               key="f_ciudad",
                               on_change=solo_letras, args=("f_ciudad",))
        #  Sin selección, el informe dice "su comercializador" a secas, que es
        #  lo que dice hoy. Nunca queda un hueco ni un guion en la página.
        comercializador = st.selectbox(
            "Comercializador del cliente", COMERCIALIZADORES,
            index=None, placeholder="¿Cuál es su comercializador?",
            key="f_comercializador",
            help="Sale en el informe. Si no lo escoges, el informe dice "
                 "«su comercializador», sin nombre.")
        if comercializador == "Otro":
            comercializador = st.text_input(
                "¿Cuál?", placeholder="Nombre del comercializador",
                key="f_comercializador_otro")
    with f2:
        direccion = st.text_input("Dirección", placeholder="Dirección del predio",
                                  key="f_direccion")
        correo = st.text_input("Correo electrónico",
                               placeholder="nombre@empresa.com",
                               key="f_correo",
                               help="A este correo te llega la oferta.")
        fecha = st.date_input("Fecha del informe", value=datetime.date.today(),
                              key="f_fecha")

    #  Los datos del asesor NO se editan aquí: son de WE Power, no del cliente.
    #  Se cambian en las constantes ASESOR_* del principio de este archivo.
    st.caption(f"Tu asesor: **{ASESOR_NOMBRE}** · {ASESOR_TEL} · {ASESOR_MAIL}")

    st.caption("Al continuar autorizas a WE Power a usar estos datos para "
               "contactarte sobre esta cotización.  *(texto provisional: falta "
               "redactar la autorización de tratamiento de datos)*")

    generar = st.button("Generar informe", type="primary")

#  El PDF se guarda en session_state: al hacer clic en "Descargar" Streamlit
#  vuelve a correr la página entera, y sin esto el botón desaparecería.
if generar:
    if not nombre.strip():
        st.error("Escribe al menos el nombre para generar el informe.")
    else:
        datos = informe_pdf.armar_datos(
            {"nombre": nombre, "telefono": telefono, "direccion": direccion,
             "ciudad": ciudad, "correo": correo,
             "comercializador": comercializador,
             "fecha": fecha.strftime("%d/%m/%Y"),
             "asesor_nombre": ASESOR_NOMBRE, "asesor_tel": ASESOR_TEL,
             "asesor_mail": ASESOR_MAIL},
            sim, r, au, proy, consumo, cu, cv, cu_ce)
        base = "Informe WE Club - " + (nombre.strip() or "cliente")
        #  El HTML siempre se puede generar: es texto, no depende de nada.
        st.session_state["html"] = informe_pdf.construir_html(datos).encode("utf-8")
        st.session_state["html_nombre"] = base + ".html"
        st.session_state["archivo_nombre"] = base + ".pdf"
        try:
            st.session_state["pdf"] = informe_pdf.generar_pdf(datos)
            st.session_state.pop("pdf_error", None)
        except Exception as err:
            #  No se traga el error: WeasyPrint puede fallar por no estar
            #  instalado O por faltarle librerías del sistema, y son cosas
            #  distintas. Sin ver el mensaje real no se sabe cuál es.
            import traceback
            st.session_state.pop("pdf", None)
            st.session_state["pdf_error"] = traceback.format_exc()

if st.session_state.get("pdf"):
    st.success("Informe listo.")
    st.download_button("Descargar informe en PDF", st.session_state["pdf"],
                       file_name=st.session_state["archivo_nombre"],
                       mime="application/pdf", type="primary")

elif st.session_state.get("html"):
    #  Plan B: el mismo informe, en HTML. Se abre en el navegador y desde ahí
    #  se imprime a PDF (Ctrl+P). Sale idéntico porque es la misma plantilla.
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
