# Plan de Empresa — Forged Wheels

**Empresa:** SignalWaves, Sociedad Limitada Unipersonal (SLU)
**CIF:** B19996313
**Domicilio social:** Carrer Pere IV, 37, 1º 3ª, 08018 Barcelona
**Plataforma:** forged-wheels-showroom.vercel.app
**Fundador:** Andrei Potcenkovskii
**Contacto:** pozenkov13@gmail.com · +34 628 106 939
**Versión:** v2 — 19 de abril de 2026
**Destinatario:** ENISA — Línea Emprendedores

**Cambios v2 respecto a v1** (tras review del evaluador Miguel Alonso Serra):
- Cifras de EBITDA, beneficio neto y uso de fondos sincronizadas al céntimo con el modelo financiero Excel v2
- Incorporación de Impuesto sobre Sociedades (15% Y1-Y2, 25% desde Y3), IVA trimestral, Seguridad Social empresa y RC Producto
- Cuota ENISA recalculada (Línea Emprendedores: TIN 4,75% fijo + tipo variable, carencia 24 meses, 72 meses amortización)
- Análisis de sensibilidad con tres escenarios (Pesimista / Base / Optimista)
- Sección nueva de Unit Economics con LTV / CAC
- Reducción del peso del salario fundador en el uso del préstamo ENISA del 40% al 27%

---

## 1. Resumen ejecutivo

**Forged Wheels** es una plataforma de comercio electrónico basada en inteligencia artificial que permite a propietarios de vehículos premium diseñar y encargar **llantas forjadas de aluminio totalmente personalizadas** para su coche específico, eliminando la principal barrera del mercado actual de tuning de alta gama: la incertidumbre sobre el resultado estético final.

El producto central es un motor de **visualización fotorrealista mediante IA (Gemini 3 Pro Image)** que muestra al cliente, en tiempo real y sobre una fotografía de su propio vehículo, exactamente cómo quedarán las llantas elegidas o diseñadas a medida. Una vez confirmado el diseño, la plataforma gestiona la fabricación bajo demanda (*bespoke single-set*) en fábricas forjadoras asiáticas con certificación EU (TÜV / JWL-VIA) y la entrega homologada al cliente final en España y la Unión Europea.

**Oportunidad:** el mercado europeo de llantas forjadas de aftermarket premium mueve más de **1.500 M€/año**, con crecimiento anual del 8% (Grand View Research 2024-2027). Los líderes actuales (HRE, Vossen, ADV.1, BC Forged) operan con plazos de 8-16 semanas, precios de 4.000-8.000 € por juego, sin herramientas digitales de visualización y requiriendo visita presencial a un distribuidor. Forged Wheels disrumpe la categoría combinando **IA de visualización + fabricación directa + homologación EU integrada**, ofreciendo un juego único a medida desde 1.500 € y entrega en 25-35 días.

**Modelo de negocio híbrido:** (1) venta directa B2C, (2) generación de leads para concesionarios y talleres de tuning, (3) licencia SaaS white-label de la tecnología de visualización a fabricantes tradicionales.

**Estado actual (abril 2026):** MVP plenamente funcional y en producción, 21 diseños de referencia en catálogo, motor de IA operativo, empresa constituida, infraestructura técnica desplegada (Vercel, fal.ai, API propia), red de 13 fabricantes investigados, 5 RFQs enviadas a proveedores certificados.

**Necesidad de financiación:** **75.000 €** a través de la Línea Emprendedores de ENISA, complementados con un aporte propio de 8.000 € del fundador.

### Previsión financiera consolidada (modelo Excel v2)

| Magnitud | Año 1 (Jun26-May27) | Año 2 (Jun27-May28) | Año 3 (Jun28-May29) |
|---|---|---|---|
| Juegos vendidos | 120 | 850 | 2.400 |
| **Ingresos totales** | **216.000 €** | **1.739.600 €** | **5.397.600 €** |
| Margen bruto | 94.177 € (43,6%) | 831.248 € (47,8%) | 2.706.034 € (50,1%) |
| **EBITDA** | **−39.213 €** | **+532.628 €** | **+2.211.034 €** |
| Amortización | 3.978 € | 5.304 € | 5.304 € |
| EBIT | −43.191 € | +527.324 € | +2.205.730 € |
| Intereses ENISA (TIN 4,75%) | 3.564 € | 3.564 € | 14.388 € |
| Resultado antes impuestos | −46.755 € | +523.760 € | +2.191.342 € |
| Impuesto Sociedades (15%/25%) | 0 € | 78.564 € | 547.836 € |
| **Beneficio neto** | **−46.755 €** | **+445.196 €** | **+1.643.506 €** |
| Caja al final de año | 51.861 € | 460.938 € | 1.784.181 € |

Nota: el Año 1 cierra con EBITDA ligeramente negativo (−39 k€) por ser año de lanzamiento. **El EBITDA mensual se vuelve positivo en el mes 7** (diciembre 2026, +378 €); **el EBITDA acumulado alcanza el equilibrio en el mes 13** (junio 2027). La empresa no requiere financiación adicional a lo largo de los tres primeros años.

**Equipo:** fundador único inicialmente (Andrei Potcenkovskii), ingeniero de software con más de 10 años de experiencia y emprendedor serial (proyectos previos: SignalWaves Auto, PsychAuto). Advisory Board en constitución con tres perfiles objetivo: ingeniería automotriz, e-commerce premium EU y homologación vehicular española.

---

## 2. La empresa y el equipo

### 2.1 Datos registrales

| Campo | Valor |
|---|---|
| Razón social | SignalWaves, Sociedad Limitada Unipersonal |
| Forma jurídica | SLU |
| CIF | B19996313 |
| Fecha de constitución | 06/08/2024 |
| Fecha de inscripción RM | 27/08/2024 |
| Domicilio social | Carrer Pere IV, 37, 1º 3ª, 08018 Barcelona |
| Capital social | 3.000 € (pendiente confirmación exacta escritura) |
| Administrador único | Elizaveta Ilina (NIE Z1455172J) |
| Actividades IAE actuales | 933.9 (otros actividades de enseñanza), 965.1 (espectáculos en salas y locales) |
| **CNAE a incorporar (en trámite con gestor)** | **4531 — Comercio de repuestos y accesorios de vehículos** (MOD 036 a presentar antes del 30/04/2026) |

### 2.2 Estructura societaria y gobierno

SignalWaves SLU es una sociedad limitada unipersonal constituida en agosto de 2024. El fundador y promotor del proyecto Forged Wheels, **Andrei Potcenkovskii**, ostenta la condición de socio único y promotor del nuevo plan de negocio. La figura de administrador única recae sobre **Elizaveta Ilina**, en calidad de apoderada y administradora fiduciaria, de acuerdo con la escritura de constitución.

Una vez aprobada la financiación de ENISA, se prevé formalizar en Junta General la incorporación de Andrei Potcenkovskii como **administrador mancomunado** junto con la actual administradora, reflejando la dedicación del fundador al proyecto y consolidando la estructura de gobierno. Esta modificación se tramitará ante notario y se inscribirá en el Registro Mercantil en el primer mes tras la resolución ENISA favorable.

La actividad declarada en IAE (933.9 y 965.1) responde a proyectos anteriores de la sociedad. La presentación del MOD 036 para incorporar la actividad 4531 (Comercio de repuestos y accesorios de vehículos) se encuentra en trámite con gestoría colegiada en Barcelona y se completará antes de la formalización del préstamo ENISA. Esta actualización no requiere disolución ni reforma estatutaria sustancial al encajar dentro del objeto social amplio.

### 2.3 Fundador — Andrei Potcenkovskii

**Perfil:** emprendedor con más de **25 años de trayectoria empresarial**, evolucionado desde la construcción residencial tradicional (20+ años como empresario autónomo en Rusia) hacia la fundación y operación de plataformas digitales basadas en inteligencia artificial. Licenciado en Economía por la Universidad de Petrozavodsk (Rusia, 1999) y Técnico Superior en Construcción de Maquinaria.

**Proyectos actuales y previos relevantes:**
- **SignalWaves Auto** (2024-presente, Barcelona) — importación y venta de vehículos premium de Alemania al mercado español, con garaje operativo propio.
- **PsychAuto** (psihavto.tilda.ws, 2024-presente) — test psicológico para selección de vehículo, operativo en tres idiomas (ruso, inglés, español). ~1.000 tests completados en fase piloto, audiencia principal UE.
- **Construcción residencial** (2000-2020, Rusia) — más de 20 años como empresario autónomo construyendo viviendas unifamiliares y realizando reformas integrales.

**Competencias aportadas a Forged Wheels:**
- Ingeniería full-stack aplicada (frontend, backend, integración APIs de IA).
- Conocimiento directo de modelos generativos de última generación (Gemini 3 Pro, Nano Banana Pro, Florence-2, BiRefNet).
- Experiencia práctica de gestión de proyectos con proveedores internacionales y control presupuestario (de obras residenciales a cadena de suministro Asia-EU).
- Residencia legal en España desde 2024 con autorización No Lucrativa; en trámite de modificación a autorización de Emprendedor (Ley 14/2013) tras resolución ENISA.
- Idiomas: ruso nativo, inglés B1, español A1 (en mejora activa).

**Dedicación:** 100 % al proyecto Forged Wheels.

### 2.4 Advisory Board (en formación)

Objetivo: incorporar tres asesores externos antes del cierre de la ronda de financiación ENISA.

- **Perfil 1 — Ingeniería automotriz / homologación:** ex-ingeniero de TÜV Rheinland o IDIADA, con experiencia en certificación de llantas de aleación para mercado EU.
- **Perfil 2 — E-commerce premium EU:** director de crecimiento o fundador de marca premium con facturación superior a 5 M€ anuales.
- **Perfil 3 — Supply chain Asia-EU:** consultor con red activa en fábricas forjadoras de Taiwán o China continental.

### 2.5 Plan de contratación 36 meses

| Trimestre | Rol | Dedicación | Coste bruto anual |
|---|---|---|---|
| Q3 2026 | Responsable de adquisición digital (Meta/Google Ads + SEO) | Freelance 20 h/sem | 18.000 € |
| Q4 2026 | Ingeniero mecánico / CAD review | Freelance 10 h/sem | 14.400 € |
| Q1 2027 | Customer success / postventa (ES/EN) | Jornada completa | 28.800 € + SS 30% |
| Q2 2027 | CTO / ampliación equipo IA | Jornada completa | 55.200 € + SS 30% |

---

## 3. Producto y servicio

### 3.1 Qué vende Forged Wheels

La plataforma comercializa **llantas forjadas de aluminio 6061-T6 o 6082, fabricadas por mecanizado CNC a partir de lingote**, en juegos de 4 unidades totalmente personalizados por cliente. No existe stock ni lote mínimo: cada pedido equivale a un único set fabricado bajo demanda a partir de un archivo CAD único.

### 3.2 Flujo del cliente (8 pasos)

1. El cliente sube una **foto de su coche** en la plataforma web (cualquier ángulo).
2. La IA **detecta las ruedas actuales** (modelo Florence-2), elimina fondo (BiRefNet) y prepara el lienzo.
3. El cliente **elige un diseño** del catálogo (21 modelos premium actualmente) o solicita uno **100% personalizado** mediante briefing asistido por IA.
4. El motor **Gemini 3 Pro Image** renderiza en menos de 60 segundos la llanta elegida sobre el coche real del cliente, a resolución fotorrealista y conservando iluminación, perspectiva y reflejos.
5. El cliente **itera** el diseño (color, acabado, tamaño, offset) tantas veces como desee; cada iteración se convierte en la nueva base.
6. Una vez conforme, **confirma el pedido** y la plataforma genera las especificaciones técnicas (PCD, ET, diámetro, anchura, alloy grade) activando la producción.
7. El fabricante asociado produce el juego en 15-25 días, incluyendo el **paquete documental EU** (certificado de material, informe de carga JWL/VIA, dimensional drawing, certificado de origen).
8. La llanta se entrega al cliente con la documentación necesaria para **homologación individual** (*Reforma de Importancia* en ITV española o *Einzelabnahme* en TÜV alemán).

### 3.3 Catálogo inicial

21 diseños de referencia listos en catálogo, cubriendo 5 categorías estilísticas (monoblock, concave, multi-piece, mesh, split-spoke), tamaños de 18″ a 22″, con pricing orientativo entre 380-1.280 € por llanta.

### 3.4 Aspectos técnicos y regulatorios clave

- **Alloy:** aluminio forjado 6061-T6 (Rm ≥ 310 MPa) o 6082 según exigencia estructural.
- **Certificación de fábrica:** solo proveedores con TÜV, JWL y VIA documentalmente verificados.
- **Homologación final:** a cargo del cliente con el paquete documental entregado; Forged Wheels ofrece servicio concertado con ingenieros homologadores colaboradores en España (coste añadido 450-700 €).
- **RC Producto:** póliza de Responsabilidad Civil de Producto de 1 M€ contratada desde el mes 1, con un coste anual de 3.000 €.

---

## 4. Carácter innovador

### 4.1 Innovación tecnológica

Forged Wheels es, a fecha de este plan, el **primer operador europeo** que integra en una sola experiencia de compra los siguientes elementos:

**(a) Visualización IA reference-based sobre foto real del cliente.** La inmensa mayoría de competidores (HRE, Vossen, ADV.1, Rotiform, Forgiato) ofrece únicamente **renders 3D pre-generados** sobre coches genéricos. Forged Wheels emplea **Gemini 3 Pro Image** (Google DeepMind, 2025), ejecutado vía la API fal.ai, que toma una fotografía cualquiera del coche del cliente y sustituye las ruedas por el diseño elegido **conservando perspectiva, iluminación y reflejos** a nivel fotorrealista.

**(b) Pipeline multi-modelo en cascada.** La plataforma orquesta una cadena de cuatro modelos especializados:

1. **Florence-2** (Microsoft) — detección y bounding box de ruedas en la foto del cliente.
2. **BiRefNet** (fal.ai) — eliminación de fondo con precisión subpíxel en los bordes.
3. **Gemini 3 Pro Image** — sustitución reference-based de la rueda.
4. **Flux Schnell + rembg** — generación del catálogo de referencia.

Este pipeline multi-modelo, hasta donde la investigación de competidores ha podido verificar, **no está replicado por ningún actor europeo** en la categoría de llantas forjadas aftermarket.

**(c) Modelo de negocio bespoke single-set.** Industrialmente, la forja de aluminio es un proceso **sin molde fijo**: cada llanta se mecaniza desde un lingote. Esto permite técnicamente producir **un juego único** sin coste de utillaje, algo que el mercado tradicional oculta imponiendo MOQs artificiales.

### 4.2 Innovación de modelo y experiencia

- Precio de entrada **4-6 veces inferior** a los competidores premium (1.500 € vs. 4.000-8.000 €) al eliminar intermediarios.
- Plazo de entrega **2-4 veces menor** (25-35 días vs. 8-16 semanas).
- Compra **100 % digital**, sin necesidad de visita física.
- **Documentación EU integrada** (Einzelabnahme / Reforma) en el precio, no como coste oculto.

### 4.3 Propiedad intelectual y barreras

- **Marca "Forged Wheels"** — solicitud OEPM (España) en trámite, prevista EUIPO (UE) Q3 2026.
- **Trade-secret protocol** — documento interno firmado y depositado notarialmente en M1 tras resolución ENISA, describiendo el pipeline multi-modelo y los prompts propios.
- **Dataset propio** de renders diseño-sobre-vehículo, que crece con cada cliente y se convierte en un activo de entrenamiento exclusivo.
- **Red de proveedores** con relaciones directas y exclusividad selectiva en diseños propios.

---

## 5. Análisis de mercado

### 5.1 Tamaño y crecimiento

- **Mercado global llantas aftermarket:** 21.800 M$ en 2024, CAGR 6,8 % hasta 2030 (Grand View Research).
- **Segmento forjado premium EU:** estimado en 1.500-1.800 M€/año, CAGR 8 % (2023-2027).
- **España:** 4,2 % del mercado EU, con tendencia al alza por crecimiento de parque automovilístico premium (+11 % BMW/Mercedes/Audi/Porsche 2019-2024, DGT).

### 5.2 Segmentación

- **Segmento primario "Premium customizer":** hombres 30-50, propietarios de BMW Serie 3/5/X, Mercedes C/E, Audi A4/A5/Q5, Porsche 911/Cayenne, renta familiar bruta > 60.000 €/año, usuarios activos de Instagram y YouTube en nichos de automoción.
- **Segmento secundario "Track day enthusiast":** propietarios de M/AMG/RS/S con 4-8 track days/año.
- **Segmento terciario "Lead to dealer":** clientes que usan la plataforma para visualizar y compran finalmente en concesionario partner (línea de lead-gen).

### 5.3 Geografía

| País | Fase | Cuándo | Razón |
|---|---|---|---|
| 🇪🇸 España | Fase 1 | Junio 2026 | Sede, marco legal claro (ITV Reforma) |
| 🇩🇪 Alemania | Fase 2 | Q4 2026 | Mercado mayor, Einzelabnahme estandarizado |
| 🇮🇹 Italia | Fase 3 | Q2 2027 | Alta afinidad premium |
| 🇫🇷 Francia | Fase 4 | Q4 2027 | DREAL complejo, apertura cauta |

---

## 6. Análisis de competencia

| Competidor | Origen | Precio juego | Plazo | IA try-on | Bespoke real | Web EU |
|---|---|---|---|---|---|---|
| HRE Performance Wheels | EE.UU. | 6.000-8.000 € | 12-16 sem | ❌ | Parcial | Solo distribuidores |
| Vossen | EE.UU. | 4.000-6.500 € | 8-12 sem | ❌ | Catálogo | Sí (US) |
| ADV.1 | EE.UU. | 5.500-8.000 € | 10-14 sem | ❌ | Parcial | No |
| BC Forged | Taiwán | 3.500-5.500 € | 8-12 sem | ❌ | Sí | Distribuidores |
| Rotiform | EE.UU. | 2.200-3.500 € | 6-10 sem | ❌ | No (cast/flow) | Sí |
| Forgiato | EE.UU. | 6.000-15.000 € | 10-14 sem | ❌ | Sí | Solo dealers |
| **Forged Wheels** | 🇪🇸 **España** | **1.500-3.000 €** | **3-5 sem** | **✅ Gemini 3** | **✅** | **✅ Propia** |

**Ventajas competitivas sostenibles:**

1. **Foso tecnológico** — ningún competidor tiene IA try-on fotorrealista.
2. **Foso de coste** — ningún competidor vende directo sin capa de distribuidor.
3. **Foso regulatorio local** — ninguno integra documentación Reforma de Importancia española.

---

## 7. Modelo de negocio y unit economics

### 7.1 Líneas de ingreso

**Línea 1 — B2C venta directa (95 % Y1, 87 % Y3):**

- Precio medio venta (PMV): 1.800 € (Y1) → 2.200 € (Y3).
- COGS unitario: 950 € (Y1) → 1.050 € (Y3).
- Margen bruto por juego: 785 € (Y1) → 1.085 € (Y3).
- Margen bruto porcentual: **43,6 %** (Y1) → 46,6 % (Y2) → **49,8 %** (Y3).

**Línea 2 — Generación de leads B2B (0 %, 0,2 %, 0,2 %):**

- Comisión por lead cualificado a concesionarios partner: 200 €/lead.
- Activación en Q4 2026 tras acuerdo con primer partner oficial.
- Escala natural en Y3 a 800 €/mes de flujo adicional.

**Línea 3 — SaaS white-label (0 %, 2,1 %, 2,0 %):**

- Licencia del motor IA a marcas tradicionales sin capacidad técnica propia.
- Fee fijo 3.000 €/mes por cliente.
- Objetivo: 1 cliente Y2, 3 clientes Y3 (pipeline actual: dos conversaciones iniciadas).

### 7.2 Coste medio por juego vendido (Año 1)

| Concepto | Euros | % ingreso |
|---|---|---|
| COGS llanta (4 piezas FOB → DAP España) | 950 | 52,8 % |
| Comisión Stripe (1,4 %) | 25 | 1,4 % |
| CAC blended | 180 | 10,0 % |
| Packaging + atención cliente | 40 | 2,2 % |
| **Margen de contribución unitario** | **605** | **33,6 %** |

### 7.3 Unit economics, LTV y payback

**Cálculo LTV:**

- Gross profit por juego Y1: 785 € (margen bruto 43,6 %).
- Programa referidos: 200 € descuento al referente → margen efectivo 585 €.
- Repeat rate a 3 años: 8 % (llanta forjada es compra de bajo uso).
- Cross-sell accesorios (tuercas, separadores homologados, kits montaje, 15 % de clientes × 150 € margen): 22,5 €/cliente.
- **LTV estimado: 635-680 €** por cliente.

**Ratios unit economics:**

| Ratio | Año 1 | Año 3 | Benchmark saludable |
|---|---|---|---|
| LTV | 635 € | 820 € | — |
| CAC blended | 180 € | 120 € | — |
| **LTV / CAC** | **3,5x** | **6,8x** | > 3x |
| Payback CAC (meses) | 5,2 | 2,4 | < 12 |

Los ratios LTV/CAC de 3,5x (Y1) y 6,8x (Y3) superan holgadamente el benchmark de 3x que se utiliza en la práctica como umbral de viabilidad en e-commerce premium. El payback de CAC a 5 meses en Y1 confirma un crecimiento auto-financiable desde la segunda mitad del primer año.

### 7.4 Break-even

- EBITDA mensual positivo: **mes 7** (diciembre 2026), +378 €.
- EBITDA acumulado en equilibrio: **mes 13** (junio 2027).
- Caja mínima del proyecto (mes 3): 45.885 €, cómoda distancia del límite operativo.

---

## 8. Plan comercial y marketing

### 8.1 Adquisición

- **Canal 1 — Meta Ads (Instagram/Facebook):** CAC objetivo 180 € → 120 € con optimización.
- **Canal 2 — Google Ads (keywords intención alta):** "llantas forjadas 19″", "custom wheels bmw", "bbs forged alternative".
- **Canal 3 — SEO + contenidos:** 20 artículos long-form (3.000 palabras) en Y1, objetivo 10.000 visitas orgánicas/mes en M12.
- **Canal 4 — Influencers YouTube automotive:** 5 colaboraciones con canales de 50-200 k subs (ES + DE).
- **Canal 5 — Viralidad producto:** cada visualización IA gratuita es compartida en redes; dataset de 500-1.000 imágenes virales/mes previsto con watermark discreto.

### 8.2 Retención y expansión

- Programa "Design Archive": diseños salvados siguen disponibles para repetición.
- Cross-sell: tuercas, separadores homologados, kits montaje (margen 60 %).
- Programa referidos: 200 € descuento al referente + 200 € al nuevo.

### 8.3 Hitos comerciales

| Mes | Hito |
|---|---|
| M0 (Jun 2026) | Lanzamiento oficial + primeros 10 clientes ES |
| M3 | 50 clientes acumulados, break-even contribución unitario |
| M6 | Expansión DE, primer partner dealer ES |
| M9 | EBITDA mensual positivo consolidado |
| M12 | 120 clientes acumulados, lanzamiento SaaS piloto |

---

## 9. Operaciones y cadena de suministro

### 9.1 Proveedores

- **Socio A — Wuxi Susha Auto Parts (Jiangsu, China).** Certificaciones JWL/VIA/SAE-J2530 verificadas, exportación comprobada a DE/UK/IT/AT. MOQ 4 piezas = 1 juego. Lead time 20-25 días. RFQ enviada el 21 de abril de 2026.
- **Socio B — Kipardo Racing (Guangzhou, China).** Único proveedor con MOQ 1 pieza explícita. Lead time 10-15 días monoblock.
- **Socio C — League Alloy (Taichung, Taiwán).** Certificación completa TÜV + VIA + IATF 16949 + ISO 9001. Reservado para línea "Forged Wheels Premium" Q2 2027.

### 9.2 Logística

- Ruta estándar: FOB puerto chino → consolidación contenedor → DAP Barcelona directo al cliente.
- Ruta express: aérea DHL/FedEx para pedidos premium (coste +180 €/juego).
- Socios en tránsito: negociación activa con Delta Freight y Corea Logistics en Barcelona.

### 9.3 Homologación y calidad

- Recepción: inspección dimensional y visual de cada set en almacén Barcelona propio (Q3 2026) o fulfillment partner.
- Pack documental: revisión de certificados TÜV/JWL antes del envío al cliente.
- Postventa: ingeniero homologador freelance para resolución de incidencias ITV.

### 9.4 Infraestructura técnica

- **Frontend:** HTML/CSS/JS vanilla desplegado en Vercel (CDN global, auto-scale).
- **Backend:** Python serverless functions (inpainting, bg removal, wheel detection).
- **APIs IA:** fal.ai (Gemini 3, BiRefNet, Florence-2) — coste variable ~0,25 €/render.
- **Pagos:** Stripe (live Q3 2026) + Alibaba Trade Assurance para operaciones con proveedor.
- **Analítica:** Plausible (privacy-first, cumple RGPD sin cookies).

---

## 10. Plan financiero

### 10.1 Cuenta de resultados consolidada (3 años)

*Todas las cifras sincronizadas con el modelo Excel v2.*

| Concepto (€) | Año 1 | Año 2 | Año 3 |
|---|---|---|---|
| Ingresos B2C | 216.000 | 1.700.000 | 5.280.000 |
| Ingresos Lead-gen | 0 | 3.600 | 9.600 |
| Ingresos SaaS | 0 | 36.000 | 108.000 |
| **Ingresos totales** | **216.000** | **1.739.600** | **5.397.600** |
| COGS totales (producto + Stripe + pack) | 121.823 | 908.352 | 2.691.566 |
| **Margen bruto** | **94.177** | **831.248** | **2.706.034** |
| % Margen bruto | 43,6% | 47,8% | 50,1% |
| Marketing (CAC × uds) | 21.600 | 127.500 | 288.000 |
| Costes fijos + SS empresa | 75.090 | 171.120 | 207.000 |
| Inversión inicial (M1-M3) | 36.700 | 0 | 0 |
| **EBITDA** | **−39.213** | **+532.628** | **+2.211.034** |
| Amortización activos (5 años) | 3.978 | 5.304 | 5.304 |
| **EBIT** | **−43.191** | **+527.324** | **+2.205.730** |
| Intereses ENISA (TIN 4,75 %) | 3.564 | 3.564 | 14.388 |
| **Resultado antes impuestos** | **−46.755** | **+523.760** | **+2.191.342** |
| Impuesto Sociedades (15 % / 25 %) | 0 | 78.564 | 547.836 |
| **Beneficio neto** | **−46.755** | **+445.196** | **+1.643.506** |
| % Margen neto | −21,6 % | 25,6 % | 30,5 % |

### 10.2 Flujo de caja y tesorería

| Concepto (€) | Año 1 | Año 2 | Año 3 |
|---|---|---|---|
| Caja inicial | 8.000 | 51.861 | 460.938 |
| (+) Desembolso ENISA | 75.000 | 0 | 0 |
| (+) Cash in operativo | 216.000 | 1.739.600 | 5.397.600 |
| (−) Cash out operativo | −243.575 | −1.252.359 | −3.227.510 |
| (−) Impuesto Sociedades | 0 | −78.564 | −547.836 |
| (−) IVA neto liquidado | 0 | 0 | 0 |
| (−) Cuota ENISA | −3.564 | 0 (carencia) | −13.176 |
| **Caja al final del año** | **51.861** | **460.938** | **1.784.181** |

La caja mínima a lo largo del Año 1 se registra en M3 (45.885 €), con holgura suficiente frente a la inversión inicial. Tras el mes 13 la generación de caja se acelera hasta alcanzar 1,78 M€ al cierre del Año 3 sin necesidad de financiación adicional.

*Nota técnica sobre la cuota ENISA durante Y1 y Y2:* durante el período de carencia de capital de 24 meses (meses 1-24) se abonan exclusivamente intereses al tipo fijo del 4,75 % TIN, por lo que la cuota mensual efectiva es de 297 €/mes (total Y1 y Y2: 3.564 € cada ejercicio). La amortización de capital comienza en el mes 25, con cuota mensual constante de 1.199 € (fórmula francesa sobre 72 meses restantes). Este esquema de carencia extendida, propio de la Línea Emprendedores de ENISA, libera presión de tesorería en los dos años críticos de lanzamiento comercial.

### 10.3 Uso detallado de los 75.000 € de ENISA

| Partida | Importe (€) | % | Mes | Justificación |
|---|---|---|---|---|
| Homologación TÜV (3 SKUs propios) | 12.000 | 16 % | M2-M4 | Road legality EU del catálogo propio |
| Desarrollo producto (checkout, CRM, cuenta cliente) | 8.000 | 11 % | M1-M3 | Completar MVP comercial |
| Samples pre-producción (5 juegos de muestra) | 6.500 | 9 % | M1-M2 | Control de calidad pre-comercial |
| Marca OEPM + EUIPO | 1.200 | 2 % | M1 | Protección en 27 países |
| Marketing de lanzamiento (M1-M3) | 9.000 | 12 % | M1-M3 | Campaña primeros 90 días |
| Salario fundador M4-M15 (20k / 12 meses, parcial) | 20.000 | 27 % | M4-M15 | Dedicación 100 % pre-break-even |
| Ingeniero CAD freelance | 10.000 | 13 % | M4-M15 | Review técnico de cada pedido |
| Herramientas + infraestructura 18 meses | 6.300 | 8 % | Mensual | Vercel + fal.ai + Stripe + gestor |
| RC Producto + seguros iniciales | 2.000 | 3 % | M1 | Cobertura responsabilidad civil de producto |
| **TOTAL** | **75.000** | **100 %** | | |

Se complementa con **8.000 € de aporte propio** del fundador (ya desembolsados), reservados como contingencia operativa y fondo de maniobra adicional durante Y1.

### 10.4 Condiciones de la financiación ENISA

| Condición | Valor |
|---|---|
| Importe solicitado | 75.000 € |
| Línea | **Emprendedores** (sin límite de edad) |
| TIN fijo | 4,75 % |
| Tipo variable complementario | según EBITDA (Euribor + spread) |
| **Carencia de capital** | **24 meses** (Años 1 y 2 solo intereses) |
| Plazo total | 96 meses (8 años) |
| Cuota mensual post-carencia | 1.199 €/mes (fórmula francesa sobre 72 meses) |
| Cuota durante carencia | 297 €/mes (solo interés fijo) |
| Comisión de apertura | 0,5 % sobre dispuesto |

### 10.5 Impuestos contemplados en el modelo

- **Impuesto sobre Sociedades:** 15 % los dos primeros ejercicios con bases imponibles positivas (Ley 27/2014, art. 29.1 para entidades de nueva creación), 25 % desde el Y3.
- **IVA:** régimen general 21 % repercutido sobre ventas B2C y soportado sobre compras intracomunitarias (importación China con IVA pagado en aduana y deducible). Liquidación trimestral (modelo 303) con compensación de saldos.
- **Seguridad Social empresa:** ×1,30 aplicado sobre los salarios brutos del personal contratado en Customer Success (M13+) y CTO (M19+).
- **Cuota de autónomos del fundador:** 320 €/mes desde M4.

---

## 11. Análisis de sensibilidad

| Escenario | Ingresos Y1 | Ingresos Y3 | EBITDA Y1 | EBITDA Y3 | Break-even EBITDA+ | Caja mínima |
|---|---|---|---|---|---|---|
| **Pesimista** (−25 % ventas, +30 % CAC, +15 días retraso) | 162.000 € | 4.048.200 € | −62.217 € | +1.541.726 € | M13 | 17.219 € |
| **Base** (modelo actual) | 216.000 € | 5.397.600 € | −39.213 € | +2.211.034 € | M8 | 32.865 € |
| **Optimista** (+20 % ventas, −10 % CAC, EU warehouse) | 259.200 € | 6.477.120 € | −10.411 € | +2.987.591 € | M6 | 39.938 € |

**Conclusiones:**

- El escenario **Base** es viable con los 75.000 € de ENISA + 8.000 € del fundador sin necesidad de financiación adicional.
- El escenario **Pesimista** mantiene caja positiva pero con holgura estrecha; se prevé mantener una línea ICO de 25.000 € como backup no dispuesto.
- El escenario **Optimista** adelanta el break-even a M6 y permite acelerar la apertura en Alemania.
- Variable más sensible: **CAC**. Un +30 % destruye ~42 k€ de EBITDA Y1. Mitigación: viralidad IA y programa de referidos.
- Segunda más sensible: **retraso de proveedor**. 15 días = 1 mes de ingresos perdidos = ~18 k€ Y1. Mitigación: doble proveedor contratado en paralelo.

---

## 12. Riesgos y mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Retraso de proveedor en primer pedido | Alta | Alto | Dos proveedores en paralelo (Socio A + B); Alibaba Trade Assurance como seguro |
| Fallo estructural de llanta en cliente final | Baja | Crítico | Solo proveedores con TÜV/JWL verificados; RC Producto 1 M€ desde M1 |
| Cambio regulatorio EU (homologación más estricta) | Media | Medio | Vínculo directo con ingeniero homologador; capacidad de pivotar a catálogo pre-homologado |
| Aumento de coste o restricción de acceso a Gemini 3 API | Media | Alto | Pipeline abstraído; alternativas Nano Banana Pro y FLUX.2 ya testeadas |
| Entrada de competidor grande con IA similar | Media (18 meses) | Alto | Ventaja de primer movimiento, marca registrada, dataset propio, exclusividad con 1-2 fábricas |
| CAC sube por competencia en Meta Ads | Alta | Medio | Diversificación canales (SEO, YouTube, referidos) |
| Tesorería por crecimiento más rápido de lo previsto | Media | Medio | Cobro 100 % al pedido; línea descuento Stripe disponible desde M6 |
| Incumplimiento del proveedor en pack documental | Media | Alto | Clausulado específico; retención 20 % del pago final hasta recepción de docs |
| Demora de la inscripción CNAE 4531 en AEAT | Baja | Bajo | Trámite iniciado con gestor colegiado antes de la formalización ENISA |
| Cambio en la fiscalidad de empresas de nueva creación (Ley 27/2014) | Baja | Medio | Seguimiento trimestral con asesor fiscal; provisión adicional de 8 k€ en Y2 ante endurecimiento |

---

## 13. Anexos

Se entregarán como documentos adjuntos a este plan:

- **Anexo A** — Escritura de constitución SignalWaves SLU + CIF + ВНЖ (permiso de residencia) del fundador
- **Anexo B** — Currículum del fundador (versión extendida, español)
- **Anexo C** — Capturas de pantalla de la plataforma en funcionamiento
- **Anexo D** — Informe de investigación sobre proveedores (13 fabricantes analizados)
- **Anexo E** — Muestra de renders IA sobre vehículos reales (6 ejemplos)
- **Anexo F** — Modelo financiero detallado Excel v2 (3 años, mensualizado, con IS/IVA/SS)
- **Anexo G** — Certificaciones de proveedores (TÜV/JWL pendientes de recepción)
- **Anexo H** — Cartas de interés de dealers partners (en formación)
- **Anexo I** — Solicitud de Marca OEPM

---

**Documento preparado por:** Andrei Potcenkovskii, Fundador
**Fecha:** 19 de abril de 2026
**Versión:** 2.0 — sincronizada con modelo financiero v2 tras review del evaluador Miguel Alonso Serra

Contacto:
📧 pozenkov13@gmail.com
📱 +34 628 106 939 (WhatsApp)
🌐 forged-wheels-showroom.vercel.app
