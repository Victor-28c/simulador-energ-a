import os
import base64
import datetime

AQUI = os.path.dirname(os.path.abspath(__file__))

# --- Paleta ------------------------------------------------------------
AZUL = "#004191"
AZUL_OSCURO = "#00305F"
NARANJA = "#E2A03C"
AZUL_CLARO = "#E7F0FC"     # fondo de énfasis (tinte de marca, no gris genérico)
GRIS_CLARO = "#F3F5F8"     # fondo neutro
GRIS = "#5A6472"
LINEA = "#DFE5EE"


def _logo_base64():
    for nombre in ("logo_wepower.png", "logo.png"):
        ruta = os.path.join(AQUI, nombre)
        if os.path.exists(ruta):
            with open(ruta, "rb") as f:
                return "data:image/png;base64," + base64.b64encode(f.read()).decode()
    return ""


def cop(v, d=0):
    return "$ " + f"{v:,.{d}f}".replace(",", "@").replace(".", ",").replace("@", ".")


def pct(v, d=1):
    return f"{v * 100:,.{d}f}".replace(",", "@").replace(".", ",").replace("@", ".") + " %"


def num(v, d=0):
    return f"{v:,.{d}f}".replace(",", "@").replace(".", ",").replace("@", ".")


# --- Iconos propios (SVG originales, sin dependencias externas) --------

ICONO_CHECK = f'''<svg viewBox="0 0 20 20" width="4.4mm" height="4.4mm" xmlns="http://www.w3.org/2000/svg">
<circle cx="10" cy="10" r="9" fill="{AZUL}"/>
<path d="M6 10.3l2.6 2.6L14.3 7" stroke="#fff" stroke-width="1.8" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
</svg>'''

ICONO_CAMBIO = f'''<svg viewBox="0 0 20 20" width="4.4mm" height="4.4mm" xmlns="http://www.w3.org/2000/svg">
<circle cx="10" cy="10" r="9" fill="{NARANJA}"/>
<path d="M5.6 8h7M11 5.6L13.4 8 11 10.4M14.4 12h-7M9 9.6L6.6 12 9 14.4" stroke="#fff" stroke-width="1.3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
</svg>'''

ICONO_ESCUDO = f'''<svg viewBox="0 0 20 20" width="5.4mm" height="5.4mm" xmlns="http://www.w3.org/2000/svg">
<path d="M10 2.2l6.2 2.3v4.7c0 4-2.6 7-6.2 8.2-3.6-1.2-6.2-4.2-6.2-8.2V4.5L10 2.2z" fill="{AZUL_CLARO}" stroke="{AZUL}" stroke-width="1"/>
<path d="M7.1 10.1l1.9 1.9L13.1 8" stroke="{AZUL}" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
</svg>'''

# Motivo decorativo de portada: sol (comunidad solar) + nodos conectados
# (empresas que se agrupan). Dibujado a mano, sin fotografías externas.
MOTIVO_PORTADA = f'''<svg viewBox="0 0 300 420" preserveAspectRatio="xMidYMid slice"
     xmlns="http://www.w3.org/2000/svg"
     style="position:absolute; top:0; left:0; width:100%; height:100%;">
  <circle cx="250" cy="70" r="66" fill="none" stroke="#ffffff" stroke-opacity="0.12" stroke-width="1.3"/>
  <circle cx="250" cy="70" r="90" fill="none" stroke="#ffffff" stroke-opacity="0.08" stroke-width="1.3"/>
  <circle cx="250" cy="70" r="32" fill="{NARANJA}" fill-opacity="0.20"/>
  <circle cx="250" cy="70" r="18" fill="{NARANJA}" fill-opacity="0.30"/>
  <g stroke="#ffffff" stroke-opacity="0.16" stroke-width="1.1">
    <line x1="36" y1="345" x2="92" y2="313"/>
    <line x1="92" y1="313" x2="150" y2="338"/>
    <line x1="150" y1="338" x2="118" y2="388"/>
    <line x1="92" y1="313" x2="66" y2="266"/>
    <line x1="150" y1="338" x2="176" y2="292"/>
  </g>
  <g fill="#ffffff" fill-opacity="0.18">
    <rect x="28" y="337" width="16" height="16" rx="3"/>
    <rect x="84" y="305" width="16" height="16" rx="3"/>
    <rect x="142" y="330" width="16" height="16" rx="3"/>
    <rect x="110" y="380" width="16" height="16" rx="3"/>
    <rect x="58" y="258" width="16" height="16" rx="3"/>
    <rect x="168" y="284" width="16" height="16" rx="3"/>
  </g>
</svg>'''


def _lista_ico(items, icono):
    filas = "".join(f'<li>{icono}<span>{t}</span></li>' for t in items)
    return f'<ul class="lista-ico">{filas}</ul>'


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
        font-size: 9.5pt; line-height: 1.5; margin: 0; }}
h1 {{ font-size: 22pt; color: {AZUL}; margin: 0 0 2mm 0; }}
h2 {{ font-size: 19pt; color: {AZUL}; margin: 0 0 5mm 0; letter-spacing: -.2pt; }}
h3 {{ font-size: 11.5pt; color: {AZUL}; margin: 0 0 2mm 0; }}
h4 {{ font-size: 9.5pt; color: {AZUL_OSCURO}; margin: 0 0 1mm 0; }}
p  {{ margin: 0 0 2.8mm 0; }}
.pagina {{ page-break-after: always; }}
.pagina:last-child {{ page-break-after: auto; }}
.gris {{ color: {GRIS}; }}
.chico {{ font-size: 8pt; }}

/* --- Portada --- */
.portada {{ width: 210mm; height: 297mm; display: flex;
            page-break-after: always; }}
.pt-izq {{ width: 78mm; background: {AZUL}; color: #fff; padding: 20mm 12mm;
           position: relative; overflow: hidden; }}
.pt-izq img {{ width: 24mm; margin-bottom: 14mm; position: relative; }}
.pt-izq .marca {{ font-size: 19pt; font-weight: bold; letter-spacing: -.3pt; position: relative; }}
.pt-izq .club {{ color: {NARANJA}; font-size: 30pt; font-weight: bold;
                 margin: 1mm 0 0 0; line-height: 1; position: relative; }}
.pt-izq .linea {{ width: 34mm; height: 2px; background: {NARANJA}; margin: 7mm 0; position: relative; }}
.pt-izq .lema {{ font-size: 11pt; line-height: 1.5; opacity: .93; position: relative; }}
.pt-izq .web {{ position: absolute; bottom: 20mm; left: 12mm; font-size: 9pt; opacity: .8; }}
.pt-der {{ flex: 1; padding: 20mm 16mm; }}
.pt-der .saludo {{ font-size: 30pt; font-weight: bold; color: {AZUL};
                   margin: 0 0 6mm 0; line-height: 1.06; }}
.pt-der p {{ font-size: 10pt; line-height: 1.58; margin-bottom: 3.6mm; }}
.pt-der .cierre {{ color: {AZUL}; font-weight: bold; }}
.cifras {{ display: flex; gap: 5mm; margin: 6.5mm 0; }}
.cifra-caja {{ flex: 1; border-top: 2px solid {NARANJA}; padding-top: 2.4mm; min-width: 0; }}
.cifra-caja b {{ display: block; color: {AZUL}; font-size: 13.5pt; white-space: nowrap; }}
.cifra-caja span {{ font-size: 7.4pt; color: {GRIS}; }}
.asesor-portada {{ border-top: 2px solid {NARANJA}; padding-top: 4mm; margin-top: 6mm; }}

/* --- Encabezado de páginas interiores --- */
.cab {{ border-bottom: 2px solid {NARANJA}; padding-bottom: 2.5mm; margin-bottom: 6.5mm;
        display: flex; align-items: center; }}
.cab img {{ width: 13mm; }}
.cab-mid {{ flex: 1; display: flex; justify-content: center; }}
.puntos {{ display: flex; gap: 1.4mm; }}
.punto {{ width: 1.7mm; height: 1.7mm; border-radius: 50%; background: {LINEA}; }}
.punto.activo {{ background: {NARANJA}; }}
.cab .t {{ font-size: 8pt; color: {GRIS}; }}

/* --- Bloques --- */
.destacado {{ background: linear-gradient(135deg, {AZUL} 0%, {AZUL_OSCURO} 100%); color: #fff;
              border-radius: 3mm; padding: 8mm; text-align: center; margin: 5mm 0; }}
.destacado .cifra {{ font-size: 29pt; font-weight: bold; line-height: 1.1;
                     white-space: nowrap; }}
.destacado .sub {{ font-size: 10.5pt; opacity: .9; margin-top: 2.2mm; }}
.caja {{ background: {GRIS_CLARO}; border-radius: 2.5mm; padding: 5mm; }}
.caja-enfasis {{ background: {AZUL_CLARO}; border-radius: 2.5mm; padding: 5mm; }}
.caja-borde {{ border: 1px solid {LINEA}; border-radius: 2.5mm; padding: 5mm; }}

table {{ width: 100%; border-collapse: collapse; font-size: 9pt; }}
th {{ background: {GRIS_CLARO}; color: {AZUL}; text-align: left;
      padding: 2.4mm 3mm; font-size: 8.5pt; }}
td {{ padding: 2.4mm 3mm; border-bottom: 1px solid {LINEA}; }}
td.n {{ text-align: right; white-space: nowrap; }}
tr.total td {{ font-weight: bold; color: {AZUL}; border-top: 1.5px solid {AZUL};
               border-bottom: none; }}

.cols {{ display: flex; gap: 6mm; }}
.col {{ flex: 1; }}
.dato {{ display: flex; gap: 4mm; border-bottom: 1px solid {LINEA}; padding: 2.2mm 0; }}
.dato .k {{ flex: 0 0 38%; color: {GRIS}; }}
.dato .v {{ flex: 1; font-weight: bold; overflow-wrap: break-word; }}

/* Paso a paso con línea de tiempo */
.stepper {{ position: relative; padding-left: 9mm; margin-top: 5mm; }}
.stepper::before {{ content: ""; position: absolute; left: 3.7mm; top: 3.6mm; bottom: 3.6mm;
                     width: 1.6px; background: {LINEA}; }}
.paso {{ position: relative; margin-bottom: 6mm; }}
.paso:last-child {{ margin-bottom: 0; }}
.paso .num {{ position: absolute; left: -9mm; top: 0; width: 7.2mm; height: 7.2mm;
              border-radius: 50%; background: {AZUL}; color: #fff; font-weight: bold;
              font-size: 9.5pt; display: flex; align-items: center; justify-content: center; }}
.paso .etiqueta {{ font-size: 8pt; color: {NARANJA}; font-weight: bold; margin-bottom: 0.8mm; }}

.barra {{ background: {LINEA}; border-radius: 2.6mm; height: 6mm; margin: 2mm 0; overflow: hidden; }}
.barra div {{ background: linear-gradient(90deg, {AZUL}, {AZUL_OSCURO}); height: 100%; }}

ul {{ margin: 0 0 2mm 0; padding-left: 4.5mm; }}
li {{ margin-bottom: 1.8mm; }}
.lista-ico {{ list-style: none; padding: 0; margin: 0 0 2mm 0; }}
.lista-ico li {{ display: flex; gap: 2.8mm; align-items: flex-start; margin-bottom: 3mm; }}
.lista-ico li svg {{ flex: 0 0 auto; margin-top: 0.3mm; }}
.lista-ico li span {{ flex: 1; }}

.nota {{ font-size: 7.5pt; color: {GRIS}; margin-top: 3mm; line-height: 1.45; }}

/* Tarjetas de riesgo */
.riesgo {{ display: flex; gap: 4mm; padding: 4.2mm 0; border-bottom: 1px solid {LINEA};
           align-items: flex-start; }}
.riesgo:last-child {{ border-bottom: none; }}
.riesgo .cont {{ flex: 1; }}
.riesgo .cont p {{ margin: 0; font-size: 8.8pt; color: {GRIS}; }}
.riesgo .quien {{ flex: 0 0 32mm; text-align: right; font-size: 8pt; font-weight: bold; color: {AZUL}; }}

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


def _cab(indice, titulo, logo):
    marca = ('<img src="' + logo + '">') if logo else (
        '<b style="color:' + AZUL + '; font-size:11pt">WE POWER</b>')
    puntos = "".join(
        f'<span class="punto{" activo" if i <= indice else ""}"></span>'
        for i in range(1, 9))
    return (f'<div class="cab">{marca}'
            f'<div class="cab-mid"><div class="puntos">{puntos}</div></div>'
            f'<div class="t">{titulo}</div></div>')


def construir_html(d):
    logo = _logo_base64()
    logo_img = ('<img src="' + logo + '">') if logo else ""

    tope = max(p["acumulado"] for p in d["proyeccion"]) or 1
    filas_proy = "".join(
        f'<tr><td>Año {p["anio"]}</td>'
        f'<td class="n">{cop(p["ahorro_anual"])}</td>'
        f'<td class="n">{pct(p["ahorro_pct"])}</td>'
        f'<td class="n">{cop(p["acumulado"])}</td>'
        f'<td style="width:34%"><div class="barra">'
        f'<div style="width:{p["acumulado"]/tope*100:.1f}%"></div></div></td></tr>'
        for p in d["proyeccion"])

    lista_no_cambia = _lista_ico([
        "Su operador de energía y su comercializador siguen siendo los mismos.",
        "La continuidad del servicio: si la granja no genera, su operador lo sigue atendiendo.",
        "Su empresa no pone capital ni compra equipos.",
        "No tiene que hacer trámites: nosotros los hacemos por usted.",
    ], ICONO_CHECK)

    lista_si_cambia = _lista_ico([
        "Su medidor se reemplaza por un medidor inteligente, sin costo para usted.",
        "Parte de la energía que consume la genera una granja solar y se le acredita en su factura.",
        "Paga menos por esa energía: un descuento sobre el costo unitario que paga hoy.",
        "Recibe reportes de su consumo y de su ahorro.",
    ], ICONO_CAMBIO)

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>{CSS}</style></head><body>

<div class="aviso-print">
  <b>Para guardarlo en PDF:</b> presione <b>Ctrl + P</b> (o <b>Cmd + P</b> en Mac)
  y elija <b>Guardar como PDF</b>. Este aviso no se imprime.
</div>

<!-- ============ 1. PORTADA ============ -->
<div class="portada">
  <div class="pt-izq">
    {MOTIVO_PORTADA}
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
  {_cab(2, "Ahorro estimado para su empresa", logo)}
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
        <div style="font-size:10.5pt; opacity:.9">Ahorro estimado al año</div>
        <div class="cifra">{cop(d['ahorro_anual'])}</div>
        <div class="sub">{cop(d['ahorro_mes'])} cada mes</div>
      </div>
      <div class="caja-enfasis">
        <h3 style="margin-top:0">Equivale a</h3>
        <p style="font-size:17pt; font-weight:bold; color:{AZUL}; margin:0">
          {pct(d['ahorro_pct'])} menos<br>
          <span style="font-size:9.5pt; font-weight:normal; color:{GRIS}">
            en su factura de energía</span></p>
      </div>
      <div class="caja-borde" style="margin-top:4.5mm">
        <h3 style="margin-top:0">Energía que le cubrimos</h3>
        <p style="margin:0"><b>{num(d['asignada'])} kWh al mes</b> generados en nuestras granjas solares</p>
        <div class="barra"><div style="width:{min(100, d['cobertura']*100):.0f}%"></div></div>
        <p class="chico gris" style="margin:0">Equivale al <b>{pct(d['cobertura'],0)}</b> de su
          consumo. Su energía sigue llegando por la red de siempre: lo que cambia es
          el precio de esa parte.</p>
      </div>
    </div>
  </div>

  <div class="caja" style="margin-top:6mm">
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
  {_cab(3, "Su factura, antes y después", logo)}
  <h2>Su factura, antes y después</h2>

  <div class="cols">
    <div class="col caja-borde" style="text-align:center">
      <div class="gris chico">Antes pagaba</div>
      <div style="font-size:20pt; font-weight:bold; color:{GRIS}">{cop(d['factura_sin'])}</div>
      <div class="chico gris">todo su consumo a la red</div>
    </div>
    <div class="col destacado" style="margin:0">
      <div style="font-size:8.5pt; opacity:.9">Ahora paga (entre las dos)</div>
      <div style="font-size:20pt; font-weight:bold">{cop(d['factura_con'])}</div>
      <div class="chico" style="color:{NARANJA}">−{cop(d['ahorro_mes'])} cada mes</div>
    </div>
  </div>

  <h3 style="margin-top:7mm">De qué se compone lo que va a pagar</h3>
  <table>
    <tr><th>Concepto</th><th style="text-align:right">Valor</th></tr>
    <tr><td>Lo que le sigue pagando a su comercializador</td>
        <td class="n">{cop(d['pago_comercializador'])}</td></tr>
    <tr><td>Lo que le paga a WE Power</td>
        <td class="n">{cop(d['pago_ce'])}</td></tr>
    <tr class="total"><td>Total, entre las dos facturas</td>
        <td class="n">{cop(d['factura_con'])}</td></tr>
  </table>
  <p class="nota" style="margin-top:2.5mm">Recibirá <b>dos facturas</b>: la de su comercializador, como siempre, y la de la comunidad.
  Su comercializador le sigue facturando toda
  la energía. Ese cobro junta dos cosas: los {num(d['energia_red'])} kWh que no
  alcanzamos a cubrir, al precio de siempre, y el cargo que le hace por los
  {num(d['exc1'])} kWh que sí cubrimos.</p>

  <h3 style="margin-top:7mm">Por cada kWh que le cubrimos</h3>
  <div class="cols">
    <div class="col caja" style="text-align:center">
      <div class="chico gris">Ese kWh en la red</div>
      <div style="font-size:15pt; font-weight:bold">{cop(d['costo_red_kwh'],2)}</div>
      <div class="chico gris">energía + 20 % de contribución</div>
    </div>
    <div class="col caja" style="text-align:center">
      <div class="chico gris">Ese kWh con WE Power</div>
      <div style="font-size:15pt; font-weight:bold">{cop(d['costo_ce_kwh'],2)}</div>
      <div class="chico gris">no paga contribución</div>
    </div>
    <div class="col caja" style="text-align:center; background:{AZUL}; color:#fff">
      <div class="chico" style="opacity:.85">Se ahorra</div>
      <div style="font-size:15pt; font-weight:bold; color:{NARANJA}">{cop(d['ahorro_kwh'],2)}</div>
      <div class="chico" style="opacity:.85">{pct(d['descuento'],0)} menos</div>
    </div>
  </div>

  <p class="nota">Su factura no baja ese mismo {pct(d['descuento'],0)} porque el descuento
  aplica solo a los kWh que ponemos nosotros, que son el {pct(d['cobertura'],0)} de su consumo:
  {pct(d['descuento'],0)} × {pct(d['cobertura'],0)} = {pct(d['ahorro_pct'])} de su factura.</p>
</div>

<!-- ============ 4. PROYECCIÓN ============ -->
<div class="pagina">
  {_cab(4, "Su ahorro con los años", logo)}
  <h2>Su ahorro con los años</h2>
  <p class="gris">Proyección a {len(d['proyeccion'])} años con el plan Estándar.</p>

  <table>
    <tr><th>Período</th><th style="text-align:right">Ahorro del año</th>
        <th style="text-align:right">% de su factura</th>
        <th style="text-align:right">Acumulado</th><th></th></tr>
    {filas_proy}
  </table>

  <div class="destacado" style="margin-top:7mm">
    <div style="font-size:10.5pt; opacity:.9">Ahorro acumulado en {len(d['proyeccion'])} años</div>
    <div class="cifra">{cop(d['acumulado_total'])}</div>
  </div>

  <div class="caja" style="margin-top:6mm">
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
  {_cab(5, "Qué cambia y qué no cambia", logo)}
  <h2>Qué cambia y qué no cambia para su empresa</h2>

  <div class="cols">
    <div class="col caja">
      <h3 style="margin-top:0">Lo que NO cambia</h3>
      {lista_no_cambia}
    </div>
    <div class="col caja">
      <h3 style="margin-top:0">Lo que sí cambia</h3>
      {lista_si_cambia}
    </div>
  </div>

  <h3 style="margin-top:7mm">Quién es quién</h3>
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
  {_cab(6, "Cómo se afilia", logo)}
  <h2>Cómo se afilia: cuatro pasos</h2>
  <p class="gris">Firmar la afiliación no tiene costo para su empresa.</p>

  <div class="stepper">
    <div class="paso"><div class="num">1</div>
      <div class="etiqueta">HOY</div>
      <b>Nos entrega su factura.</b> Con su última factura y sus datos hacemos el estudio de su consumo.</div>
    <div class="paso"><div class="num">2</div>
      <div class="etiqueta">EN 5 DÍAS HÁBILES</div>
      <b>Recibe su simulación.</b> Su ahorro estimado, su participación y su capacidad, con los supuestos a la vista.</div>
    <div class="paso"><div class="num">3</div>
      <div class="etiqueta">SI LE SIRVE</div>
      <b>Firma su afiliación.</b> Nos autoriza a hacer los trámites y a vincularlo a la comunidad.</div>
    <div class="paso"><div class="num">4</div>
      <div class="etiqueta">AL CREAR LA COMUNIDAD</div>
      <b>Queda vinculado.</b> Le informamos su comunidad asignada y le entregamos copia del acuerdo.</div>
  </div>

  <h3 style="margin-top:8mm">Del primer contacto al primer ahorro: 16 semanas</h3>
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
  {_cab(7, "Riesgos y cómo se cubren", logo)}
  <h2>Riesgos y cómo se cubren</h2>
  <p class="gris">Preferimos que los vea ahora y no después de firmar.</p>

  <div class="caja-borde" style="padding:1mm 5mm">
    <div class="riesgo">
      {ICONO_ESCUDO}
      <div class="cont"><h4>La granja genera menos de lo proyectado</h4>
        <p>Su suministro no se interrumpe: la energía faltante la entrega su operador.</p></div>
      <div class="quien">WE POWER y el generador</div>
    </div>
    <div class="riesgo">
      {ICONO_ESCUDO}
      <div class="cont"><h4>Su consumo resulta menor al proyectado</h4>
        <p>Su ahorro baja en proporción. El plan se revisa en el acuerdo.</p></div>
      <div class="quien">Compartido</div>
    </div>
    <div class="riesgo">
      {ICONO_ESCUDO}
      <div class="cont"><h4>Si no logramos vincularlo</h4>
        <p>Si en doce meses no se crea la comunidad, la afiliación termina y usted no paga nada.</p></div>
      <div class="quien">WE POWER</div>
    </div>
    <div class="riesgo">
      {ICONO_ESCUDO}
      <div class="cont"><h4>Cambia la regulación aplicable</h4>
        <p>La estructura se ajusta o se termina sin penalidad para usted.</p></div>
      <div class="quien">WE POWER</div>
    </div>
    <div class="riesgo">
      {ICONO_ESCUDO}
      <div class="cont"><h4>No sabe quién le facturará</h4>
        <p>Se define quién factura y cuántas facturas recibe antes de firmar.</p></div>
      <div class="quien">WE POWER</div>
    </div>
  </div>

  <div class="caja-enfasis" style="margin-top:7mm">
    <h3 style="margin-top:0">Qué firma: su afiliación a We Club</h3>
    <p>Un mandato que nos permite hacer los trámites en su nombre: vincularlo a una comunidad
    energética y firmar por usted el acuerdo de la comunidad y el contrato de suministro.</p>
    <p style="margin:0"><b>¿Cuánto cuesta firmar?</b> Nada. Usted solo empieza a pagar cuando se firme
    el contrato de suministro en su nombre, y en las condiciones de ese contrato.</p>
  </div>
</div>

<!-- ============ 8. SIGUIENTE PASO ============ -->
<div class="pagina">
  {_cab(8, "Siguiente paso", logo)}
  <h2>El único paso de hoy es el primero</h2>

  <div class="destacado">
    <div style="font-size:14pt">Entréguenos su factura y le devolvemos su simulación<br>
      en 5 días hábiles.</div>
  </div>

  <div class="cols" style="margin-top:6mm">
    <div class="col caja">
      <h3 style="margin-top:0">Su asesor</h3>
      <div class="dato"><div class="k">Nombre</div><div class="v">{d['asesor_nombre']}</div></div>
      <div class="dato"><div class="k">Teléfono</div><div class="v">{d['asesor_tel']}</div></div>
      <div class="dato" style="border-bottom:none"><div class="k">Correo</div><div class="v">{d['asesor_mail']}</div></div>
    </div>
    <div class="col caja-borde">
      <h3 style="margin-top:0">We Club en cifras</h3>
      <div class="dato"><div class="k">Energía gestionada</div><div class="v">+100 MW</div></div>
      <div class="dato"><div class="k">Proyectos en el país</div><div class="v">Más de 50</div></div>
      <div class="dato" style="border-bottom:none"><div class="k">Origen de la energía</div><div class="v">100 % solar</div></div>
    </div>
  </div>

  <div class="caja-borde" style="margin-top:7mm">
    <h3 style="margin-top:0">Beneficios de ser parte de We Club</h3>
    <div class="cols">
      <div class="col">
        <p style="margin-bottom:2mm"><b>Energía 100 % renovable.</b> Acceda a energía solar sin
        instalar nada en su sede y reduzca su huella de carbono.</p>
        <p style="margin:0"><b>Ahorro desde el primer día.</b> Calculamos su ahorro con su propia factura.</p>
      </div>
      <div class="col">
        <p style="margin-bottom:2mm"><b>Confiabilidad y control.</b> Sigue conectado con su operador
        actual, así que no arriesga el suministro.</p>
        <p style="margin:0"><b>Inversión cero.</b> WE POWER cubre el 100 % de la inversión,
        incluido el medidor inteligente.</p>
      </div>
    </div>
  </div>

  <p class="nota" style="margin-top:9mm">
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


def armar_datos(form, sim, r, au, proyeccion, consumo, cu, cv, cu_ce):
    return {
        "nombre":    form.get("nombre") or "—",
        "telefono":  form.get("telefono") or "—",
        "direccion": form.get("direccion") or "—",
        "ciudad":    form.get("ciudad") or "—",
        "correo":    form.get("correo") or "",
        "fecha":     form.get("fecha") or datetime.date.today().strftime("%d/%m/%Y"),
        "asesor_nombre": form.get("asesor_nombre") or "—",
        "asesor_tel":    form.get("asesor_tel") or "—",
        "asesor_mail":   form.get("asesor_mail") or "—",
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
    from weasyprint import HTML
    return HTML(string=construir_html(datos), base_url=AQUI).write_pdf()
