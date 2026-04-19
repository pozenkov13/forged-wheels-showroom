# ANEXOS TÉCNICOS — PROTOCOLO DE DEPÓSITO DE SECRETO EMPRESARIAL

**Protocolo:** PW-TS-2026-001
**Titular:** SIGNALWAVES, S.L.U. — CIF B19996313
**Promotor:** D. Andrei Potcenkovskii
**Fecha:** 19 de abril de 2026

**Documento confidencial.** Este conjunto de Anexos forma parte integrante del Protocolo de Depósito de Secreto Empresarial y se presenta ante fedatario público en sobre cerrado y lacrado, conforme a la Ley 1/2019, de 20 de febrero, de Secretos Empresariales.

---

## ANEXO A — Diagrama y especificación del Pipeline multi-modelo

### A.1 Arquitectura general

El Sistema Propietario de Visualización Forged Wheels opera mediante la siguiente secuencia de cuatro etapas, orquestadas por un *backend* serverless en Python desplegado en la infraestructura Vercel.

```
┌─────────────────────────────────────────────────────────────────────┐
│                   ENTRADA: Foto del vehículo del cliente            │
│                   (JPEG/PNG, cualquier ángulo, hasta 10 MB)         │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  ETAPA 1  │  FLORENCE-2 (Microsoft, via fal.ai)                     │
│           │  ─ Detección de ruedas                                  │
│           │  ─ Salida: bounding boxes (x1, y1, x2, y2) × N          │
│           │  ─ Confidence threshold propietario: 0.42               │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  ETAPA 2  │  BiRefNet (fal.ai)                                      │
│           │  ─ Eliminación de fondo subpíxel                        │
│           │  ─ Sólo si el cliente sube su propia llanta custom      │
│           │  ─ Salida: PNG transparente 1200×1200                   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  ETAPA 3  │  GEMINI 3 PRO IMAGE (Google DeepMind, via fal.ai)       │
│           │  ─ Sustitución reference-based                           │
│           │  ─ Input: foto coche + foto llanta referencia           │
│           │  ─ Prompt propietario (Anexo B)                         │
│           │  ─ Conservación de iluminación, perspectiva, reflejos   │
│           │  ─ Salida: imagen final fotorrealista                   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  ETAPA 4  │  FLUX SCHNELL + REMBG (uso interno, generación catálogo)│
│           │  ─ Creación de renders de referencia del catálogo       │
│           │  ─ No se ejecuta en el flujo del cliente final          │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   SALIDA: Imagen final al cliente                   │
│                   (data URL PNG, watermark "FW" sutil)              │
└─────────────────────────────────────────────────────────────────────┘
```

### A.2 Parámetros de transferencia entre etapas

- **Etapa 1 → 3:** los bounding boxes obtenidos se envían a Gemini como región de interés para focar la sustitución.
- **Etapa 2 → 3:** el PNG con fondo eliminado se sube a *fal.ai storage* y su URL se pasa como segunda imagen de referencia a Gemini.
- **Fallback interno:** si Florence-2 devuelve confianza < 0.42 se activa un segundo intento con parámetros relajados; tras un segundo fallo, se pide al cliente una foto adicional.

### A.3 Latencia y coste unitario

| Etapa | Latencia media | Coste / render |
|---|---|---|
| Florence-2 | 2-4 s | 0,008 € |
| BiRefNet | 3-6 s | 0,015 € |
| Gemini 3 Pro Image | 25-55 s | 0,20 € |
| **Total por sesión** | **30-65 s** | **~0,22 €** |

Información comercial confidencial — no divulgar.

---

## ANEXO B — Biblioteca de prompts propietarios v1.0

A continuación se recogen los prompts de instrucción utilizados por el Sistema en cada etapa. Son el resultado de cientos de iteraciones empíricas y constituyen una parte sustancial del secreto empresarial.

### B.1 Prompt de detección (Florence-2)

```
<OD>
```

Configuración del modelo: task prompt estándar de *object detection* de Florence-2, filtrado *post-hoc* por las siguientes clases candidatas: "wheel", "tire", "rim", "alloy wheel", "car wheel". Se conservan las detecciones con confidence ≥ 0.42 (umbral propietario determinado empíricamente sobre un conjunto de 200 imágenes de prueba).

### B.2 Prompt principal de sustitución (Gemini 3 Pro Image)

*Prompt V1.0 — producción actual:*

```
Take the car from image 1. Change both of its wheels to look exactly like
the wheel rim shown in image 2. Keep the car body, paint, lighting, shadows,
environment and camera perspective IDENTICAL to image 1. The new wheels must:
- exactly match the spoke design, finish and color of image 2
- fit naturally into the existing wheel wells of the car from image 1
- preserve realistic perspective distortion and specular highlights
- NOT alter any other part of the car (bumper, body lines, ground plane)
Output: the original car from image 1 with only the wheels replaced.
```

### B.3 Prompt de generación de catálogo (Flux Schnell)

*Usado internamente para generar imágenes de referencia del catálogo de 21 modelos actuales:*

```
Studio product photography of a premium forged aluminum automotive wheel,
[MODELO]-spoke [CATEGORÍA] design, [ACABADO] finish, [TAMAÑO] inch size,
deep lip, chrome center cap.
Lighting: dramatic rim light upper right, soft fill left, depth and texture.
Background: pure black seamless.
Composition: 3/4 front view, wheel slightly tilted toward camera.
Style: high-end automotive commercial, BMW Individual aesthetic.
Technical: shot on Phase One, 85mm macro, f/8, ISO 100.
Quality: 8k, photorealistic, ultra-detailed, sharp focus.
--ar 1:1 --v 6 --style raw --q 2
```

Variables `[MODELO]`, `[CATEGORÍA]`, `[ACABADO]`, `[TAMAÑO]` se inyectan dinámicamente desde el esquema de catálogo (Anexo E).

### B.4 Prompts de asistencia en briefing de diseño custom (no públicos)

Se mantienen en el *codebase* privado un conjunto de 14 prompts de asistencia conversacional para ayudar al cliente a describir su diseño ideal. Son propiedad exclusiva del titular. Se entregan listados nominalmente al fedatario, con el texto completo reservado.

---

## ANEXO C — Lógica de orquestación (código fuente)

Se acompañan impresos los archivos fuente del *backend* serverless que implementa la orquestación:

### C.1 `api/inpaint.py` (307 líneas)

Archivo central de orquestación. Responsabilidades:

- Recepción del pedido del cliente (imagen coche + imagen/ID de llanta).
- Invocación secuencial de los modelos de IA (Florence-2 → Gemini 3 Pro).
- Gestión de *fallbacks*, reintentos y validaciones de calidad intermedia.
- Inserción del *watermark* sutil "FW" de trazabilidad.
- Almacenamiento del resultado en el *dataset* interno (Anexo D).

Ruta del archivo: `/api/inpaint.py` del repositorio privado `forged-wheels-showroom`.

### C.2 `api/remove_bg.py` (132 líneas)

Módulo auxiliar para la eliminación de fondo (Etapa 2 del Pipeline). Se invoca únicamente cuando el cliente sube una llanta custom en lugar de elegir una del catálogo.

Ruta del archivo: `/api/remove_bg.py` del repositorio privado.

### C.3 Secciones relevantes de `index.html`

El archivo principal del frontend contiene en sus *scripts* embebidos la lógica de orquestación del lado cliente (gestión de estado, iteraciones de diseño, llamadas a las APIs internas, *drag & drop* de llantas). Se identifican las siguientes funciones confidenciales:

- `loadCatalog()` — carga dinámica del catálogo propietario.
- `runAIDetection()` — orquestación cliente de la detección.
- `runInpaint()` — disparador de la sustitución reference-based.
- `submitWaitlist()` — captación de leads *early-access*.

Ruta del archivo: `/index.html` del repositorio privado.

*Se entrega al fedatario una impresión completa de los tres archivos anteriores, con sus hashes SHA-256 para acreditar integridad del depósito:*

- `inpaint.py`:     [HASH_A_CALCULAR_EN_DÍA_DEPÓSITO]
- `remove_bg.py`:   [HASH_A_CALCULAR_EN_DÍA_DEPÓSITO]
- `index.html`:     [HASH_A_CALCULAR_EN_DÍA_DEPÓSITO]

---

## ANEXO D — Dataset interno de referencia

### D.1 Naturaleza del dataset

El dataset interno comprende tres conjuntos de imágenes, todos almacenados en repositorio privado con acceso restringido al promotor del titular:

- **Dataset 1 — Catálogo de referencia:** 21 diseños de llantas forjadas procesados en resolución 1200×1200 PNG con fondo transparente, etiquetados con metadatos del esquema propietario (Anexo E).
- **Dataset 2 — Renders del cliente:** imágenes renderizadas por el Sistema sobre fotos reales de vehículos de clientes. Cada imagen se almacena con los metadatos: marca/modelo del coche, diseño seleccionado, timestamp, hash del ID de cliente. A fecha del presente protocolo: **42 imágenes** generadas durante la fase de pruebas internas.
- **Dataset 3 — Pruebas de modelo:** conjunto de 200 imágenes de referencia (coches de diversas marcas, ángulos, iluminaciones) utilizado para el ajuste empírico de los umbrales de confianza de Florence-2.

### D.2 Proyección de crecimiento

- Año 1 (Jun 2026 – May 2027): estimado 1.200-2.400 renders con consentimiento de uso.
- Año 2: estimado 8.500-12.000 renders.
- Año 3: estimado 24.000-36.000 renders.

El crecimiento del dataset alimenta un ciclo virtuoso: cada render añadido mejora la calidad del *fine-tuning* futuro del Sistema sobre modelos base abiertos, y actúa como barrera de entrada frente a competidores.

### D.3 Consentimiento y RGPD

Todas las imágenes del Dataset 2 se obtienen bajo los Términos y Condiciones de la plataforma, que incluyen la cesión explícita de uso para mejora del servicio. No se almacena dato personal identificable del cliente en las imágenes; sólo un hash del ID interno.

---

## ANEXO E — Esquema de catálogo propietario

### E.1 Estructura de datos

Cada diseño de llanta del catálogo se describe mediante el siguiente *schema* JSON, de diseño propio del titular:

```json
{
  "id": "wN",
  "name": "Nombre comercial del diseño",
  "category": "monoblock | concave | multi-piece | mesh | split-spoke",
  "finish": "descripción textual del acabado",
  "sizes": ["18", "19", "20", "21", "22"],
  "pcd": ["5x112", "5x114.3", "5x120", "5x130"],
  "et_range": "rango de offset en mm",
  "price_from": "precio desde (EUR)",
  "price_to": "precio hasta (EUR)",
  "image": "ruta a PNG transparente",
  "source": "URL del proveedor forjador de origen"
}
```

### E.2 Valor del esquema

La estructura anterior permite:

- **Filtrado por compatibilidad vehicular** (PCD + diámetro + ET).
- **Cross-selling automático** (sugerencias por categoría + acabado).
- **Cálculo de precio dinámico** en función de tamaño × acabado × proveedor.
- **Integración directa con el proveedor forjador** mediante el campo `source`.

### E.3 Contenido actual

A fecha del presente protocolo, el catálogo contiene **21 diseños completamente caracterizados** con los metadatos anteriores. Se entrega al fedatario una impresión del archivo `wheels/catalog.json` (aproximadamente 414 líneas JSON).

---

## ANEXO F — Procedimiento operativo de fabricación bajo demanda

### F.1 Flujo comercial de pedido

```
1. Cliente confirma diseño en plataforma forged-wheels-showroom.vercel.app
                        │
                        ▼
2. Sistema genera automáticamente:
   ─ Especificación técnica (PCD, ET, diámetro, anchura, alloy grade)
   ─ Archivo STEP/IGES del diseño (si custom)
   ─ Render final de referencia (imagen PNG 1200×1200)
   ─ Orden de compra interna (PDF)
                        │
                        ▼
3. Pago del cliente procesado vía Stripe
   (cobro 100% al pedido, sin fiado)
                        │
                        ▼
4. Backend envía al proveedor forjador asociado:
   ─ Ficha técnica completa
   ─ Archivo STEP/IGES
   ─ Plazo acordado (15-25 días)
   ─ Requisitos de pack documental EU
                        │
                        ▼
5. Fabricación CNC desde lingote aluminio 6061-T6 / 6082
                        │
                        ▼
6. Control de calidad en fábrica + emisión del pack documental:
   ─ Material certificate
   ─ Load test report JWL/VIA
   ─ Dimensional drawing
   ─ Certificate of origin
                        │
                        ▼
7. Envío DAP Barcelona → cliente final
                        │
                        ▼
8. Cliente homologa en TÜV (DE) o ITV Reforma (ES)
   con el pack documental entregado.
```

### F.2 Proveedores asociados (identificados a la fecha del protocolo)

- **Socio primario:** Wuxi Susha Auto Parts (SSRacing, Jiangsu, China). Certificaciones JWL/VIA/SAE J2530/TÜV verificadas. MOQ 1 juego. RFQ enviada el 21/04/2026.
- **Socio secundario:** Kipardo Racing (Guangzhou, China). MOQ 1 pieza, lead time 10-15 días.
- **Socio premium (reserva 2027):** League Alloy (Taichung, Taiwán). IATF 16949 + TÜV + VIA + ISO 9001.

---

## ANEXO G — Modelo de cláusula de confidencialidad para terceros colaboradores

A continuación se reproduce el texto tipo incluido en todos los contratos de colaboración con *freelancers*, proveedores, asesores externos o socios técnicos que accedan a cualquier componente no público del Sistema.

---

### CLÁUSULA DE CONFIDENCIALIDAD Y PROTECCIÓN DE SECRETO EMPRESARIAL

**1. Objeto.** El Colaborador reconoce que, en el desempeño de los servicios contratados por SignalWaves, S.L.U. (en adelante, la "Sociedad"), podrá tener acceso a información confidencial relativa al Sistema Propietario de Visualización Forged Wheels (en adelante, el "Sistema"), que constituye **secreto empresarial** de la Sociedad al amparo de la Ley 1/2019, de 20 de febrero.

**2. Información confidencial.** A los efectos de la presente cláusula, se considera información confidencial cualquier dato, especificación técnica, código fuente, *prompt*, diagrama, imagen, metadato, listado de proveedores, *pricing*, o cualquier otro elemento relativo al Sistema al que el Colaborador pueda acceder por razón del contrato.

**3. Obligaciones del Colaborador.** El Colaborador se obliga a:

a) Mantener la más estricta confidencialidad sobre la información, no revelándola a terceros bajo ningún concepto.
b) Utilizar la información exclusivamente para la finalidad del contrato.
c) No reproducir, copiar, almacenar, transmitir ni utilizar la información fuera del ámbito del contrato.
d) Al término del contrato, devolver o destruir toda la información en su poder, a petición de la Sociedad.

**4. Duración.** La presente obligación subsistirá durante la vigencia del contrato y por un plazo de cinco (5) años tras su extinción.

**5. Penalización.** El incumplimiento de la presente cláusula facultará a la Sociedad a exigir: (i) la cesación inmediata de la conducta infractora, (ii) la indemnización de daños y perjuicios conforme al artículo 9 de la Ley 1/2019, que incluirá tanto el daño emergente como el lucro cesante, y (iii) la aplicación de las medidas de defensa previstas en el Título II de la citada ley.

**6. Jurisdicción.** Para cualquier controversia derivada de la presente cláusula, las partes se someten expresamente a los Juzgados y Tribunales de Barcelona, con renuncia a cualquier otro fuero que pudiera corresponderles.

---

## DILIGENCIA FINAL DE LOS ANEXOS

D. Andrei Potcenkovskii, como promotor del titular SIGNALWAVES, S.L.U., **rubrica** el presente conjunto de Anexos, que se adjuntan al Protocolo PW-TS-2026-001 en sobre cerrado y lacrado, para su depósito notarial conforme a los términos del Protocolo principal.

Fdo. ______________________________
**D. Andrei Potcenkovskii**
Barcelona, 19 de abril de 2026

---

*Documento elaborado conforme a la Ley 1/2019, de 20 de febrero, de Secretos Empresariales (BOE núm. 45, 21/02/2019).*
*Protocolo principal: PW-TS-2026-001.*
