#  El reparto es proporcional al consumo: todos los usuarios quedan con la
#  MISMA cobertura (índice de distribución = 1), salvo los que chocan contra
#  su techo. Al entrar un usuario nuevo se recalculan TODOS los PDE.


# =========================================================
# 1. PARÁMETROS DE LA PLANTA
# =========================================================

GENERACION_ANUAL_KWH = 1_800_000.0

GENERACION_MENSUAL_KWH = GENERACION_ANUAL_KWH / 12

CAPACIDAD_INSTALADA_KWP = None


# =========================================================
# 2. PARÁMETROS REGULATORIOS
# =========================================================

PDE_MAXIMO_LEGAL = 0.099

MIN_FRONTERAS = 11

LIMITE_AGPE_KWP = 1000.0
LIMITE_CIN_AC_KW = 100.0


# =========================================================
# 3. PARÁMETROS TARIFARIOS
# =========================================================

CONTRIBUCION = 0.20

TIPO1_EXENTO_DE_CONTRIBUCION = True


# =========================================================
# 4. PARÁMETROS DE DIMENSIONAMIENTO
# =========================================================

#   RESTRICCIÓN DURA : Σ PDE = 100 % y cada PDE < 10 %.  No es negociable.
#   OBJETIVO         : que todos los miembros ahorren.
#   CRITERIO         : repartir proporcional al consumo, con la MISMA cobertura
#                      para todos (índice de distribución = 1).

TOPE_CONSUMO = 0.80


# =========================================================
# 5. PARÁMETROS DE PROYECCIÓN
# =========================================================

INFLACION_RED_ANUAL = 0.05
INFLACION_CE_ANUAL = 0.03


# =========================================================
# 6. LOS PLANES
# =========================================================

#   Un plan es una COBERTURA: qué parte del consumo del usuario pone la CE.
#   El PDE se deriva de ahí, con la misma fórmula del techo individual del
#   Excel:  min(9,9 % , cobertura x consumo / generación).
#
#   El plan ESTÁNDAR (80 %) es exactamente ese techo. Los otros dos son el
#   mismo cálculo con otra cobertura.

PLAN_BASICO = 0.30        # ~ PDE 3 % para un usuario de 15.000 kWh/mes
PLAN_ESTANDAR = TOPE_CONSUMO
PLAN_PREMIUM = 1.00

PLANES = (("Básico", PLAN_BASICO),
          ("Estándar", PLAN_ESTANDAR),
          ("Premium", PLAN_PREMIUM))


# =========================================================
# 7. DATOS DE LA COMUNIDAD PARA MOSTRAR
# =========================================================
#   No entran en ningún cálculo: son solo para escribirlos en pantalla.
#   Antes aquí vivía la lista de los 12 contratos con su PDE declarado. Se
#   quitó porque el PDE ya no sale de repartir la planta entre los miembros,
#   sino del plan que elige el usuario: la calculadora no necesita saber
#   quién más está adentro. Las funciones repartir_por_consumo() y
#   validar_comunidad() siguen aquí abajo, intactas, para quien arme la
#   comunidad y para la verificación contra el Excel.

MIEMBROS_ACTUALES = 12


# =========================================================
# FORMATO Y ENTRADA
# =========================================================

def formatear(valor, decimales=0):
    if abs(valor) < 0.5 * (10 ** -decimales):
        valor = 0.0
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "@").replace(".", ",").replace("@", ".")


def cop(valor, decimales=0):
    return "$ " + formatear(valor, decimales)


def pct(valor, decimales=2):
    return formatear(valor * 100, decimales) + " %"


def texto_a_numero(texto):
    limpio = texto.strip().replace("$", "").replace(" ", "").replace("%", "")
    if "," in limpio:
        limpio = limpio.replace(".", "").replace(",", ".")
    elif limpio.count(".") > 1:
        limpio = limpio.replace(".", "")
    return float(limpio)


def preguntar(mensaje, minimo=None, maximo=None, ayuda=""):
    print(f"\n{mensaje}")
    if ayuda:
        print(f"   ({ayuda})")
    while True:
        try:
            valor = texto_a_numero(input("   > "))
        except (ValueError, EOFError):
            print("  Eso no parece un número. Intenta otra vez.")
            continue
        if minimo is not None and valor < minimo:
            print(f"  Tiene que ser mayor o igual a {formatear(minimo, 2)}.")
            continue
        if maximo is not None and valor > maximo:
            print(f"  Tiene que ser menor o igual a {formatear(maximo, 2)}.")
            continue
        return valor


def preguntar_si_no(mensaje, ayuda=""):
    print(f"\n{mensaje}")
    if ayuda:
        print(f"   ({ayuda})")
    while True:
        try:
            r = input("   > ").strip().lower()
        except EOFError:
            return True
        if r in ("s", "si", "sí", "y", "yes", "1"):
            return True
        if r in ("n", "no", "0"):
            return False
        print("  Responde 's' o 'n'.")


def titulo(texto):
    print("\n" + "=" * 78)
    print(f" {texto}")
    print("=" * 78)


def seccion(texto):
    print("\n" + "▔" * 78)
    print(f" {texto}")
    print("▔" * 78)


# =========================================================
# VALIDACIÓN REGULATORIA
# =========================================================

def validar_comunidad(pdes, n_fronteras):
    """Devuelve (ok, lista_de_hallazgos). Un hallazgo es (nivel, mensaje)."""
    hallazgos = []

    suma = sum(pdes)
    if abs(suma - 1.0) > 1e-6:
        hallazgos.append(("ERROR", f"La suma de los PDE es {pct(suma, 4)}, debe ser 100,0000 % (Art. 19)."))

    violan = [i for i, p in enumerate(pdes) if p >= 0.10]
    if violan:
        hallazgos.append(("ERROR",
            f"{len(violan)} usuario(s) con PDE >= 10 %. Rompe el Art. 20 num. 1 iii): "
            "TODA la comunidad pierde el crédito de energía, no solo ese usuario."))

    if any(p < 0 for p in pdes):
        hallazgos.append(("ERROR", "Hay PDE negativos. La reasignación pidió más de lo disponible."))

    if n_fronteras < MIN_FRONTERAS:
        hallazgos.append(("ERROR",
            f"Con {n_fronteras} fronteras es imposible que todos queden por debajo del 10 %. "
            f"Se necesitan al menos {MIN_FRONTERAS}."))

    if CAPACIDAD_INSTALADA_KWP is not None:
        if CAPACIDAD_INSTALADA_KWP > LIMITE_AGPE_KWP:
            hallazgos.append(("ERROR",
                f"Capacidad instalada {formatear(CAPACIDAD_INSTALADA_KWP, 0)} kWp > "
                f"{formatear(LIMITE_AGPE_KWP, 0)} kWp (límite AGPE, Res. UPME 281/2015). "
                "Aplica el Art. 20 num. 3: no hay crédito de energía y este modelo no aplica."))
        cin_ac = CAPACIDAD_INSTALADA_KWP / n_fronteras
        if cin_ac > LIMITE_CIN_AC_KW:
            hallazgos.append(("ERROR",
                f"CIN_AC = {formatear(cin_ac, 1)} kW > {formatear(LIMITE_CIN_AC_KW, 0)} kW "
                "(Art. 18 y Art. 20 num. 1 ii). La comunidad cae al régimen del numeral 2."))
        else:
            hallazgos.append(("OK", f"CIN_AC = {formatear(cin_ac, 1)} kW (límite {formatear(LIMITE_CIN_AC_KW, 0)} kW)."))
    else:
        hallazgos.append(("AVISO",
            "CAPACIDAD_INSTALADA_KWP no está definida: no se validaron el límite de 1 MW "
            "ni CIN_AC <= 100 kW."))

    ok = not any(n == "ERROR" for n, _ in hallazgos)
    return ok, hallazgos


# =========================================================
# ASIGNACIÓN DE PDE
# =========================================================

def energia_asignada(pde):
    """kWh que le corresponden a un PDE en un mes."""
    return GENERACION_MENSUAL_KWH * pde


def pde_por_cobertura(cobertura, consumo):
    """De 'quiero cubrir X % de mi consumo' al PDE que hay que declarar.

    Es la misma fórmula del techo individual del Excel. El tope del 9,9 %
    no es negociable: Art. 20 num. 1 iii) de la Res. CREG 101 072 de 2025.
    """
    return min(PDE_MAXIMO_LEGAL, cobertura * consumo / GENERACION_MENSUAL_KWH)


def repartir_por_consumo(consumos):
    """
    Se resuelve por rondas:
      1. Se reparte lo que queda proporcional al consumo de los que siguen libres.
      2. El que se pasa de su techo se fija ahi y sale de la reparticion.
      3. Lo que sobro se vuelve a repartir entre los que quedan.

    Devuelve (pdes, lambda, indices de los usuarios topados).
    """
    n = len(consumos)
    if n == 0:
        return [], 0.0, set()

    techos = [min(PDE_MAXIMO_LEGAL, TOPE_CONSUMO * c / GENERACION_MENSUAL_KWH)
              for c in consumos]

    # Si la suma de los techos no llega al 100 %, la cartera no puede absorber
    # toda la generacion: no hay reparto posible bajo estas reglas.
    if sum(techos) < 1.0 - 1e-12:
        raise ValueError(
            f"Los techos suman {pct(sum(techos), 2)}: la cartera no alcanza a absorber "
            f"el 100 % de la generacion. Hay que subir TOPE_CONSUMO (hoy "
            f"{pct(TOPE_CONSUMO, 0)}) o meter mas usuarios.")

    topados = set()
    lam = 0.0
    for _ in range(200):
        resto = 1.0 - sum(techos[i] for i in topados)
        base = sum(consumos[i] for i in range(n) if i not in topados)
        if base <= 0:
            break
        lam = resto / base
        nuevos = {i for i in range(n)
                  if i not in topados and lam * consumos[i] >= techos[i] - 1e-15}
        if not nuevos:
            break
        topados |= nuevos

    pdes = [techos[i] if i in topados else lam * consumos[i] for i in range(n)]

    # Ajuste final por decimales, para que sume 100 % exacto
    dif = 1.0 - sum(pdes)
    if abs(dif) > 1e-12:
        for i in sorted(range(n), key=lambda k: pdes[k], reverse=(dif < 0)):
            espacio = (techos[i] - pdes[i]) if dif > 0 else pdes[i]
            paso = dif if abs(dif) <= espacio else (espacio if dif > 0 else -espacio)
            pdes[i] += paso
            dif -= paso
            if abs(dif) <= 1e-12:
                break

    return pdes, lam, topados


# =========================================================
# MOTOR FINANCIERO  (Art. 26 Res. CREG 174/2021, lit. a)
# =========================================================

# La sección está organizada en tres bloques:
#
#   BLOQUE 1 -> ahorro_unitario_tipo1()  : cuánto se ahorra en UN kWh (el átomo)
#   BLOQUE 2 -> balance_mensual()        : las dos facturas del mes
#   BLOQUE 3 -> balance_mensual()        : la resta, que debe coincidir con B1 × kWh

# APARTE: umbrales_precio() NO calcula ningún ahorro. Es un semáforo para juzgar
# el precio acordado. Si se borrara, el ahorro saldría exactamente igual.
# =========================================================


#  semáforo del precio

def umbrales_precio(cu, cv, contrib):
    """Solo dice si el precio es sano, alto o inviable."""
    return {

        "neutro_tarifa": cu - cv,

        "techo_absoluto": cu * (1 + contrib) - cv,
    }


# BLOQUE 1: el ahorro de UN kWh (el átomo de todo el modelo)

def ahorro_unitario_tipo1(cu, cv, cu_ce, contrib):
    """
    lo que pasa cuando la ce entrega un kwh:

      1. Ese kWh desaparece de su factura de la red
      2. ...y con él desaparece su contribución
      3. Pero el comercializador le cobra el Cv
      4. Y le paga a la comunidad su precio

    Neto:  CU × (1 + contrib) − Cv − CU_CE

    """
    # Pedazo 1: lo que gana en el precio de la energía.
    por_tarifa = cu - cv - cu_ce

    # Pedazo 2
    por_contribucion = cu * contrib if TIPO1_EXENTO_DE_CONTRIBUCION else 0.0

    total = por_tarifa + por_contribucion
    costo_red = cu * (1 + contrib)   # lo que ese kWh le cuesta hoy, con contribucion

    return {
        "por_tarifa": por_tarifa,
        "por_contribucion": por_contribucion,
        "total": total,
        "costo_red": costo_red,
        "descuento_efectivo": total / costo_red if costo_red > 0 else 0.0,
    }


# BLOQUE 2 y 3: las dos facturas del mes, y la resta

def balance_mensual(consumo, pde, cu, cv, cu_ce, contrib):
    """Arma UN mes con el consumo promedio y saca el ahorro.

        SIN comunidad   consumo × cu × 1,20

        CON comunidad   (consumo−asignada) × cu × 1,20   = ....
                        asignada × (cargo Cv)            = ....
                        asignada × cu_ce                 = ....
                                                           ────────────
                                                           $suma de los 3

        AHORRO = sin_ce − con_ce                 = $....

    Comprobación (BLOQUE 3): solo confirma, coge lo asignado y lo multiplica por el ahorro(CU × (1 + contribución) − Cv − CU_CE = ...).
    """
    asignada = energia_asignada(pde)

    exc1 = min(asignada, consumo)
    exc2 = max(asignada - consumo, 0.0)

    # --- Factura SIN comunidad: compra todo su consumo a la red, con impuesto
    factura_sin = consumo * cu * (1 + contrib)

    # --- Factura CON comunidad: queda partida en tres renglones
    # 1) Lo que le sigue comprando a la red (lo que la CE no alcanzó a cubrir).
    #    Paga precio completo y sí carga contribución.
    energia_red = consumo - exc1
    pago_red = energia_red * cu * (1 + contrib)
    # 2) El cargo del Art. 26: por cada kWh permutado el comercializador acredita
    #    el CUv y cobra de vuelta el Cv. Este es el renglón que casi todos los
    #    modelos olvidan.
    cargo_cv = exc1 * cv
    # 3) Lo que le paga a la comunidad. Modalidad "páguelo asignado": se le cobra
    #    TODO lo asignado, no solo lo permutado. Y no carga contribución, porque
    #    no es el servicio público regulado sino una compraventa aparte.
    pago_ce = asignada * cu_ce
    factura_con = pago_red + cargo_cv + pago_ce

    # --- BLOQUE 3: el ahorro es la resta. Debe coincidir con exc1 × ahorro
    #     unitario del BLOQUE 1 (lo verifica una prueba automática).
    ahorro = factura_sin - factura_con

    return {
        "asignada": asignada,
        "exc1": exc1,
        "exc2": exc2,
        "cobertura": asignada / consumo if consumo > 0 else 0.0,
        "energia_red": energia_red,
        "factura_sin": factura_sin,
        "pago_red": pago_red,
        "cargo_cv": cargo_cv,
        "pago_ce": pago_ce,
        "factura_con": factura_con,
        "ahorro_mes": ahorro,
        "ahorro_anual": ahorro * 12,
        "ahorro_pct": ahorro / factura_sin if factura_sin > 0 else 0.0,
    }


# --- Proyección: repite el mes del BLOQUE 2 una vez por año -----------------

def proyectar(consumo, pde, cu0, cv0, cu_ce0, contrib, anios):
    """Vuelve a armar el mismo mes año por año, moviendo solo los precios.

    El CU y el Cv suben con la inflación de la red; el CU_CE con la de la CE.
    El PDE no se mueve: se asume que el acuerdo con la comunidad se mantiene.
    Como la red sube más rápido que la CE, la brecha se abre y el ahorro crece.
    """
    filas = []
    acumulado = 0.0
    for a in range(anios):
        f = (1 + INFLACION_RED_ANUAL) ** a
        g = (1 + INFLACION_CE_ANUAL) ** a
        r = balance_mensual(consumo, pde, cu0 * f, cv0 * f, cu_ce0 * g, contrib)
        acumulado += r["ahorro_anual"]
        filas.append({
            "anio": a + 1,
            "cu": cu0 * f,
            "cu_ce": cu_ce0 * g,
            "ahorro_anual": r["ahorro_anual"],
            "ahorro_pct": r["ahorro_pct"],
            "acumulado": acumulado,
        })
    return filas


# =========================================================
# PROGRAMA PRINCIPAL
# =========================================================

def main():
    titulo("CALCULADORA DE AHORRO · COMUNIDAD ENERGÉTICA")
    print(f" Planta: {formatear(GENERACION_MENSUAL_KWH, 0)} kWh/mes  ·  "
          f"{MIEMBROS_ACTUALES} miembros actuales")

    # ---------- 1. DATOS DEL USUARIO ----------
    seccion("1. DATOS DEL USUARIO")

    cu = preguntar("1. Costo unitario de la energía, CU (COP/kWh)",
                   minimo=1, maximo=5000,
                   ayuda="El valor por kWh de su factura actual, antes de contribución")

    cv = preguntar("2. Componente de comercialización, Cv (COP/kWh)",
                   minimo=0, maximo=cu,
                   ayuda="Está dentro del CU. El comercializador lo cobra por cada kWh permutado (Art. 26)")

    paga_contribucion = preguntar_si_no(
        "3. ¿El usuario paga contribución de solidaridad? (s/n)",
        ayuda="Sí: estratos 5 y 6, comerciales. No: industriales exentos por CIIU (Ley 1430/2010)")
    contrib = CONTRIBUCION if paga_contribucion else 0.0

    consumo = preguntar("4. Consumo PROMEDIO mensual (kWh)", minimo=1,
                        ayuda="Promedio de los últimos 6 a 12 meses")

    cu_ce = preguntar("5. Precio acordado con la comunidad, CU_CE (COP/kWh)", minimo=1,
                      ayuda="El precio al que la CE le venderá el kWh")

    anios = int(preguntar("6. Período de análisis (años)", minimo=1, maximo=25,
                          ayuda="Para la proyección con inflación"))

    # ---------- 2. DIAGNÓSTICO DEL PRECIO ----------
    seccion("2. DIAGNÓSTICO DEL PRECIO ACORDADO")

    umb = umbrales_precio(cu, cv, contrib)
    au = ahorro_unitario_tipo1(cu, cv, cu_ce, contrib)

    print(f"  Costo real del kWh en la red        = {cop(au['costo_red'], 2):>14}"
          f"   (CU x {formatear(1 + contrib, 2)})")
    print(f"  Precio acordado con la comunidad    = {cop(cu_ce, 2):>14}")

    if cu_ce >= umb["techo_absoluto"]:
        print("\n  >> Con este precio el usuario NO ahorra nada.")
        print(f"     El CU_CE tendría que bajar de {cop(umb['techo_absoluto'], 2)}.")
        return

    print("\n  DESGLOSE DEL AHORRO POR CADA kWh TIPO 1:")
    print(f"     Ahorro por tarifa (CU - Cv - CU_CE) = {cop(au['por_tarifa'], 2):>12}")
    print(f"     Ahorro por contribución (CU x {formatear(contrib, 2)}) = {cop(au['por_contribucion'], 2):>12}")
    print(f"     {'-' * 52}")
    print(f"     AHORRO UNITARIO TOTAL               = {cop(au['total'], 2):>12}")
    print(f"     Descuento efectivo sobre el costo real = {pct(au['descuento_efectivo'], 2):>9}")

    # ---------- 3. LOS TRES PLANES ----------
    seccion("3. LOS TRES PLANES")
    print("  El PDE sale de la cobertura del plan, topado en el 9,9 % legal.")
    print()
    print(f"  {'PLAN':<10}{'PDE':>9}{'kWh/MES':>11}{'COBERTURA':>11}"
          f"{'AHORRO/MES':>16}{'% FACTURA':>11}")
    print("-" * 78)

    resultados = {}
    for nombre, cobertura in PLANES:
        pde = pde_por_cobertura(cobertura, consumo)
        r = balance_mensual(consumo, pde, cu, cv, cu_ce, contrib)
        resultados[nombre] = (pde, r)
        print(f"  {nombre:<10}{pct(pde, 3):>9}{formatear(r['asignada'], 0):>11}"
              f"{pct(r['cobertura'], 1):>11}{cop(r['ahorro_mes']):>16}"
              f"{pct(r['ahorro_pct'], 1):>11}")
    print("-" * 78)

    # Única validación que le corresponde a una calculadora: el tope individual.
    # Las de comunidad (Sigma PDE = 100 %, minimo 11 fronteras, CIN_AC) las hace
    # validar_comunidad() cuando se arma el roster, no aquí.
    peor = max(p for p, _ in resultados.values())
    if peor >= 0.10:
        print(f"  [ERROR] Un PDE de {pct(peor, 3)} rompe el Art. 20 num. 1 iii).")
        return
    print(f"  [OK] El PDE más alto es {pct(peor, 3)}, por debajo del 10 % (Art. 20 num. 1 iii).")

    tope_kwh = PDE_MAXIMO_LEGAL * GENERACION_MENSUAL_KWH
    if resultados["Premium"][1]["cobertura"] < 0.995:
        print(f"  [AVISO] El Premium no llega al 100 %: la ley no deja asignarle a un"
              f" solo usuario\n          más de {formatear(tope_kwh, 0)} kWh/mes"
              f" ({pct(resultados['Premium'][1]['cobertura'], 0)} de su consumo).")

    # ---------- 4. LA FACTURA CON EL PLAN ESTÁNDAR ----------
    pde_est, r = resultados["Estándar"]
    seccion("4. LA FACTURA CON EL PLAN ESTÁNDAR")

    et = lambda txt: f"     {txt:<44}"
    print("  ANTES:")
    print(et(f"{formatear(consumo, 0)} kWh x {cop(cu, 2)} x {formatear(1 + contrib, 2)}")
          + f"= {cop(r['factura_sin']):>14}")
    print("\n  AHORA:")
    print(et(f"Energía de la red ({formatear(r['energia_red'], 0)} kWh)")
          + f"= {cop(r['pago_red']):>14}")
    print(et(f"Cargo Cv sobre lo permutado ({formatear(r['exc1'], 0)} kWh)")
          + f"= {cop(r['cargo_cv']):>14}")
    print(et(f"Pago a la comunidad ({formatear(r['asignada'], 0)} kWh)")
          + f"= {cop(r['pago_ce']):>14}")
    print(f"     {'-' * 60}")
    print(et("TOTAL") + f"= {cop(r['factura_con']):>14}")
    print(f"\n  AHORRO: {cop(r['ahorro_mes'])} al mes  ·  {cop(r['ahorro_anual'])} al año"
          f"  ·  {pct(r['ahorro_pct'], 2)} de la factura")
    print(f"  Del ahorro, {cop(r['exc1'] * au['por_contribucion'], 0)} viene de la contribución"
          f" evitada y\n  {cop(r['exc1'] * au['por_tarifa'], 0)} del diferencial tarifario.")
    print("\n  Es un estimado: está calculado con el consumo promedio. Si un mes")
    print("  consume más, ahorra más; si consume menos, ahorra menos.")

    # ---------- 5. PROYECCIÓN ----------
    seccion(f"5. PROYECCIÓN A {anios} AÑO(S) — PLAN ESTÁNDAR")
    print(f"  Supuestos: red +{pct(INFLACION_RED_ANUAL, 1)}/año, "
          f"CE +{pct(INFLACION_CE_ANUAL, 1)}/año, PDE estático.")
    print()
    print(f"  {'AÑO':>4} {'CU RED':>12} {'CU CE':>12} {'AHORRO AÑO':>16} {'%':>8} {'ACUMULADO':>16}")
    print("-" * 78)
    for f in proyectar(consumo, pde_est, cu, cv, cu_ce, contrib, anios):
        print(f"  {f['anio']:>4} {cop(f['cu'], 2):>12} {cop(f['cu_ce'], 2):>12} "
              f"{cop(f['ahorro_anual']):>16} {pct(f['ahorro_pct'], 1):>8} {cop(f['acumulado']):>16}")
    print("-" * 78)

    print("\n  NOTA OPERATIVA: cambiar el PDE exige informar al comercializador con")
    print("  10 días hábiles de anticipación al inicio del ciclo de facturación (Art. 19).")


if __name__ == "__main__":
    main()
