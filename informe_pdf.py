# =========================================================
#  INFORME EN PDF — WE CLUB · WE POWER
# =========================================================
#
#  Este archivo NO calcula nada. Recibe los números que la interfaz ya
#  calculó y los datos que el usuario escribió en el formulario, los mete
#  en una plantilla HTML y la convierte en PDF.
#
#  Si un número sale mal aquí, el error está en simulador_ce.py, no acá.
#
#  Necesita WeasyPrint. En Streamlit Cloud hace falta un packages.txt con
#  las librerías del sistema (ver el archivo en el repo).
# =========================================================

import os
import base64
import datetime

AQUI = os.path.dirname(os.path.abspath(__file__))

# --- Colores de la marca (sacados del logo) --------------------------------
AZUL = "#004191"
AZUL_OSCURO = "#00305F"
NARANJA = "#E2A03C"
NARANJA_TEXTO = "#C07B14"   # el del logo aclara demasiado sobre blanco

#  Quién estructura el proyecto y administra la comunidad. Maira anotó "iría
#  el nombre de la SPV" y Ricardo escribió al lado "We Club", que es lo que
#  quedó. Si la SPV termina teniendo una razón social distinta que deba salir
#  en la oferta, se cambia aquí y en ningún otro sitio.
NOMBRE_SPV = "We Club"
GRIS = "#5A6472"
GRIS_CLARO = "#EEF1F6"


def _logo_base64():
    """Mete el logo dentro del HTML para no depender de rutas al imprimir."""
    for nombre in ("logo_wepower.png", "logo.png"):
        ruta = os.path.join(AQUI, nombre)
        if os.path.exists(ruta):
            with open(ruta, "rb") as f:
                return "data:image/png;base64," + base64.b64encode(f.read()).decode()
    return ""


# --- Formato colombiano (copiado a propósito: este archivo es autónomo) ----

def cop(v, d=0):
    return "$ " + f"{v:,.{d}f}".replace(",", "@").replace(".", ",").replace("@", ".")


def pct(v, d=1):
    return f"{v * 100:,.{d}f}".replace(",", "@").replace(".", ",").replace("@", ".") + " %"


def num(v, d=0):
    return f"{v:,.{d}f}".replace(",", "@").replace(".", ",").replace("@", ".")


# =========================================================
# LA PLANTILLA
# =========================================================

CSS = f"""
@page {{
    size: A4;
    margin: 16mm 14mm 14mm 14mm;
    @bottom-center {{
        content: "WE CLUB · Comunidades energéticas          " counter(page) " / " counter(pages);
        font-size: 7.5pt; color: {GRIS};
    }}
}}
@page :first {{ margin: 0; @bottom-center {{ content: ""; }} }}

* {{ box-sizing: border-box; }}
body {{ font-family: Carlito, Calibri, "DejaVu Sans", Arial, sans-serif;
        color: {AZUL_OSCURO}; font-size: 10pt; line-height: 1.5; margin: 0; }}
h1 {{ font-size: 21pt; color: {AZUL}; margin: 0 0 2mm 0; font-weight: 700; }}
/* Los títulos de sección: naranja, con una regla fina debajo. */
h2 {{ font-size: 17pt; color: {NARANJA_TEXTO}; margin: 0 0 4mm 0;
      font-weight: 700; letter-spacing: -.2pt;
      border-bottom: 1.2px solid #EADCC4; padding-bottom: 2mm; }}
h3 {{ font-size: 11pt; color: {AZUL}; margin: 0 0 2mm 0; font-weight: 700; }}
p  {{ margin: 0 0 2.5mm 0; }}
.pagina {{ page-break-after: always; }}
.pagina:last-child {{ page-break-after: auto; }}
.gris {{ color: {GRIS}; }}
.chico {{ font-size: 8pt; }}

/* --- Portada --- */
.portada {{ width: 210mm; height: 297mm; display: flex;
            page-break-after: always; }}
.pt-izq {{ width: 78mm; background: {AZUL}; color: #fff; padding: 20mm 12mm;
           position: relative; overflow: hidden; }}
/* El motivo de la portada de la presentación de WE Club: cuadraditos
   redondeados unidos por líneas finas, como una red. Va en SVG dentro del
   propio HTML para no depender de otra imagen, y detrás del texto. */
.pt-izq .malla {{ position: absolute; left: 0; top: 0;
                  width: 78mm; height: 297mm; z-index: 0; }}
.pt-izq > *:not(.malla) {{ position: relative; z-index: 1; }}
.pt-izq img {{ width: 24mm; margin-bottom: 14mm; }}
.pt-izq .marca {{ font-size: 19pt; font-weight: bold; letter-spacing: -.3pt; }}
.pt-izq .club {{ color: {NARANJA}; font-size: 30pt; font-weight: bold;
                 margin: 1mm 0 0 0; line-height: 1; }}
.pt-izq .linea {{ width: 34mm; height: 2px; background: {NARANJA}; margin: 7mm 0; }}
.pt-izq .lema {{ font-size: 11pt; line-height: 1.5; opacity: .93; }}
.pt-izq .web {{ position: absolute; bottom: 20mm; font-size: 9pt; opacity: .8; }}
.pt-der {{ flex: 1; padding: 20mm 16mm; }}
.pt-der .saludo {{ font-size: 30pt; font-weight: 700; color: {AZUL};
                   margin: 0 0 7mm 0; line-height: 1.1; letter-spacing: -.5pt; }}
.pt-der p {{ font-size: 10pt; line-height: 1.55; margin-bottom: 3.5mm; }}
.pt-der .cierre {{ color: {AZUL}; font-weight: bold; }}
.cifras {{ display: flex; gap: 3mm; margin: 6mm 0; }}
.cifra-caja {{ flex: 1; background: {GRIS_CLARO}; border-radius: 2mm;
               padding: 3mm; text-align: center; }}
.cifra-caja b {{ display: block; color: {AZUL}; font-size: 13pt; }}
.cifra-caja span {{ font-size: 7.5pt; color: {GRIS}; }}
.asesor-portada {{ border-top: 2px solid {NARANJA}; padding-top: 4mm; margin-top: 6mm; }}

/* El sello del descuento: lo pidieron resaltado, no como una frase mas. */
.sello {{ display: inline-block; background: {NARANJA}; color: #fff;
          font-weight: 700; font-size: 11.5pt; border-radius: 2mm;
          padding: 2mm 4mm; }}

/* Las dos facturas, una al lado de la otra. */
.factura {{ border: 1px solid #D8E0EC; border-radius: 2mm; padding: 4mm;
            text-align: center; }}
.factura .de {{ font-size: 8pt; letter-spacing: .5pt; color: {GRIS};
                text-transform: uppercase; margin-bottom: 1.5mm; }}
.factura .val {{ font-size: 17pt; font-weight: 700; color: {AZUL}; }}
.factura .qué {{ font-size: 8pt; color: {GRIS}; margin-top: 1.5mm; }}
.suma {{ background: {AZUL}; color: #fff; border-radius: 2mm; padding: 3mm;
         text-align: center; margin-top: 3mm; }}
.suma b {{ font-size: 14pt; }}

/* La línea de tiempo de la afiliación: la pidieron como dibujo, no como
   tabla de texto. Va en SVG dentro del propio HTML, sin imagen aparte. */
.crono {{ width: 100%; height: 52mm; }}

/* --- Encabezado de páginas interiores --- */
/* El logo trae su propio fondo azul, así que sobre blanco queda como una
   estampilla pegada. Metiéndolo en una banda del MISMO azul, el recuadro
   desaparece y el logo se funde con la página. La banda sangra hasta los
   bordes usando márgenes negativos que cancelan los de @page. */
.cab {{ background: {AZUL}; margin: -16mm -14mm 7mm -14mm;
        padding: 4.5mm 14mm; display: flex; align-items: center;
        border-bottom: 2.5px solid {NARANJA}; }}
.cab img {{ width: 13mm; }}
.cab .t {{ flex: 1; text-align: right; font-size: 8.5pt; color: #fff;
           opacity: .85; letter-spacing: .3pt; }}

/* --- Bloques --- */
.destacado {{ background: {AZUL}; color: #fff; border-radius: 3mm;
              padding: 7mm; text-align: center; margin: 4mm 0; }}
.destacado .cifra {{ font-size: 25pt; font-weight: bold; line-height: 1.1;
                     white-space: nowrap; }}
.destacado .sub {{ font-size: 10pt; opacity: .9; margin-top: 2mm; }}
.caja {{ background: {GRIS_CLARO}; border-radius: 2.5mm; padding: 4mm; }}
.caja-borde {{ border: 1px solid #D5DCE6; border-radius: 2.5mm; padding: 4mm; }}

table {{ width: 100%; border-collapse: collapse; font-size: 9pt; }}
th {{ background: #FBF3E4; color: {NARANJA_TEXTO}; text-align: left;
      padding: 2.5mm 3mm; font-size: 9pt; font-weight: 700; }}
td {{ padding: 2mm 3mm; border-bottom: 1px solid #E4E9F0; }}
td.n {{ text-align: right; white-space: nowrap; }}
tr.total td {{ font-weight: bold; color: {AZUL}; border-top: 1.5px solid {AZUL};
               border-bottom: none; }}

.cols {{ display: flex; gap: 5mm; }}
.col {{ flex: 1; }}
.dato {{ display: flex; border-bottom: 1px solid #E4E9F0; padding: 1.8mm 0; }}
.dato .k {{ width: 42%; color: {GRIS}; }}
.dato .v {{ flex: 1; font-weight: bold; }}

.paso {{ border-left: 3px solid {NARANJA}; padding: 0 0 0 4mm; margin-bottom: 4mm; }}
.paso .n {{ color: {NARANJA}; font-weight: bold; font-size: 8.5pt; }}

.barra {{ background: #E4E9F0; border-radius: 1mm; height: 5mm; margin: 1.5mm 0; }}

/* --- Las dos barras del kWh ---
   El ancho de cada bloque es proporcional a su valor, así que la comparación
   se entiende sin leer un número: la barra gris de arriba es el kWh de la red
   y la de abajo, del mismo largo, se parte en la energía del club, el cargo de
   comercialización y el hueco, que es el ahorro. */
.kbarras {{ margin-top: 2mm; }}
.kfila {{ display: flex; align-items: center; margin-bottom: 2.5mm; }}
.kfila .ket {{ width: 32mm; text-align: right; padding-right: 3mm;
               font-size: 8pt; color: {GRIS}; line-height: 1.25; }}
.kpista {{ flex: 1; height: 9mm; background: {GRIS_CLARO}; border-radius: 1.5mm;
           display: flex; overflow: hidden; }}
.kseg {{ display: flex; align-items: center; padding: 0 2.5mm; color: #fff;
         font-weight: 700; font-size: 9.5pt; white-space: nowrap; }}
.kred {{ background: {GRIS}; }}
.kclub {{ background: {AZUL}; }}
.kcom {{ background: #93A7C4; font-size: 8pt; padding: 0 1.5mm; }}
.khueco {{ flex: 1; display: flex; align-items: center; padding: 0 2.5mm;
           color: {NARANJA_TEXTO}; font-weight: 700; font-size: 9pt;
           white-space: nowrap; }}
.kleyenda {{ font-size: 7.5pt; color: {GRIS}; margin-top: 1mm; }}

/* El remate: la cifra del ahorro, sola y grande. */
.kremate {{ margin-top: 4mm; background: #FBF3E4; border: 1px solid #EAD9BA;
            border-radius: 2mm; padding: 4mm 6mm; display: flex;
            align-items: center; justify-content: center; gap: 5mm; }}
.kremate .kcifra {{ font-size: 26pt; font-weight: 700; color: {NARANJA_TEXTO};
                    line-height: 1; letter-spacing: -.5pt; white-space: nowrap; }}
.kremate .ktxt {{ font-size: 11pt; color: {AZUL_OSCURO}; line-height: 1.3; }}
.barra div {{ background: {AZUL}; height: 5mm; border-radius: 1mm; }}

ul {{ margin: 0 0 2mm 0; padding-left: 4.5mm; }}
li {{ margin-bottom: 1.5mm; }}
.nota {{ font-size: 7.5pt; color: {GRIS}; margin-top: 3mm; line-height: 1.4; }}

/* SOLO PANTALLA. Al imprimir manda @page; pero si alguien abre el HTML en el
   navegador no hay @page y el contenido se estira a lo ancho de la ventana.
   Aquí se dibujan hojas A4 centradas para que se vea igual que en papel. */
@media screen {{
    body {{ background: #6E7480; padding: 8mm 0; }}
    .portada, .pagina {{
        width: 210mm; min-height: 297mm; margin: 0 auto 8mm auto;
        background: #fff; box-shadow: 0 1mm 4mm rgba(0,0,0,.35);
        padding: 16mm 14mm; }}
    .portada {{ padding: 0; }}
    .aviso-print {{
        max-width: 210mm; margin: 0 auto 6mm auto; padding: 4mm 6mm;
        background: #FFF7E3; border-left: 4px solid {NARANJA};
        border-radius: 2mm; font-size: 10pt; color: #5A4A20; }}
}}
@media print {{ .aviso-print {{ display: none; }} }}
"""


#  Las cuatro etapas del cronograma. El ancho de cada tramo es proporcional
#  a sus semanas, así el dibujo no miente: el tramo de 10 semanas se ve cinco
#  veces más largo que el de 2.
ETAPAS = [
    ("Estudio de su consumo", 2, "Usted facilita la copia"),
    ("Firma de la afiliación", 2, "Usted firma"),
    ("Medidor y trámites", 10, "Lo gestiona We Club"),
    ("Puesta en marcha", 2, "Lo gestiona We Club"),
]


def _crono():
    """Dibuja el cronograma como una línea de tiempo en SVG."""
    total = sum(e[1] for e in ETAPAS)
    ancho, alto = 1000.0, 330.0
    margen, y = 10.0, 160.0
    util = ancho - margen * 2
    piezas = ["<svg class='crono' viewBox='0 0 %g %g'>" % (ancho, alto)]
    piezas.append("<line x1='%g' y1='%g' x2='%g' y2='%g' stroke='#D8E0EC' "
                  "stroke-width='3'/>" % (margen, y, ancho - margen, y))
    x = margen
    for i, (nombre, semanas, quien) in enumerate(ETAPAS):
        w = util * semanas / total
        color = AZUL if "We Club" in quien else NARANJA
        piezas.append("<rect x='%g' y='%g' width='%g' height='20' rx='10' "
                      "fill='%s'/>" % (x + 3, y - 10, w - 6, color))
        cx = x + w / 2
        piezas.append("<circle cx='%g' cy='%g' r='17' fill='#fff' stroke='%s' "
                      "stroke-width='3.5'/>" % (cx, y, color))
        piezas.append("<text x='%g' y='%g' text-anchor='middle' font-size='19' "
                      "font-weight='700' fill='%s'>%d</text>"
                      % (cx, y + 7, color, i + 1))
        #  Los rótulos van alternados, arriba y abajo, para que no se pisen
        #  cuando dos etapas cortas quedan pegadas.
        arriba = i % 2 == 0
        ty = y - 42 if arriba else y + 58
        #  Los rotulos de los tramos cortos son mas anchos que el tramo, asi
        #  que en los extremos se anclan al borde para no salirse del lienzo.
        anc, tx = "middle", cx
        if i == 0:
            anc, tx = "start", margen
        elif i == len(ETAPAS) - 1:
            anc, tx = "end", ancho - margen
        piezas.append("<text x='%g' y='%g' text-anchor='%s' font-size='21' "
                      "font-weight='700' fill='%s'>%s</text>"
                      % (tx, ty, anc, AZUL_OSCURO, nombre))
        piezas.append("<text x='%g' y='%g' text-anchor='%s' font-size='18' "
                      "fill='%s'>%d semanas · %s</text>"
                      % (tx, ty + (-24 if arriba else 24), anc, GRIS, semanas, quien))
        x += w
    #  El cierre, como una etiqueta y no como un renglon suelto.
    ancho_chip = 540.0
    piezas.append("<rect x='%g' y='%g' width='%g' height='36' rx='18' "
                  "fill='%s'/>" % (ancho - margen - ancho_chip, alto - 36,
                                   ancho_chip, AZUL))
    piezas.append("<text x='%g' y='%g' text-anchor='middle' font-size='18' "
                  "font-weight='700' fill='#fff'>Inicio del ahorro: primer mes "
                  "de operación</text>" % (ancho - margen - ancho_chip / 2, alto - 12))
    piezas.append("</svg>")
    return "".join(piezas)


def _cab(titulo, logo):
    # Si falta el archivo del logo, va el nombre en texto: el encabezado
    # no queda cojo y el informe se puede emitir igual.
    #  El texto de respaldo va en blanco: la banda del encabezado es azul, así
    #  que un texto azul sería invisible. Y dice We Club, que es la marca con
    #  la que se le habla al cliente.
    marca = ('<img src="' + logo + '">') if logo else (
        '<b style="color:#fff; font-size:11pt">WE CLUB</b>')
    return '<div class="cab">' + marca + '<div class="t">' + titulo + '</div></div>'


def _barras_kwh(d):
    """Las dos barras del kWh, a escala, más el remate con el ahorro.

    Todo sale de los mismos números que ya calculó el modelo. El 100 % de la
    escala es el kWh de la red, que siempre es el más caro de los dos (si no
    lo fuera no habría ahorro, y la página ni siquiera llega hasta aquí).
    """
    base = d["costo_red_kwh"]
    pc_club = d["cu_ce"] / base * 100
    pc_com = d["cv"] / base * 100
    pc_hueco = 100 - pc_club - pc_com

    #  Con el hueco muy angosto el rótulo no cabe y sale cortado. En ese caso
    #  se calla: la cifra grande de abajo ya lo dice, y más grande.
    rotulo = cop(d["ahorro_kwh"], 2) if pc_hueco >= 14 else ""
    #  Lo mismo con el cargo de comercialización, que es el bloque más angosto.
    com = cop(d["cv"], 2) if pc_com >= 11 else ""

    return f"""
  <div class="kbarras">
    <div class="kfila">
      <div class="ket">Hoy, comprado<br>a la red</div>
      <div class="kpista">
        <div class="kseg kred" style="width:100%">{cop(base, 2)}</div>
      </div>
    </div>
    <div class="kfila">
      <div class="ket">Con We Club</div>
      <div class="kpista">
        <div class="kseg kclub" style="width:{pc_club:.2f}%">{cop(d['cu_ce'], 2)}</div>
        <div class="kseg kcom" style="width:{pc_com:.2f}%">{com}</div>
        <div class="khueco">{rotulo}</div>
      </div>
    </div>
    <div class="kleyenda">
      <b style="color:{AZUL}">&#9632;</b> energía de We Club &nbsp;·&nbsp;
      <b style="color:#93A7C4">&#9632;</b> comercialización, que su comercializador
      le sigue cobrando &nbsp;·&nbsp; el espacio en blanco es lo que usted deja de pagar
    </div>
    <div class="kremate">
      <div class="kcifra">{cop(d['ahorro_kwh'], 2)}</div>
      <div class="ktxt">menos por cada kWh<br>que le cubrimos</div>
    </div>
  </div>"""


def _supuesto_inflacion(d):
    """El renglón de la inflación, redactado según los valores que haya.

    Los dos porcentajes viven en simulador_ce.py y se pueden cambiar. Si el
    texto dijera "suben lo mismo" a secas, el día que alguien los ponga
    distintos el informe estaría mintiendo. Así la frase sigue al dato.
    """
    red, ce = d["infl_red"], d["infl_ce"]
    if abs(red - ce) < 1e-9:
        return ("La tarifa de la red y el precio de We Club suben lo mismo cada "
                "año: <b>" + pct(red, 0) + "</b>.")
    return ("La tarifa de la red sube <b>" + pct(red, 0) + "</b> al año y el "
            "precio de We Club <b>" + pct(ce, 0) + "</b>.")


def _nombrar_comercializador(d):
    """«Su comercializador EPM» si se escogió; «Su comercializador» si no."""
    nombre = d.get("comercializador") or ""
    return "Su comercializador <b>" + nombre + "</b>" if nombre else "Su comercializador"


def construir_html(d):
    """d es un diccionario con TODO lo que va impreso. Ver armar_datos()."""
    logo = _logo_base64()
    logo_img = ('<img src="' + logo + '">') if logo else ""

    # ---------- proyección: barras proporcionales ----------
    tope = max(p["acumulado"] for p in d["proyeccion"]) or 1
    filas_proy = "".join(
        f'<tr><td>Año {p["anio"]}</td>'
        f'<td class="n">{cop(p["ahorro_anual"])}</td>'
        f'<td class="n">{pct(p["ahorro_pct"])}</td>'
        f'<td class="n">{cop(p["acumulado"])}</td>'
        f'<td style="width:34%"><div class="barra">'
        f'<div style="width:{p["acumulado"]/tope*100:.1f}%"></div></div></td></tr>'
        for p in d["proyeccion"])

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>{CSS}</style></head><body>

<div class="aviso-print">
  <b>Para guardarlo en PDF:</b> presione <b>Ctrl + P</b> (o <b>Cmd + P</b> en Mac)
  y elija <b>Guardar como PDF</b>. Este aviso no se imprime.
</div>

<!-- ============ 1. PORTADA ============ -->
<div class="portada">
  <div class="pt-izq">
    <svg class="malla" viewBox="0 0 78 297" preserveAspectRatio="none">
      <g stroke="#9DBEE8" stroke-opacity=".22" stroke-width=".25" fill="none">
        <path d="M10 150 L40 138 M40 138 L68 158 M68 158 L56 190 M56 190 L26 176
                 M26 176 L10 150 M26 176 L8 210 M8 210 L38 224 M38 224 L56 190
                 M38 224 L70 232 M38 224 L20 258 M8 210 L20 258 M70 232 L62 264
                 M20 258 L44 276 M44 276 L62 264 M68 158 L74 128"/>
      </g>
      <g fill="#9DBEE8" fill-opacity=".26">
        <rect x="8.6" y="148.6" width="2.8" height="2.8" rx=".7"/>
        <rect x="38.6" y="136.6" width="2.8" height="2.8" rx=".7"/>
        <rect x="66.6" y="156.6" width="2.8" height="2.8" rx=".7"/>
        <rect x="24.6" y="174.6" width="2.8" height="2.8" rx=".7"/>
        <rect x="54.6" y="188.6" width="2.8" height="2.8" rx=".7"/>
        <rect x="6.6" y="208.6" width="2.8" height="2.8" rx=".7"/>
        <rect x="36.6" y="222.6" width="2.8" height="2.8" rx=".7"/>
        <rect x="68.6" y="230.6" width="2.8" height="2.8" rx=".7"/>
        <rect x="18.6" y="256.6" width="2.8" height="2.8" rx=".7"/>
        <rect x="60.6" y="262.6" width="2.8" height="2.8" rx=".7"/>
        <rect x="42.6" y="274.6" width="2.8" height="2.8" rx=".7"/>
      </g>
    </svg>
    {logo_img}
    <div class="marca">WE POWER</div>
    <div class="club">WE CLUB</div>
    <div class="linea"></div>
    <div class="lema">Comunidades energéticas de WE Power.<br><br>
      Energía limpia, a menor costo y sin invertir en equipos.</div>
    <div class="web">wepower.com.co</div>
  </div>

  <div class="pt-der">
    <div class="saludo">¡Hola, {d['saludo']}!</div>

    <p>En <b>We Club</b> ponemos la energía del sol a disposición de su empresa.
    <b>We Club es una comunidad energética:</b> reunimos a varias empresas para
    comprar energía solar en conjunto y, al comprar entre muchos, el precio por
    kWh baja.</p>

    <p>Su empresa <b>sigue conectada con su operador de energía actual</b>. Nosotros
    le suministramos una parte de su consumo desde nuestras granjas solares, a una
    tarifa menor que la que paga hoy.</p>

    <p><b>No tiene que invertir un solo peso ni instalar un solo panel.</b>
    Generamos la energía en granjas solares cercanas y la inyectamos a la red
    para que usted pueda aprovecharla. Nosotros nos encargamos de los trámites;
    usted, de ahorrar.</p>

    <div class="cifras">
      <div class="cifra-caja"><b>+100 MW</b><span>gestionados</span></div>
      <div class="cifra-caja"><b>+50</b><span>proyectos en el país</span></div>
      <div class="cifra-caja"><b>100 %</b><span>solar</span></div>
    </div>

    <p class="cierre">En las páginas siguientes encontrará el ahorro estimado para
    su empresa, calculado con su propio consumo y con las tarifas que paga hoy.</p>

    <div class="asesor-portada">
      <p style="margin-bottom:1mm"><b>{d['asesor_nombre']}</b><br>
        {d['asesor_tel']}<br>{d['asesor_mail']}</p>
      <p class="chico gris" style="margin:0">{d['ciudad']} · {d['fecha']}
        {"· " + d['correo'] if d['correo'] else ""}</p>
    </div>
  </div>
</div>

<!-- ============ 2. SU AHORRO ============ -->
<div class="pagina">
  {_cab("Ahorro estimado para su empresa", logo)}
  <h2>Ahorro estimado para su empresa</h2>

  <div class="cols">
    <div class="col">
      <h3>Los datos de su empresa</h3>
      <div class="dato"><div class="k">Nombre</div><div class="v">{d['nombre']}</div></div>
      <div class="dato"><div class="k">Teléfono</div><div class="v">{d['telefono']}</div></div>
      <div class="dato"><div class="k">Dirección</div><div class="v">{d['direccion']}</div></div>
      <div class="dato"><div class="k">Ciudad</div><div class="v">{d['ciudad']}</div></div>
      <div class="dato"><div class="k">Correo</div><div class="v">{d['correo']}</div></div>
      <div class="dato"><div class="k">Consumo promedio</div><div class="v">{num(d['consumo'])} kWh/mes</div></div>
      <div class="dato"><div class="k">Tarifa que paga hoy</div><div class="v">{cop(d['cu'],2)} /kWh</div></div>
      <div class="dato"><div class="k">Plan</div><div class="v">Estándar</div></div>
    </div>
    <div class="col">
      <div class="destacado">
        <div style="font-size:10pt; opacity:.9">Ahorro estimado al año</div>
        <div class="cifra">{cop(d['ahorro_anual'])}</div>
        <div class="sub">{cop(d['ahorro_mes'])} cada mes</div>
      </div>
      <div class="caja">
        <h3 style="margin-top:0">Equivale a</h3>
        <p style="font-size:16pt; font-weight:bold; color:{AZUL}; margin:0">
          {pct(d['ahorro_pct'])} menos<br>
          <span style="font-size:9.5pt; font-weight:normal; color:{GRIS}">
            en su factura de energía</span></p>
        <p class="chico gris" style="margin:2mm 0 0 0">Es el
          <b>{pct(d['descuento'],0)}</b> de descuento aplicado sobre el
          <b>{pct(d['cobertura'],1)}</b> de su consumo que le cubrimos.</p>
      </div>
      <div class="caja-borde" style="margin-top:4mm">
        <h3 style="margin-top:0">Energía que le cubrimos</h3>
        <p style="margin:0"><b>{num(d['asignada'])} kWh al mes</b> generados en nuestras granjas solares</p>
        <div class="barra"><div style="width:{min(100, d['cobertura']*100):.0f}%"></div></div>
        <p class="chico gris" style="margin:0">Equivale aproximadamente al
          <b>{pct(d['cobertura'],0)}</b> de su consumo, y es sobre esa parte que
          le aplicamos el descuento. Su energía sigue llegando por la red de
          siempre: lo que cambia es el precio de esos kWh.</p>
      </div>
    </div>
  </div>

  <div class="caja" style="margin-top:5mm">
    <h3 style="margin-top:0">Cómo se calcula</h3>
    <p style="margin:0 0 3mm 0">Hoy cada kWh de la red le cuesta
    <b>{cop(d['costo_red_kwh'],2)}</b>, con la contribución incluida. Nosotros le
    vendemos esa energía a <b>{cop(d['cu_ce'],2)}</b> por kWh:
    <b>{cop(d['costo_red_kwh'] - d['cu_ce'],2)}</b> menos por cada kWh.</p>
    <p style="margin:0 0 3mm 0">Sobre esos mismos kWh su comercializador le sigue
    cobrando el costo de comercialización, <b>{cop(d['cv'],2)}</b> por kWh. Sumando
    las dos cosas, cada kWh que le cubrimos le queda en
    <b>{cop(d['costo_ce_kwh'],2)}</b>, y su ahorro real es de
    <b>{cop(d['ahorro_kwh'],2)}</b> por kWh.</p>
    <div class="sello">{pct(d['descuento'],0)} de descuento por cada kWh que le cubrimos</div>
    <p class="chico gris" style="margin:2mm 0 0 0">
      Las tarifas de energía se indexan periódicamente. Las cifras de esta oferta
      se calculan con las tarifas vigentes a la fecha y se actualizan con las
      indexaciones que apliquen.</p>
  </div>

  <p class="nota"><b>Es un estimado.</b> Está calculado con un consumo promedio de
  {num(d['consumo'])} kWh al mes. Su consumo cambia mes a mes y su ahorro también:
  en un mes de mayor consumo ahorra más, en uno de menor consumo ahorra menos.</p>
</div>

<!-- ============ 3. LA FACTURA ============ -->
<div class="pagina">
  {_cab("Su factura, antes y después", logo)}
  <h2>Su factura, antes y después</h2>

  <div class="caja-borde" style="text-align:center; margin-bottom:5mm">
    <div class="gris chico">ANTES PAGABA, EN UNA SOLA FACTURA</div>
    <div style="font-size:19pt; font-weight:bold; color:{GRIS}">{cop(d['factura_sin'])}</div>
    <div class="chico gris">todo su consumo comprado a la red</div>
  </div>

  <h3>Ahora recibe dos facturas</h3>
  <div class="cols">
    <div class="col factura">
      <div class="de">Factura de su comercializador</div>
      <div class="val">{cop(d['pago_comercializador'])}</div>
      <div class="qué">{num(d['energia_red'])} kWh al precio de siempre,
        más el costo de comercialización de los {num(d['exc1'])} kWh que le cubrimos</div>
    </div>
    <div class="col factura">
      <div class="de">Factura de We Club</div>
      <div class="val">{cop(d['pago_ce'])}</div>
      <div class="qué">{num(d['exc1'])} kWh de energía de la comunidad,
        a {cop(d['cu_ce'],2)} por kWh</div>
    </div>
  </div>
  <div class="suma">Entre las dos: <b>{cop(d['factura_con'])}</b> &nbsp;·&nbsp;
    <span style="color:{NARANJA}">−{cop(d['ahorro_mes'])} cada mes</span></div>

  <p class="nota" style="margin-top:4mm">Recibe <b>dos facturas</b>: la de su
  proveedor actual y la de la Comunidad We Club, cada una por la cantidad de
  energía correspondiente y con las tarifas que aplica cada uno.</p>

  <h3 style="margin-top:6mm">Por cada kWh que le cubrimos</h3>
  {_barras_kwh(d)}

</div>

<!-- ============ 4. PROYECCIÓN ============ -->
<div class="pagina">
  {_cab("Su ahorro con los años", logo)}
  <h2>Su ahorro con los años</h2>
  <p class="gris">Proyección a {len(d['proyeccion'])} años con el plan Estándar.</p>

  <table>
    <tr><th>Período</th><th style="text-align:right">Ahorro del año</th>
        <th style="text-align:right">% de su factura</th>
        <th style="text-align:right">Acumulado</th><th></th></tr>
    {filas_proy}
  </table>

  <div class="destacado" style="margin-top:6mm">
    <div style="font-size:10pt; opacity:.9">Ahorro acumulado en {len(d['proyeccion'])} años</div>
    <div class="cifra">{cop(d['acumulado_total'])}</div>
  </div>

  <div class="caja" style="margin-top:5mm">
    <h3 style="margin-top:0">Supuestos de la proyección</h3>
    <ul>
      <li>{_supuesto_inflacion(d)} Es un supuesto de trabajo y se ajusta con
        las indexaciones que rijan en cada período.</li>
      <li>Su consumo se mantiene. Si su consumo cambia, su ahorro cambia con él.</li>
      <li>Su participación en la comunidad se mantiene. Si se ajusta, el ahorro
        se recalcula sobre la nueva participación.</li>
    </ul>
  </div>
  <p class="nota">Las cifras son estimadas y dependen de su consumo real, de la
  tarifa que le cobre su comercializador en cada período y del incremento de los
  índices de indexación.</p>
</div>

<!-- ============ 5. QUÉ CAMBIA ============ -->
<div class="pagina">
  {_cab("Qué cambia y qué no cambia", logo)}
  <h2>Qué cambia y qué no cambia para su empresa</h2>

  <div class="cols">
    <div class="col caja">
      <h3 style="margin-top:0">Lo que NO cambia</h3>
      <ul>
        <li>{_nombrar_comercializador(d)} sigue siendo el mismo.</li>
        <li>La continuidad del servicio: si la granja no genera, su comercializador
          lo sigue atendiendo.</li>
        <li>Su empresa no pone capital ni compra equipos.</li>
        <li>No se requiere instalar paneles ni equipos de generación en su predio.</li>
        <li>No tiene que hacer trámites: nosotros los hacemos por usted.</li>
      </ul>
    </div>
    <div class="col caja">
      <h3 style="margin-top:0">Lo que sí cambia</h3>
      <ul>
        <li>Su medidor se reemplaza por un medidor inteligente, sin costo para usted.</li>
        <li>Parte de la energía que consume la genera una granja solar y se le acredita en su factura.</li>
        <li>Paga menos por esa energía: un descuento sobre el costo unitario que paga hoy.</li>
        <li>Recibe reportes de su consumo y de su ahorro.</li>
      </ul>
    </div>
  </div>

  <h3 style="margin-top:6mm">Quién es quién</h3>
  <table>
    <tr><td style="width:34%"><b>Granja solar</b></td>
        <td>Genera la energía solar de la que provendrá la parte de su consumo
            que le cubrimos.</td></tr>
    <tr><td><b>Comunidad energética</b></td>
        <td>Agrupa a los usuarios, fija las reglas y asigna la energía entre ellos.</td></tr>
    <tr><td><b>Su comercializador</b></td>
        <td>Compra, vende y factura la energía ante el mercado eléctrico. Sigue
            siendo el mismo de siempre.</td></tr>
    <tr><td><b>We Club</b></td>
        <td>Administra la comunidad, hace los trámites y traslada los beneficios
            a sus miembros.</td></tr>
    <tr><td><b>Su empresa</b></td>
        <td>Consume y paga. Delega en We Club la gestión y los trámites.</td></tr>
  </table>
  <p class="nota">{NOMBRE_SPV} estructura el proyecto, administra la comunidad y
  traslada sus beneficios a los miembros. La venta de energía la hace un
  comercializador. Operación amparada por las Resoluciones CREG 174
  de 2021 y 101 072 de 2025.</p>
</div>

<!-- ============ 6. CÓMO SE AFILIA ============ -->
<div class="pagina">
  {_cab("Cómo se afilia", logo)}
  <h2>Cómo se afilia: cinco pasos</h2>
  <p class="gris">Firmar la afiliación no tiene costo para su empresa.</p>

  <div class="paso"><div class="n">PASO 1 · HOY</div>
    <b>Nos facilita una copia de su factura.</b> Con eso basta: con su última
    factura hacemos el estudio de su consumo. No necesitamos nada más de usted.</div>
  <div class="paso"><div class="n">PASO 2 · EN 5 DÍAS HÁBILES</div>
    <b>Recibe su simulación.</b> Su ahorro estimado, su participación y su capacidad, con los supuestos a la vista.</div>
  <div class="paso"><div class="n">PASO 3 · SI LE SIRVE</div>
    <b>Firma su afiliación.</b> Nos autoriza a hacer los trámites y a vincularlo a la comunidad.</div>
  <div class="paso"><div class="n">PASO 4 · AL CREAR LA COMUNIDAD</div>
    <b>Queda vinculado.</b> Le informamos su comunidad asignada y le entregamos copia del acuerdo.</div>
  <div class="paso"><div class="n">PASO 5 · DESDE ENTONCES</div>
    <b>Empieza a disfrutar del ahorro.</b> We Club se encarga de todos los
    trámites y de administrar la comunidad. Usted, de ahorrar.</div>

  <h3 style="margin-top:6mm">Del primer contacto al primer ahorro: 16 semanas</h3>
  {_crono()}
  <p class="nota">Cuatro semanas dependen de su empresa: facilitar una copia de la
  factura y firmar. Las doce restantes las gestiona We Club, sujeto a los tiempos
  del Ministerio de Energía y del operador de red.</p>
</div>

<!-- ============ 7. RIESGOS ============ -->
<div class="pagina">
  {_cab("¿Dudas? Aquí se las resolvemos", logo)}
  <h2>¿Dudas? Aquí se las resolvemos</h2>
  <p class="gris">Preferimos que las resuelva ahora y no después de firmar.</p>

  <table>
    <tr><th style="width:38%">Duda</th><th>Respuesta</th></tr>
    <tr><td><b>¿Y si la granja genera menos de lo proyectado?</b></td>
        <td>Sigue recibiendo la energía de su proveedor actual, sin ningún
            cambio y al precio de siempre.</td></tr>
    <tr><td><b>¿Y si mi consumo resulta menor al proyectado?</b></td>
        <td>Su ahorro baja en proporción, porque se calcula sobre la energía
            que efectivamente se le cubre. El plan se revisa en el acuerdo.</td></tr>
    <tr><td><b>¿Qué pasa si no logran vincularme?</b></td>
        <td>Si en doce meses no se crea la comunidad, la afiliación termina y
            usted no paga nada.</td></tr>
    <tr><td><b>¿Y si cambia la regulación?</b></td>
        <td>La estructura se ajusta o se termina, sin penalidad para usted.</td></tr>
    <tr><td><b>Si se va la luz por una falla o un mantenimiento de la red,
            ¿me sigue llegando la energía solar?</b></td>
        <td>No. Toda la energía, la solar incluida, le llega por la misma red.
            Si la red se cae, no llega ninguna. Pertenecer a la comunidad le
            cambia el precio de su energía, no la forma en que le llega.</td></tr>
    <tr><td><b>¿Y cómo hago para no quedarme sin energía?</b></td>
        <td>Podemos instalarle baterías, con un costo aparte, para que no se
            quede sin servicio cuando la red falle.</td></tr>
  </table>

  <div class="caja" style="margin-top:6mm">
    <h3 style="margin-top:0">Afiliación muy sencilla: usted firma la
      vinculación y nosotros nos encargamos de todo</h3>
    <p>Firma un acuerdo de mandato que nos permite hacer los trámites en su
    nombre: firmar por usted los documentos de vinculación a la comunidad
    energética y el contrato de suministro.</p>
    <p style="margin:0"><b>¿Cuánto cuesta firmar?</b> Nada. Usted solo empieza a
    pagar cuando la comunidad energética entre en operación.</p>
  </div>
</div>

<!-- ============ 8. SIGUIENTE PASO ============ -->
<div class="pagina">
  {_cab("Siguiente paso", logo)}
  <h2>El único paso de hoy es el primero</h2>

  <div class="destacado" style="text-align:left">
    <div style="font-size:12.5pt; margin-bottom:3mm">
      <b style="color:{NARANJA}">1.</b> &nbsp;Facilítenos una copia de su factura.
      Le devolvemos su simulación en 5 días hábiles.</div>
    <div style="font-size:12.5pt; margin:0">
      <b style="color:{NARANJA}">2.</b> &nbsp;Si ya nos la entregó, ahora solo
      queda firmar el acuerdo y ¡empezar a ahorrar!</div>
  </div>

  <div class="cols" style="margin-top:5mm">
    <div class="col caja">
      <h3 style="margin-top:0">Su asesor</h3>
      <div class="dato"><div class="k">Nombre</div><div class="v">{d['asesor_nombre']}</div></div>
      <div class="dato"><div class="k">Teléfono</div><div class="v">{d['asesor_tel']}</div></div>
      <div class="dato"><div class="k">Correo</div><div class="v">{d['asesor_mail']}</div></div>
    </div>
    <div class="col caja-borde">
      <h3 style="margin-top:0">We Club en cifras</h3>
      <div class="dato"><div class="k">Energía gestionada</div><div class="v">+100 MW</div></div>
      <div class="dato"><div class="k">Proyectos en el país</div><div class="v">más de 50</div></div>
      <div class="dato"><div class="k">Origen de la energía</div><div class="v">100 % solar</div></div>
    </div>
  </div>

  <div class="caja-borde" style="margin-top:6mm">
    <h3 style="margin-top:0">Beneficios de ser parte de We Club</h3>
    <div class="cols">
      <div class="col">
        <p style="margin-bottom:1mm"><b>Energía 100 % renovable.</b> Acceda a energía solar sin
        instalar nada en su sede y reduzca su huella de carbono.</p>
        <p style="margin:0"><b>Ahorro desde el primer día.</b> Calculamos su ahorro con su propia factura.</p>
      </div>
      <div class="col">
        <p style="margin-bottom:1mm"><b>Confiabilidad y control.</b> Sigue conectado
        con su comercializador actual, así que no arriesga el suministro.</p>
        <p style="margin:0"><b>Inversión cero.</b> We Club cubre el 100 % de la
        inversión, incluido el medidor inteligente.</p>
      </div>
    </div>
  </div>

  <p class="nota" style="margin-top:8mm">
    <b>Esta oferta tiene validez de 30 días calendario a partir del {d['fecha']}.</b><br>
    Las cifras de este documento son una estimación calculada con el consumo promedio informado
    por el cliente y con las tarifas vigentes a la fecha. El ahorro real depende del consumo mes a
    mes, de la tarifa que cobre el comercializador y de la energía disponible en la comunidad.
    Este documento no constituye una oferta vinculante ni un contrato de suministro de energía.<br><br>
    Documento generado el {d['fecha']} para {d['nombre']}
    {"· " + d['correo'] if d['correo'] else ""}.
  </p>
</div>

</body></html>"""


# =========================================================
# ARMAR LOS DATOS Y RENDERIZAR
# =========================================================

def armar_datos(form, sim, r, au, proyeccion, consumo, cu, cv, cu_ce):
    """Junta lo del formulario con lo que la interfaz ya calculó.

    No recalcula nada: `r`, `au` y `proyeccion` son exactamente los mismos
    objetos que la página está mostrando en pantalla.
    """
    return {
        # --- del formulario ---
        "nombre":    form.get("nombre") or "—",
        #  El saludo va con la primera palabra: "¡Hola, Rodolfo!" en vez de
        #  "¡Hola, Rodolfo Pérez García!". El nombre completo sigue saliendo
        #  en la ficha de datos y en el pie.
        "saludo":    (form.get("nombre") or "").split()[0] if (form.get("nombre") or "").strip() else "—",
        "telefono":  form.get("telefono") or "—",
        "direccion": form.get("direccion") or "—",
        "ciudad":    form.get("ciudad") or "—",
        "correo":    form.get("correo") or "",
        #  Si no se escogió comercializador, el informe dice "su comercializador"
        #  a secas. Nunca sale un hueco ni un guion en medio de una frase.
        "comercializador": (form.get("comercializador") or "").strip(),
        "fecha":     form.get("fecha") or datetime.date.today().strftime("%d/%m/%Y"),
        "asesor_nombre": form.get("asesor_nombre") or "—",
        "asesor_tel":    form.get("asesor_tel") or "—",
        "asesor_mail":   form.get("asesor_mail") or "—",
        # --- del modelo ---
        "consumo": consumo, "cu": cu, "cv": cv, "cu_ce": cu_ce,
        "asignada": r["asignada"], "exc1": r["exc1"],
        "energia_red": r["energia_red"], "cobertura": r["cobertura"],
        "factura_sin": r["factura_sin"], "factura_con": r["factura_con"],
        "pago_red": r["pago_red"], "cargo_cv": r["cargo_cv"], "pago_ce": r["pago_ce"],
        "pago_comercializador": r["pago_red"] + r["cargo_cv"],
        "ahorro_mes": r["ahorro_mes"], "ahorro_anual": r["ahorro_anual"],
        "ahorro_pct": r["ahorro_pct"],
        "costo_red_kwh": au["costo_red"], "costo_ce_kwh": cv + cu_ce,
        "ahorro_kwh": au["total"], "descuento": au["descuento_efectivo"],
        "proyeccion": proyeccion,
        "acumulado_total": proyeccion[-1]["acumulado"] if proyeccion else 0,
        "infl_red": sim.INFLACION_RED_ANUAL, "infl_ce": sim.INFLACION_CE_ANUAL,
    }


def generar_pdf(datos):
    """Devuelve los bytes del PDF. Lanza ImportError si falta WeasyPrint."""
    from weasyprint import HTML
    return HTML(string=construir_html(datos), base_url=AQUI).write_pdf()
