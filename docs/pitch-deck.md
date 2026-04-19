# Forged Wheels — Pitch Deck

**Versión:** 1.0 — 19 de abril de 2026
**Audiencia:** Comité Técnico ENISA + potenciales asesores + primeras reuniones con proveedores premium (League Alloy)
**Formato:** 12 slides, para presentación oral de 10-12 minutos

---

## Slide 1 — Portada

**Forged Wheels**
*Custom forged wheels designed by AI on your own car.*

Founder · Andrei Potcenkovskii
SignalWaves SLU · CIF B19996313 · Barcelona · abril 2026
forged-wheels-showroom.vercel.app

---

## Slide 2 — El problema

**Comprar llantas forjadas premium hoy en Europa es doloroso.**

- **Precio alto:** 4.000 – 8.000 € por juego (HRE, Vossen, ADV.1).
- **Espera larga:** 8-16 semanas desde pedido hasta entrega.
- **Incertidumbre estética:** el cliente nunca ve el resultado antes de pagar. Los competidores solo muestran renders 3D sobre coches genéricos, no sobre el tuyo.
- **Cadena de intermediarios:** marca → distribuidor → taller. Cada capa añade margen y fricción.
- **Homologación:** el cliente la gestiona por su cuenta, muchas veces sin documentación adecuada del fabricante.

**Resultado:** un mercado de 1.500 M€/año en Europa donde la mayoría de clientes potenciales abandona antes de comprar por miedo a equivocarse con 5.000 €.

---

## Slide 3 — La solución

**Forged Wheels convierte la decisión estética en 30 segundos.**

1. El cliente sube **una foto de su coche**.
2. Elige un diseño del catálogo o pide uno totalmente personalizado.
3. La IA **renderiza el resultado fotorrealista sobre su coche real** en menos de 60 segundos.
4. Itera hasta estar conforme. Paga. Recibe su juego único fabricado bajo demanda en 25-35 días, con la documentación EU completa para homologar legalmente.

**Lo que cambia respecto al status quo:**

- **Precio:** desde 1.500 € por juego (4-6× más barato que HRE).
- **Plazo:** 25-35 días (2-4× más rápido).
- **Experiencia:** 100 % digital, visualización real, iteraciones infinitas gratuitas.
- **Homologación:** integrada de serie, no coste oculto.

---

## Slide 4 — Cómo funciona la IA

**Pipeline propietario multi-modelo en 4 etapas.**

```
Foto cliente ──> Florence-2 ──> BiRefNet ──> Gemini 3 Pro Image ──> Resultado
                  detecta       limpia        sustituye wheel
                  ruedas        fondo         conservando luz,
                                              perspectiva y reflejos
```

- **Florence-2** (Microsoft) — detección de ruedas.
- **BiRefNet** (fal.ai) — eliminación de fondo subpíxel.
- **Gemini 3 Pro Image** (Google DeepMind) — sustitución *reference-based* fotorrealista.
- **Orquestación, prompts, dataset y lógica de negocio son propietarios**, depositados notarialmente como secreto empresarial al amparo de la Ley 1/2019.

**Ventaja técnica:** ningún competidor europeo ofrece hoy visualización fotorrealista sobre foto real del cliente. Lo más cercano (Vossen Configurator) muestra renders 3D sobre modelos genéricos.

---

## Slide 5 — Tracción y estado actual

**abril 2026 · lanzamiento comercial junio 2026**

| Hito | Estado |
|---|---|
| Plataforma en producción | ✅ forged-wheels-showroom.vercel.app |
| 21 diseños premium en catálogo | ✅ |
| Pipeline AI operativo y testeado | ✅ |
| Empresa SignalWaves SLU constituida | ✅ |
| Investigación de 13 fabricantes premium | ✅ |
| 5 RFQs enviadas (Wuxi Susha, Kipardo, GVICHN, Wheelshome, League Alloy) | ✅ |
| Protocolo notarial de secreto empresarial | ✅ |
| Solicitud Marca OEPM | 🟡 en trámite |
| CNAE 4531 en SL | 🟡 en trámite |
| Primera venta comercial | 🎯 junio 2026 |

---

## Slide 6 — Mercado

**Mercado global aftermarket de llantas: 21.800 M$ (2024), CAGR 6,8 % hasta 2030** (Grand View Research).

Foco: **segmento forjado premium europeo** — 1.500-1.800 M€/año, crecimiento 8 %.

### Segmentación del cliente

- **Primario "Premium customizer"** — dueños de BMW, Mercedes, Audi, Porsche, 30-50 años, renta familiar > 60.000 €/año.
- **Secundario "Track day enthusiast"** — M / AMG / RS / S, 4-8 track days/año.
- **Terciario "Lead to dealer"** — clientes que usan la plataforma para visualizar y compran en un concesionario partner (línea de lead-gen).

### Geografía

🇪🇸 España (Fase 1, junio 2026) → 🇩🇪 Alemania (Fase 2, Q4 2026) → 🇮🇹 Italia (Fase 3, Q2 2027) → 🇫🇷 Francia (Fase 4, Q4 2027).

---

## Slide 7 — Competencia

| Competidor | Precio | Plazo | IA try-on | Bespoke real | Web EU propia |
|---|---|---|---|---|---|
| HRE Performance Wheels | 6.000-8.000 € | 12-16 sem | ❌ | Parcial | Solo distribuidores |
| Vossen | 4.000-6.500 € | 8-12 sem | ❌ | Catálogo | Sí (US) |
| ADV.1 | 5.500-8.000 € | 10-14 sem | ❌ | Parcial | No |
| BC Forged | 3.500-5.500 € | 8-12 sem | ❌ | Sí | Distribuidores |
| Forgiato | 6.000-15.000 € | 10-14 sem | ❌ | Sí | Solo dealers |
| **Forged Wheels** | **1.500-3.000 €** | **3-5 sem** | **✅ Gemini 3** | **✅** | **✅ Propia** |

### Fosos competitivos

1. **Tecnológico** — IA try-on fotorrealista, pipeline propietario con depósito notarial.
2. **De coste** — venta directa, sin intermediarios.
3. **Regulatorio local** — único que integra documentación de homologación española (Reforma de Importancia) en el producto.

---

## Slide 8 — Modelo de negocio

**Tres líneas de ingreso, margen creciente.**

### 1. B2C venta directa (95 % Y1 → 87 % Y3)

- PMV: 1.800 € (Y1) → 2.200 € (Y3).
- COGS: 950 € → 1.050 €.
- Margen bruto: **43,6 % → 50,1 %**.
- Cobro 100 % al pedido, sin fiado.

### 2. Lead-gen B2B (0 % → 0,2 %)

- Cliente indeciso se deriva a concesionario partner.
- Comisión: 200 € por lead cualificado.

### 3. SaaS white-label (0 % → 2,0 %)

- Licencia del motor IA a marcas tradicionales sin capacidad técnica.
- Fee: 3.000 €/mes por cliente. Pipeline: 2 conversaciones iniciadas.
- Margen: 70 %+.

### Unit economics

- **LTV:** 635 € (Y1) → 820 € (Y3).
- **CAC blended:** 180 € (Y1) → 120 € (Y3).
- **LTV / CAC:** **3,5x → 6,8x**.
- **Payback CAC:** 5 meses.

---

## Slide 9 — Proyección financiera

**Plan de crecimiento sostenible — tres años.**

| Magnitud | Año 1 | Año 2 | Año 3 |
|---|---|---|---|
| Juegos vendidos | 120 | 850 | 2.400 |
| **Ingresos totales** | **216 k€** | **1,74 M€** | **5,40 M€** |
| Margen bruto | 43,6 % | 47,8 % | 50,1 % |
| **EBITDA** | **−39 k€** | **+533 k€** | **+2,21 M€** |
| Beneficio neto post-IS | −46 k€ | +436 k€ | +1,64 M€ |
| Caja al cierre del año | 52 k€ | 452 k€ | 1,78 M€ |

- **Break-even EBITDA mensual:** mes 7 (dic 2026).
- **Break-even EBITDA acumulado:** mes 13 (jun 2027).
- **Sin necesidad de financiación adicional** durante los 3 años.

Análisis de sensibilidad: la caja mínima se mantiene positiva incluso en escenario pesimista (−25 % ventas + 30 % CAC + 15 días retraso).

---

## Slide 10 — Equipo y gobierno

**Fundador — Andrei Potcenkovskii**

- **25+ años de trayectoria empresarial** (construcción residencial en Rusia 2000-2020 → plataformas digitales con IA desde 2024).
- Licenciado en Economía · Técnico Superior en Construcción de Maquinaria.
- Ingeniería full-stack + experiencia práctica en modelos generativos (Gemini 3 Pro, Nano Banana, Florence-2, BiRefNet).
- Proyectos activos en paralelo: **SignalWaves Auto** (importación de vehículos DE→ES con garaje en Barcelona), **PsychAuto** (psihavto.tilda.ws, 3 idiomas, ~1.000 tests completados).
- Residencia legal en España desde 2024, en proceso de modificación a autorización de Emprendedor (Ley 14/2013) tras resolución ENISA.

**Advisory Board** — en formación (3 perfiles objetivo):

1. Ingeniería automotriz / homologación (TÜV / IDIADA).
2. E-commerce premium EU.
3. Supply chain Asia-EU (automotive).

**Gobierno corporativo:** SignalWaves SLU, administradora única Dña. Elizaveta Ilina. Está prevista la incorporación del fundador como administrador mancomunado en el primer mes tras la resolución ENISA favorable, mediante acta notarial e inscripción en el Registro Mercantil.

---

## Slide 11 — Solicitud ENISA — 75.000 €

**Línea Emprendedores · TIN 4,75 % · carencia 24 m · plazo 96 m.**

### Uso de fondos

| Partida | Importe | % | Mes |
|---|---|---|---|
| Homologación TÜV (3 SKUs propios) | 12.000 € | 16 % | M2-M4 |
| Desarrollo producto (checkout + CRM) | 8.000 € | 11 % | M1-M3 |
| Samples pre-producción | 6.500 € | 9 % | M1-M2 |
| Marca OEPM + EUIPO | 1.200 € | 2 % | M1 |
| Marketing lanzamiento (M1-M3) | 9.000 € | 12 % | M1-M3 |
| Salario fundador (M4-M15) | 20.000 € | 27 % | M4-M15 |
| Ingeniero CAD freelance | 10.000 € | 13 % | M4-M15 |
| Infraestructura 18 meses | 6.300 € | 8 % | Mensual |
| RC Producto + seguros | 2.000 € | 3 % | M1 |
| **TOTAL** | **75.000 €** | **100 %** | |

Complementado con 8.000 € de aporte propio del fundador ya aportados como fondo de maniobra.

---

## Slide 12 — Llamada a la acción

**Junio 2026: lanzamos en España.**
**Noviembre 2026: abrimos Alemania.**

Con el apoyo de ENISA alcanzamos:

- **2 años: +1,7 M€ facturación y EBITDA positivo 21 %.**
- **3 años: +5,4 M€ facturación y EBITDA 30 %.**
- **IP protegido** — Protocolo notarial de secreto empresarial + marcas OEPM + EUIPO.
- **Cadena de suministro verificada** con proveedores TÜV/JWL/VIA en China y Taiwán.
- **Dataset propio creciente** de +25.000 renders sobre coches reales al cierre Y3.

> *"Estamos construyendo la primera plataforma europea que elimina la incertidumbre estética en el mercado de llantas forjadas premium — el mismo salto que Warby Parker dio en gafas o que The Farfetch dio en moda de lujo."*

**Contacto:**
📧 pozenkov13@gmail.com
📱 +34 628 106 939
🌐 forged-wheels-showroom.vercel.app

---

*Deck preparado para: Comité Técnico ENISA · Advisory candidates · League Alloy / primeras factory visits.*
