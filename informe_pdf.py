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
        content: "WE CLUB · Comunidades energéticas de WE POWER          " counter(page) " / " counter(pages);
        font-size: 7.5pt; color: {GRIS};
    }}
}}
@page :first {{ margin: 0; @bottom-center {{ content: ""; }} }}

* {{ box-sizing: border-box; }}
body {{ font-family: "DejaVu Sans", Arial, sans-serif; color: {AZUL_OSCURO};
        font-size: 9.5pt; line-height: 1.45; margin: 0; }}
h1 {{ font-size: 20pt; color: {AZUL}; margin: 0 0 2mm 0; }}
h2 {{ font-size: 14pt; color: {AZUL}; margin: 0 0 3mm 0; }}
h3 {{ font-size: 10.5pt; color: {AZUL}; margin: 0 0 1.5mm 0; }}
p  {{ margin: 0 0 2.5mm 0; }}
.pagina {{ page-break-after: always; }}
.pagina:last-child {{ page-break-after: auto; }}
.gris {{ color: {GRIS}; }}
.chico {{ font-size: 8pt; }}

/* --- Portada --- */
.portada {{ width: 210mm; height: 297mm; display: flex;
            page-break-after: always; }}
.pt-izq {{ width: 78mm; background: {AZUL}; color: #fff; padding: 20mm 12mm; }}
.pt-izq img {{ width: 24mm; margin-bottom: 14mm; }}
.pt-izq .marca {{ font-size: 19pt; font-weight: bold; letter-spacing: -.3pt; }}
.pt-izq .club {{ color: {NARANJA}; font-size: 30pt; font-weight: bold;
                 margin: 1mm 0 0 0; line-height: 1; }}
.pt-izq .linea {{ width: 34mm; height: 2px; background: {NARANJA}; margin: 7mm 0; }}
.pt-izq .lema {{ font-size: 11pt; line-height: 1.5; opacity: .93; }}
.pt-izq .web {{ position: absolute; bottom: 20mm; font-size: 9pt; opacity: .8; }}
.pt-der {{ flex: 1; padding: 20mm 16mm; }}
.pt-der .saludo {{ font-size: 27pt; font-weight: bold; color: {AZUL};
                   margin: 0 0 6mm 0; line-height: 1.1; }}
.pt-der p {{ font-size: 10pt; line-height: 1.55; margin-bottom: 3.5mm; }}
.pt-der .cierre {{ color: {AZUL}; font-weight: bold; }}
.cifras {{ display: flex; gap: 3mm; margin: 6mm 0; }}
.cifra-caja {{ flex: 1; background: {GRIS_CLARO}; border-radius: 2mm;
               padding: 3mm; text-align: center; }}
.cifra-caja b {{ display: block; color: {AZUL}; font-size: 13pt; }}
.cifra-caja span {{ font-size: 7.5pt; color: {GRIS}; }}
.asesor-portada {{ border-top: 2px solid {NARANJA}; padding-top: 4mm; margin-top: 6mm; }}

/* --- Encabezado de páginas interiores --- */
.cab {{ border-bottom: 2px solid {NARANJA}; padding-bottom: 2mm; margin-bottom: 5mm;
        display: flex; }}
.cab img {{ width: 13mm; }}
.cab .t {{ flex: 1; text-align: right; font-size: 8pt; color: {GRIS}; padding-top: 4mm; }}

/* --- Bloques --- */
.destacado {{ background: {AZUL}; color: #fff; border-radius: 3mm;
              padding: 7mm; text-align: center; margin: 4mm 0; }}
.destacado .cifra {{ font-size: 25pt; font-weight: bold; line-height: 1.1;
                     white-space: nowrap; }}
.destacado .sub {{ font-size: 10pt; opacity: .9; margin-top: 2mm; }}
.caja {{ background: {GRIS_CLARO}; border-radius: 2.5mm; padding: 4mm; }}
.caja-borde {{ border: 1px solid #D5DCE6; border-radius: 2.5mm; padding: 4mm; }}

table {{ width: 100%; border-collapse: collapse; font-size: 9pt; }}
th {{ background: {GRIS_CLARO}; color: {AZUL}; text-align: left;
      padding: 2mm 3mm; font-size: 8.5pt; }}
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


def _cab(titulo, logo):
    # Si falta el archivo del logo, va el nombre en texto: el encabezado
    # no queda cojo y el informe se puede emitir igual.
    marca = ('<img src="' + logo + '">') if logo else (
        '<b style="color:' + AZUL + '; font-size:11pt">WE POWER</b>')
    return '<div class="cab">' + marca + '<div class="t">' + titulo + '</div></div>'


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
    {logo_img}
    <div class="marca">WE POWER</div>
    <div class="club">WE CLUB</div>
    <div class="linea"></div>
    <div class="lema">Comunidades energéticas de WE Power.<br><br>
      Energía limpia, a menor costo y sin invertir en equipos.</div>
    <div class="web">wepower.com.co</div>
  </div>

  <div class="pt-der">
    <div class="saludo">¡Hola,<br>{d['nombre']}!</div>

    <p>En <b>WE POWER</b> trabajamos para poner la energía del sol a disposición de
    su empresa. <b>We Club es nuestra comunidad energética:</b> reunimos a varias
    empresas para comprar energía solar en conjunto y, al comprar entre muchos,
    el precio por kWh baja.</p>

    <p>Su empresa <b>sigue conectada con su operador de energía actual</b>. Nosotros
    le suministramos una parte de su consumo desde nuestras granjas solares, a una
    tarifa menor que la que paga hoy.</p>

    <p><b>No tiene que invertir en paneles ni equipos.</b> Generamos la energía en
    granjas solares cercanas y se la llevamos a su empresa. Nosotros nos encargamos
    de los trámites; usted, de ahorrar.</p>

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
      </div>
      <div class="caja-borde" style="margin-top:4mm">
        <h3 style="margin-top:0">Energía que le cubrimos</h3>
        <p style="margin:0"><b>{num(d['asignada'])} kWh al mes</b> generados en nuestras granjas solares</p>
        <div class="barra"><div style="width:{min(100, d['cobertura']*100):.0f}%"></div></div>
        <p class="chico gris" style="margin:0">Equivale al <b>{pct(d['cobertura'],0)}</b> de su
          consumo. Su energía sigue llegando por la red de siempre: lo que cambia es
          el precio de esa parte.</p>
      </div>
    </div>
  </div>

  <div class="caja" style="margin-top:5mm">
    <h3 style="margin-top:0">Cómo se calcula</h3>
    <p style="margin:0">Cubrimos {num(d['asignada'])} kWh al mes a un costo de
    <b>{cop(d['costo_ce_kwh'],2)}</b> por kWh, frente a los <b>{cop(d['costo_red_kwh'],2)}</b>
    que le cuesta hoy cada kWh de la red con contribución incluida.
    Son <b>{cop(d['ahorro_kwh'],2)}</b> menos por cada kWh cubierto: un
    <b>{pct(d['descuento'],0)}</b> de descuento.</p>
  </div>

  <p class="nota"><b>Es un estimado.</b> Está calculado con un consumo promedio de
  {num(d['consumo'])} kWh al mes. Su consumo cambia mes a mes y su ahorro también:
  en un mes de mayor consumo ahorra más, en uno de menor consumo ahorra menos.</p>
</div>

<!-- ============ 3. LA FACTURA ============ -->
<div class="pagina">
  {_cab("Su factura, antes y después", logo)}
  <h2>Su factura, antes y después</h2>

  <div class="cols">
    <div class="col caja-borde" style="text-align:center">
      <div class="gris chico">ANTES PAGABA</div>
      <div style="font-size:19pt; font-weight:bold; color:{GRIS}">{cop(d['factura_sin'])}</div>
      <div class="chico gris">todo su consumo a la red</div>
    </div>
    <div class="col destacado" style="margin:0">
      <div style="font-size:8pt; opacity:.9">AHORA PAGA (ENTRE LAS DOS)</div>
      <div style="font-size:19pt; font-weight:bold">{cop(d['factura_con'])}</div>
      <div class="chico" style="color:{NARANJA}">−{cop(d['ahorro_mes'])} cada mes</div>
    </div>
  </div>

  <h3 style="margin-top:6mm">De qué se compone lo que va a pagar</h3>
  <table>
    <tr><th>Concepto</th><th style="text-align:right">Valor</th></tr>
    <tr><td>Lo que le sigue pagando a su comercializador</td>
        <td class="n">{cop(d['pago_comercializador'])}</td></tr>
    <tr><td>Lo que le paga a WE Power</td>
        <td class="n">{cop(d['pago_ce'])}</td></tr>
    <tr class="total"><td>TOTAL, ENTRE LAS DOS FACTURAS</td>
        <td class="n">{cop(d['factura_con'])}</td></tr>
  </table>
  <p class="nota" style="margin-top:2mm">Recibirá <b>dos facturas</b>: la de su comercializador, como siempre, y la de la comunidad.
  Su comercializador le sigue facturando toda
  la energía. Ese cobro junta dos cosas: los {num(d['energia_red'])} kWh que no
  alcanzamos a cubrir, al precio de siempre, y el cargo que le hace por los
  {num(d['exc1'])} kWh que sí cubrimos.</p>

  <h3 style="margin-top:6mm">Por cada kWh que le cubrimos</h3>
  <div class="cols">
    <div class="col caja" style="text-align:center">
      <div class="chico gris">ESE kWh EN LA RED</div>
      <div style="font-size:14pt; font-weight:bold">{cop(d['costo_red_kwh'],2)}</div>
      <div class="chico gris">energía + 20 % de contribución</div>
    </div>
    <div class="col caja" style="text-align:center">
      <div class="chico gris">ESE kWh CON WE POWER</div>
      <div style="font-size:14pt; font-weight:bold">{cop(d['costo_ce_kwh'],2)}</div>
      <div class="chico gris">no paga contribución</div>
    </div>
    <div class="col caja" style="text-align:center; background:{AZUL}; color:#fff">
      <div class="chico" style="opacity:.85">SE AHORRA</div>
      <div style="font-size:14pt; font-weight:bold; color:{NARANJA}">{cop(d['ahorro_kwh'],2)}</div>
      <div class="chico" style="opacity:.85">{pct(d['descuento'],0)} menos</div>
    </div>
  </div>

  <p class="nota">Su factura no baja ese mismo {pct(d['descuento'],0)} porque el descuento
  aplica solo a los kWh que ponemos nosotros, que son el {pct(d['cobertura'],0)} de su consumo:
  {pct(d['descuento'],0)} × {pct(d['cobertura'],0)} = {pct(d['ahorro_pct'])} de su factura.</p>
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
      <li>La tarifa de la red sube <b>{pct(d['infl_red'],0)}</b> al año.</li>
      <li>El precio de WE Power sube <b>{pct(d['infl_ce'],0)}</b> al año.</li>
      <li>Su consumo y su participación en la comunidad se mantienen.</li>
      <li>Los valores están en pesos corrientes, sin traer a valor presente.</li>
    </ul>
  </div>
  <p class="nota">Las cifras son estimadas y dependen de su consumo real y de la tarifa
  que le cobre su comercializador en cada período.</p>
</div>

<!-- ============ 5. QUÉ CAMBIA ============ -->
<div class="pagina">
  {_cab("Qué cambia y qué no cambia", logo)}
  <h2>Qué cambia y qué no cambia para su empresa</h2>

  <div class="cols">
    <div class="col caja">
      <h3 style="margin-top:0">Lo que NO cambia</h3>
      <ul>
        <li>Su operador de energía y su comercializador siguen siendo los mismos.</li>
        <li>La continuidad del servicio: si la granja no genera, su operador lo sigue atendiendo.</li>
        <li>Su empresa no pone capital ni compra equipos.</li>
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
        <td>Genera la energía solar del proyecto de generación distribuida.</td></tr>
    <tr><td><b>Comunidad energética</b></td>
        <td>Agrupa a los usuarios, fija las reglas y asigna la energía entre ellos.</td></tr>
    <tr><td><b>Comercializador habilitado</b></td>
        <td>Compra, vende y factura la energía ante el mercado eléctrico.</td></tr>
    <tr><td><b>Operador de red</b></td>
        <td>Transporta la energía y sigue atendiendo su suministro. No cambia.</td></tr>
    <tr><td><b>Su empresa</b></td>
        <td>Consume y paga. Delega en We Club la gestión y los trámites.</td></tr>
  </table>
  <p class="nota">WE POWER estructura el proyecto y administra la comunidad. No reemplaza a su
  operador de red, y la venta de energía la hace un comercializador habilitado.
  Operación amparada por las Resoluciones CREG 174 de 2021 y 101 072 de 2025.</p>
</div>

<!-- ============ 6. CÓMO SE AFILIA ============ -->
<div class="pagina">
  {_cab("Cómo se afilia", logo)}
  <h2>Cómo se afilia: cuatro pasos</h2>
  <p class="gris">Firmar la afiliación no tiene costo para su empresa.</p>

  <div class="paso"><div class="n">PASO 1 · HOY</div>
    <b>Nos entrega su factura.</b> Con su última factura y sus datos hacemos el estudio de su consumo.</div>
  <div class="paso"><div class="n">PASO 2 · EN 5 DÍAS HÁBILES</div>
    <b>Recibe su simulación.</b> Su ahorro estimado, su participación y su capacidad, con los supuestos a la vista.</div>
  <div class="paso"><div class="n">PASO 3 · SI LE SIRVE</div>
    <b>Firma su afiliación.</b> Nos autoriza a hacer los trámites y a vincularlo a la comunidad.</div>
  <div class="paso"><div class="n">PASO 4 · AL CREAR LA COMUNIDAD</div>
    <b>Queda vinculado.</b> Le informamos su comunidad asignada y le entregamos copia del acuerdo.</div>

  <h3 style="margin-top:6mm">Del primer contacto al primer ahorro: 16 semanas</h3>
  <table>
    <tr><th>Etapa</th><th>Tiempo</th><th>A cargo de</th></tr>
    <tr><td>Estudio de consumo y tarifas actuales</td><td>2 semanas</td><td>Usted entrega la factura</td></tr>
    <tr><td>Firma del acuerdo de afiliación</td><td>2 semanas</td><td>Usted firma</td></tr>
    <tr><td>Instalación del medidor y gestión ante su operador</td><td>10 semanas</td><td>WE POWER</td></tr>
    <tr><td>Puesta en marcha y capacitación</td><td>2 semanas</td><td>WE POWER</td></tr>
    <tr class="total"><td>Inicio del ahorro</td><td colspan="2">Desde el primer mes de operación</td></tr>
  </table>
  <p class="nota">Cuatro semanas dependen de su empresa (entregar la factura y firmar); las doce
  restantes las gestiona WE POWER, sujeto a los tiempos del Ministerio de Energía y del operador de red.</p>
</div>

<!-- ============ 7. RIESGOS ============ -->
<div class="pagina">
  {_cab("Riesgos y cómo se cubren", logo)}
  <h2>Riesgos y cómo se cubren</h2>
  <p class="gris">Preferimos que los vea ahora y no después de firmar.</p>

  <table>
    <tr><th>Riesgo</th><th>Qué pasa</th><th>Quién lo asume</th></tr>
    <tr><td><b>La granja genera menos de lo proyectado</b></td>
        <td>Su suministro no se interrumpe: la energía faltante la entrega su operador.</td>
        <td>WE POWER y el generador</td></tr>
    <tr><td><b>Su consumo resulta menor al proyectado</b></td>
        <td>Su ahorro baja en proporción. El plan se revisa en el acuerdo.</td>
        <td>Compartido</td></tr>
    <tr><td><b>Si no logramos vincularlo</b></td>
        <td>Si en doce meses no se crea la comunidad, la afiliación termina y usted no paga nada.</td>
        <td>WE POWER</td></tr>
    <tr><td><b>Cambia la regulación aplicable</b></td>
        <td>La estructura se ajusta o se termina sin penalidad para usted.</td>
        <td>WE POWER</td></tr>
    <tr><td><b>No sabe quién le facturará</b></td>
        <td>Se define quién factura y cuántas facturas recibe antes de firmar.</td>
        <td>WE POWER</td></tr>
  </table>

  <div class="caja" style="margin-top:6mm">
    <h3 style="margin-top:0">Qué firma: su afiliación a We Club</h3>
    <p>Un mandato que nos permite hacer los trámites en su nombre: vincularlo a una comunidad
    energética y firmar por usted el acuerdo de la comunidad y el contrato de suministro.</p>
    <p style="margin:0"><b>¿Cuánto cuesta firmar?</b> Nada. Usted solo empieza a pagar cuando se firme
    el contrato de suministro en su nombre, y en las condiciones de ese contrato.</p>
  </div>
</div>

<!-- ============ 8. SIGUIENTE PASO ============ -->
<div class="pagina">
  {_cab("Siguiente paso", logo)}
  <h2>El único paso de hoy es el primero</h2>

  <div class="destacado">
    <div style="font-size:13pt">Entréguenos su factura y le devolvemos su simulación<br>
      en 5 días hábiles.</div>
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
        <p style="margin-bottom:1mm"><b>Confiabilidad y control.</b> Sigue conectado con su operador
        actual, así que no arriesga el suministro.</p>
        <p style="margin:0"><b>Inversión cero.</b> WE POWER cubre el 100 % de la inversión,
        incluido el medidor inteligente.</p>
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
        "telefono":  form.get("telefono") or "—",
        "direccion": form.get("direccion") or "—",
        "ciudad":    form.get("ciudad") or "—",
        "correo":    form.get("correo") or "",
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
