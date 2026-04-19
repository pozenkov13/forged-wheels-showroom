# PROTOCOLO DE DEPÓSITO DE SECRETO EMPRESARIAL

**Protocolo núm.** PW-TS-2026-001
**Fecha:** 19 de abril de 2026
**Lugar:** Barcelona, España

Documento elaborado al amparo de la **Ley 1/2019, de 20 de febrero, de Secretos Empresariales**, que transpone al ordenamiento español la Directiva (UE) 2016/943.

---

## PARTE I — IDENTIFICACIÓN DEL TITULAR

**Razón social:** SIGNALWAVES, SOCIEDAD LIMITADA UNIPERSONAL
**CIF / NIF:** B19996313
**Domicilio social:** Carrer Pere IV, núm. 37, Planta 1, Puerta 3, 08018 Barcelona (España)
**Fecha de constitución:** 6 de agosto de 2024
**Inscripción Registro Mercantil:** 27 de agosto de 2024
**Administrador único:** Dña. Elizaveta Ilina, NIE Z1455172J

**Promotor y autor intelectual del secreto empresarial:**
D. Andrei Potcenkovskii
Correo electrónico: pozenkov13@gmail.com
Teléfono: +34 628 106 939

**Actividad económica objeto del secreto:** desarrollo de software basado en inteligencia artificial aplicada al sector de accesorios automovilísticos, específicamente a la visualización fotorrealista de llantas forjadas sobre vehículos de cliente final, bajo la marca comercial **"Forged Wheels"** (plataforma: forged-wheels-showroom.vercel.app).

---

## PARTE II — OBJETO DEL SECRETO EMPRESARIAL

El presente protocolo tiene por objeto el depósito y la constancia fehaciente de la existencia, en la fecha de este documento, del conjunto de conocimientos, información, procesos, prompts, configuraciones y flujos de trabajo técnicos desarrollados de forma original por el titular, y que conjuntamente conforman el **Sistema Propietario de Visualización Forged Wheels** (en adelante, "el Sistema").

El Sistema comprende, entre otros, los siguientes componentes confidenciales descritos con mayor detalle técnico en los Anexos:

1. **Pipeline multi-modelo en cascada (Anexo A):** arquitectura de orquestación en cuatro etapas sucesivas que combina los modelos Florence-2 (Microsoft), BiRefNet (fal.ai), Gemini 3 Pro Image (Google DeepMind) y Flux Schnell + rembg, ejecutados en una secuencia específica y con parámetros de transferencia de contexto propios.

2. **Biblioteca de prompts propietarios (Anexo B):** conjunto de plantillas de instrucción en lenguaje natural, optimizadas mediante iteración empírica, para la generación y sustitución de llantas en imágenes de vehículos conservando iluminación, perspectiva y reflejos fotorrealistas. Incluye prompts para el reconocimiento inicial (Florence-2), eliminación de fondo (BiRefNet), sustitución reference-based (Gemini 3 Pro) y generación de catálogo (Flux).

3. **Lógica de orquestación del sistema (Anexo C):** conjunto de reglas y algoritmos que determinan el encadenamiento, tolerancias, reintentos, validación de calidad intermedia y fallback entre los distintos modelos, así como el tratamiento del resultado final antes de su entrega al usuario.

4. **Dataset interno de referencia y entrenamiento (Anexo D):** repositorio en crecimiento continuo de imágenes renderizadas por el Sistema (llantas específicas sobre vehículos específicos de clientes), que constituye un activo de entrenamiento exclusivo no disponible públicamente y que mejora iterativamente la calidad de salida del Sistema.

5. **Taxonomía y esquema de catálogo propietario (Anexo E):** estructura de datos interna que relaciona cada diseño de llanta con metadatos técnicos (PCD, ET, alloy grade, tolerancias, coste de producción, especificaciones TÜV/JWL-VIA) y estéticos (categoría visual, finish, color, afinidad con gamas de vehículos), y que se emplea como motor de recomendación interna.

6. **Flujo comercial integrado con la fabricación bajo demanda (Anexo F):** procedimiento operativo que transforma un diseño aprobado por el cliente en una especificación técnica completa enviada al fabricante forjador asociado, incluyendo formato STEP/IGES, traducciones dimensionales y condiciones de packaging documental para homologación EU.

---

## PARTE III — CARÁCTER SECRETO

El titular declara y hace constar que el Sistema, en su conjunto y en sus componentes individuales descritos en la Parte II:

**(a)** No es, en su configuración global ni en las combinaciones precisas de sus componentes, **generalmente conocido** en los círculos en que normalmente se utilice el tipo de información o conocimientos en cuestión. Si bien los modelos de IA subyacentes (Florence-2, BiRefNet, Gemini 3, Flux) son accesibles públicamente mediante API, la **combinación específica**, los **parámetros de orquestación**, los **prompts**, el **dataset interno** y el **flujo comercial integrado** son de elaboración original y exclusiva del titular.

**(b)** No es **fácilmente accesible** para las personas pertenecientes a dichos círculos. La reproducción del Sistema requeriría meses de experimentación empírica, acceso a APIs de pago de terceros con configuraciones específicas, y el desarrollo de un dataset de entrenamiento equivalente, lo que constituye una barrera económica y temporal significativa.

**(c)** Posee un **valor empresarial**, ya sea real o potencial, precisamente por su carácter secreto, puesto que constituye la ventaja competitiva central del proyecto Forged Wheels frente a los competidores tradicionales del sector de llantas forjadas aftermarket (HRE, Vossen, ADV.1, BC Forged, Forgiato, Rotiform), ninguno de los cuales ofrece a la fecha del presente protocolo una funcionalidad equivalente de visualización reference-based sobre foto real del cliente.

**(d)** Ha sido objeto, por parte del titular, de **medidas razonables para mantenerlo en secreto**, en los términos detallados en la Parte V del presente protocolo.

---

## PARTE IV — VALOR EMPRESARIAL

El Sistema constituye el núcleo de la propuesta de valor comercial del titular en el mercado europeo de llantas forjadas personalizadas aftermarket. Su valor empresarial se manifiesta, entre otros, en los siguientes aspectos cuantificables y cualitativos:

- **Reducción de fricción comercial:** el Sistema elimina la incertidumbre estética del cliente final, identificada por el titular como la principal barrera de conversión en la categoría de llantas forjadas premium, donde los tiempos de espera habituales oscilan entre 8 y 16 semanas y los precios entre 4.000 y 8.000 € por juego.

- **Diferenciación competitiva sostenible:** ningún operador europeo, a fecha de este protocolo, ofrece una experiencia de visualización fotorrealista equivalente.

- **Activo generador de datos:** cada uso del Sistema añade una nueva imagen al dataset interno (Anexo D), incrementando progresivamente su valor de entrenamiento.

- **Barrera de entrada para terceros:** la complejidad de replicar la combinación exacta de modelos, prompts y lógica de orquestación constituye una barrera técnica no trivial.

- **Proyección financiera asociada:** el modelo de negocio respaldado por el Sistema prevé ingresos de 216.000 € (Año 1), 1.739.600 € (Año 2) y 5.397.600 € (Año 3), según el plan de empresa versión 2 de fecha 19 de abril de 2026.

---

## PARTE V — MEDIDAS RAZONABLES DE PROTECCIÓN

El titular declara haber adoptado, y mantener vigentes, las siguientes medidas razonables para preservar el carácter secreto del Sistema, en cumplimiento del artículo 1.1.c) de la Ley 1/2019:

### 5.1 Medidas técnicas

- Almacenamiento del código fuente, prompts, configuraciones y dataset en repositorios privados con autenticación de dos factores.
- Cifrado en tránsito (TLS 1.3) y en reposo de los assets críticos.
- Separación de entornos productivo, de staging y de desarrollo.
- Restricción de acceso de API keys (fal.ai, Google DeepMind) mediante variables de entorno no versionadas.
- Uso de watermark discreto en las imágenes generadas públicamente, con trazabilidad interna del render.

### 5.2 Medidas organizativas

- Restricción del acceso al Sistema al círculo mínimo imprescindible: actualmente, el promotor D. Andrei Potcenkovskii y el administrador en ejercicio.
- Cláusulas de confidencialidad incluidas contractualmente en cualquier colaboración con freelancers, asesores externos o proveedores que accedan a componentes no públicos del Sistema (cláusula tipo en Anexo G).
- Inclusión en los contratos con fabricantes forjadores asiáticos de cláusulas de no divulgación y prohibición expresa de replicación de diseños o datos técnicos comunicados por el titular.

### 5.3 Medidas jurídicas

- Solicitud de registro de la marca "Forged Wheels" ante la Oficina Española de Patentes y Marcas (OEPM), y previsión de extensión a la Oficina de Propiedad Intelectual de la Unión Europea (EUIPO) en el tercer trimestre de 2026.
- Depósito notarial del presente protocolo para fijar con efectos probatorios frente a terceros la **fecha cierta** del estado de desarrollo del Sistema.
- Compromiso de actualización y redepósito del presente protocolo con periodicidad anual, o con mayor frecuencia si se producen mejoras sustanciales del Sistema.

---

## PARTE VI — MANIFESTACIONES Y DECLARACIONES DEL TITULAR

El titular, representado por su promotor y autor intelectual D. Andrei Potcenkovskii, manifiesta bajo su responsabilidad:

**Primero.** Que el Sistema descrito es de elaboración original, desarrollado en el período comprendido entre junio de 2025 y abril de 2026, y que a la fecha del presente protocolo no ha sido divulgado públicamente ni cedido en uso a terceros.

**Segundo.** Que los componentes tecnológicos de terceros utilizados (modelos de IA accesibles vía API) se emplean bajo las licencias comerciales estándar de sus respectivos proveedores y no contravienen los términos de servicio de los mismos.

**Tercero.** Que las imágenes integrantes del dataset interno (Anexo D) han sido obtenidas con el consentimiento del usuario final de la plataforma, según los Términos y Condiciones publicados en forged-wheels-showroom.vercel.app, que incluyen la cesión explícita de uso de la imagen para mejora del servicio.

**Cuarto.** Que la información técnica detallada contenida en los Anexos A a G del presente protocolo es veraz, completa en lo que a la fecha actual del documento se refiere, y constituye por sí misma información de carácter reservado.

**Quinto.** Que el titular es consciente de que el presente depósito notarial no supone registro ni concesión de derechos exclusivos de propiedad industrial, sino únicamente la acreditación de fecha cierta frente a terceros del estado de conocimiento descrito, a efectos probatorios en eventuales procedimientos de defensa del secreto empresarial al amparo de la Ley 1/2019.

**Sexto.** Que autoriza al fedatario público interviniente a protocolizar el presente documento junto con sus Anexos en sobre cerrado, con indicación expresa del número de folios y de la fecha, quedando el contenido de los Anexos reservado salvo requerimiento judicial.

---

## PARTE VII — ANEXOS TÉCNICOS (en sobre cerrado)

Se acompañan al presente protocolo, en sobre cerrado y lacrado, los siguientes Anexos técnicos, cuyo contenido se declara como parte integrante del secreto empresarial:

- **Anexo A:** Diagrama y especificación del Pipeline multi-modelo (4 páginas).
- **Anexo B:** Biblioteca de prompts propietarios v1.0 (impresión directa, N páginas).
- **Anexo C:** Código fuente de la lógica de orquestación (impresión de los archivos `api/inpaint.py`, `api/remove_bg.py`, `index.html` en las partes relevantes).
- **Anexo D:** Descripción del dataset interno de referencia (metadatos, volumen, tipología).
- **Anexo E:** Esquema de catálogo propietario (archivo `wheels/catalog.json` impreso).
- **Anexo F:** Procedimiento operativo de fabricación bajo demanda (flujograma).
- **Anexo G:** Modelo de cláusula de confidencialidad para terceros colaboradores.

---

## PARTE VIII — DEPÓSITO Y FE PÚBLICA

El presente protocolo, en formato impreso y con la rúbrica en todas sus páginas de D. Andrei Potcenkovskii como promotor del titular, se entrega ante fedatario público para su **depósito y protocolización** al amparo de los artículos 216 y siguientes del Reglamento Notarial.

La finalidad exclusiva del presente depósito es la constancia fehaciente de la **fecha cierta** en que el titular declara tener elaborado y en su posesión el Sistema descrito, a efectos de cualquier eventual procedimiento judicial o administrativo en defensa del secreto empresarial.

El fedatario público no emite juicio sobre el contenido técnico, la originalidad, la protegibilidad o el valor comercial del Sistema, limitándose su intervención a la constatación de la identidad del compareciente, la fecha de la entrega y la integridad documental de los Anexos aportados.

---

**En Barcelona, a 19 de abril de 2026.**

**Por SIGNALWAVES, S.L.U.**

Fdo. ______________________________
**D. Andrei Potcenkovskii**
Promotor y autor intelectual del Sistema

(Firma en todas las páginas y al pie del presente protocolo)

---

**Diligencia notarial** *(a cumplimentar por el fedatario público):*

Doy fe de que en el día de la fecha, el compareciente D. Andrei Potcenkovskii, cuya identidad queda acreditada mediante [TIE / NIE / pasaporte], ha hecho entrega del presente documento de ____ folios, junto con sobre cerrado y lacrado conteniendo los Anexos A a G, procediéndose a su **protocolización** bajo el número de protocolo ________________ del corriente año.

Firma y sello del notario:

_______________________________________________

---

*Documento elaborado bajo la Ley 1/2019, de 20 de febrero, de Secretos Empresariales (BOE núm. 45, 21/02/2019).*
