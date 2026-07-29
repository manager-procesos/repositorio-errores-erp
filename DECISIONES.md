# Decisiones y reglas confirmadas — Repositorio de Errores ERP

Este documento es la **fuente única de verdad** de todas las decisiones y reglas acordadas con Olga sobre este proyecto (búsqueda de errores de Manager ERP, publicación en este repositorio, y creación de artículos en Intercom para Fin AI).

**Regla para cualquier sesión de Claude/Cowork que trabaje en este proyecto: lee este archivo primero. Si algo aquí contradice lo que crees recordar de un chat, este archivo tiene prioridad — está confirmado con evidencia, no con memoria.**

Última actualización: 24/07/2026.

---

## 1. Imágenes

- **Regla confirmada por Olga el 30/06/2026** (chat "Subida de articulos a Intercom"), re-confirmada y corregida en la tarea el 15/07/2026: cuando hay una imagen real disponible y contiene datos sensibles (RUT, nombre de cliente/empresa, base de datos, usuario, IP/servidor con nombre de cliente), **se conserva la imagen real** y se tapa **solo** la zona del dato sensible con un rectángulo del color de fondo + texto genérico de reemplazo. **Nunca se descarta la imagen completa por tener datos sensibles.**
- El placeholder genérico (mockup de "Manager ERP — Captura de Error") es **la excepción, no la regla**. Solo se usa cuando no hay ninguna imagen real disponible.
- **Limitación técnica confirmada el 23/07/2026**: no existe forma de descargar automáticamente los adjuntos de una conversación de Intercom. La herramienta `web_fetch` sólo puede bajar URLs que ya aparecieron en un mensaje del usuario o en un resultado previo de `web_fetch` ("provenance restriction") — las URLs firmadas de `intercom-attachments-*.com` que trae `get_conversation` no cumplen esa condición y la descarga falla. Por Slack sí se puede (`slack_read_file`); por Intercom, no, y no hay forma de evitarlo con las herramientas actuales.
- **Consecuencia práctica**: todo error cuya única fuente sea una conversación de Intercom (sin un mensaje de Slack con imagen adjunta) usará el placeholder genérico por diseño, no por error. Esto ya pasó en los errores #34 al #50. Si se quiere una imagen real para alguno de estos, la única forma es que Olga la descargue manualmente desde Intercom y la suba directamente en el chat.

## 2. Artículos en Intercom (pipeline `repositorio-errores-erp`)

- Se crean/actualizan con `state="published"` y **SIN asignar ninguna colección**. Esto los deja **invisibles en el Help Center** (no aparecen en menús ni búsqueda para clientes) pero **indexados por Fin AI** (`fin_state = 1`), que es el único objetivo: alimentar al chatbot, no publicar contenido público.
- **Nunca asignar colección** — eso lo maneja otro equipo (Olga confirmó el 30/06: "para eso existe otro equipo que está encargado de eso, nosotros solamente alimentamos la IA").
- Antes de crear un artículo nuevo, siempre `search_articles` para evitar duplicados (borrador o publicado).

## 3. Artículos en Intercom (pipeline distinto: `intercom-articulos-desde-conversaciones`)

- Esta es una tarea **separada e independiente** (corre 8:04 AM, lunes a viernes) que genera artículos desde conversaciones escaladas donde Fin AI no tuvo contenido (`content_sources.total_count == 0`), NO desde este repositorio de errores.
- Esos artículos se crean **siempre como `draft`** — nunca se publican automáticamente. Es un proceso distinto, no confundir con el de arriba.

## 4. No duplicar

- Errores nuevos: comparar título y síntoma contra TODOS los títulos en `datos.json` Y `respaldo_errores.json`, por similitud de contenido (no solo texto exacto). Si el síntoma/causa describe la misma falla con otras palabras, es duplicado.
- Artículos de Intercom: `search_articles` antes de crear. Ante la duda, no crear.

## 5. `datos.json` y el script local "subir-imagenes-erp.py" [CORREGIDO 24/07/2026]

- **Corrección importante:** este NO es un proceso externo ni ajeno a Claude/Cowork. Es un script local, `C:\erp-bot\subir-imagenes-erp.py`, guardado en la misma carpeta de trabajo que `datos.json` e `index.html`. Cualquier sesión de Cowork puede leerlo, editarlo o ejecutarlo — no hay un "otro equipo" administrándolo. La afirmación anterior en este documento ("proceso externo, no controlado por Claude/Cowork") era incorrecta y causó confusión real: Olga tuvo que aclarar explícitamente "soy yo y tú quienes hacemos todo".
- **Qué hacía y por qué rompía cosas:** el script lee `datos.json` e imágenes desde el DISCO LOCAL de `C:\erp-bot` (que puede estar desactualizado respecto a GitHub) y luego sobrescribe GitHub por completo (no fusiona). Como las correcciones de redacción/anonimización se pusheaban directo a GitHub sin nunca escribirse de vuelta al disco local, cada corrida de este script revertía silenciosamente esas correcciones. Esta es la causa raíz confirmada de las reversiones reportadas por Olga (imágenes con datos de cliente que volvían a aparecer sin tapar, etc.), no un proceso externo fuera de control.
- **Riesgo adicional encontrado:** la lista `PENDIENTES` dentro del script estaba indexada por `ficha_numero`, pero los números de ficha cambian cada vez que se reordena `datos.json`. Verificado el 24/07/2026: los 12 registros de `PENDIENTES` apuntaban todos a una ficha/imagen distinta de la que apuntaban cuando se escribieron — incluyendo un caso donde reactivar el script habría vuelto a subir a GitHub una imagen vieja sin redactar (con nombres de cliente y de un ejecutivo) y pegádosela a una ficha actual no relacionada.
- **Arreglo aplicado 24/07/2026:** se neutralizó el script (`PENDIENTES = []` y `return` al inicio de `main()`), dejando explicado en el propio archivo por qué y qué no hay que reactivar sin reescribirlo primero para matchear por `stable_key` en vez de `ficha_numero`. Se sincronizó también el disco local (`C:\erp-bot\datos.json` e `imagenes/`) para que coincida con el GitHub ya corregido, cerrando la brecha que el script explotaba. El archivo se conserva (no se borró) como referencia histórica.
- **Pendiente de definir con Olga:** cómo y cuándo se disparaba este script hasta ahora (no es una tarea programada de Cowork — se confirmó vía `list_scheduled_tasks` que no está entre las 7 tareas nativas). Si se ejecutaba manualmente o vía Task Scheduler de Windows, hay que decidir si se retoma (reescrito con `stable_key`) o se retira definitivamente a favor de pushes directos a GitHub.
- **Mitigación en 3 capas para faltantes (23/07/2026), sigue vigente — problema distinto (errores que desaparecen, no imágenes que se revierten):**
  1. `respaldo_errores.json` es la fuente de verdad — solo la escribe `repositorio-errores-erp`.
  2. Tarea programada `auto-repair-datos-json` (cada 30 min) reconcilia `datos.json` contra `respaldo_errores.json` y hace push si faltan errores. Avisa a Olga por Slack solo si tuvo que reparar algo. **Nota:** esta tarea solo detecta errores *faltantes*, no imágenes o campos *corruptos dentro de* un error que sigue presente.
  3. **Pendiente**: GitHub Action (`.github/workflows/auto-repair-datos.yml`, ya escrito). Bloqueado porque el token de GitHub actual no tiene el scope `workflow`.

## 6. Dos tareas programadas — por diseño, no redundancia

- `repositorio-errores-erp` (10:30 AM diario): hace todo el trabajo — auto-repara, busca errores nuevos, crea artículos, escribe en el repo, reporta a Olga.
- `auditoria-pipeline-errores-erp` (11:38 AM, lunes a viernes): vigilante **independiente y de solo lectura**, en su propia sesión. Existe porque si `repositorio-errores-erp` falla catastróficamente ANTES de llegar a su propio reporte de Slack (ej. error de conexión al inicio), nadie se entera. Este vigilante clona el repo por su cuenta y avisa igual.
- **Confirmado y reactivado a propósito por Olga el 15/07/2026** después de haber sido temporalmente fusionado en una sola tarea. No desactivar.

## 7. Dónde se conversa vs. dónde se ejecuta

- Todas las consultas, cambios o diagnósticos se hacen en un chat de Cowork (conversación normal, como esta).
- El panel "Scheduled" del panel lateral es solo para ver si una tarea corrió, pausarla/reactivarla, o ejecutarla manualmente ("Run now"). No es un lugar de conversación.

## 8. Historial de sesiones relevantes (para referencia, no releer completas)

- **"Subida de articulos a Intercom"** (30/06/2026): origen de la regla de imágenes y de "published sin colección".
- **"Repo errores Erp Consolidado Intercom Articulos"** (15/07/2026): corrigió la regla de imágenes en la tarea real, reactivó `auditoria-pipeline-errores-erp`.
- **Este chat** (23/07/2026): auto-reparación en vivo, creación de `auto-repair-datos-json`, intento de GitHub Action (bloqueado por scope), confirmación de la limitación de imágenes de Intercom, creación de este documento.

## 9. Reglas de contenido — reconfirmadas el 24/07/2026 (se habían perdido, no volver a perderlas)

- **Campo `fuente`: nunca nombrar personas.** Ni agentes de soporte (Claudia, Osvaldo, Isabel, Sylvia, Camila, etc.), ni operadoras de Intercom, ni nombres de cliente/empresa. El campo `fuente` solo debe contener: sistema (Slack/Intercom), canal, fecha, y número de caso/ticket si existe. Ejemplo correcto: `"Slack #customer-service-time — 2026-06-03"`. Ejemplo incorrecto: `"Slack #customer-service-time — 2026-06-03 (reporte de Claudia Lavín, cliente Llantas del Pacífico)"`.
- **`solucion_pasos` no puede ser "mandar a soporte".** El público de este repositorio ES soporte (alimenta a Fin AI para el equipo de soporte). Un paso como "contactar a soporte" sin más detalle es inútil y circular para quien lo lee. Cada ficha debe describir la acción técnica real (qué revisar, qué configurar, qué script ejecutar) o, si la ejecuta un rol específico (Plataforma, DBA, PSI/desarrollo), decirlo así en vez de "soporte" genérico.
- **Imágenes: la regla de la sección 1 aplica siempre, sin excepción, incluso a imágenes ya subidas hace tiempo.** No solo a las nuevas. Se han encontrado repetidamente violaciones en imágenes antiguas (nombres de personas en conversaciones de Intercom, nombres de cliente/empresa en títulos de ventana, RUTs visibles, notas físicas fotografiadas con datos de terceros). Cualquier sesión que trabaje en este repo debe re-auditar visualmente las imágenes existentes cuando haga cambios cerca, no asumir que ya están bien porque se subieron en el pasado.
- **Causa raíz confirmada y resuelta el 24/07/2026**: el script local `subir-imagenes-erp.py` (ver sección 5, corregida) era el mecanismo detrás de las reversiones — no un proceso externo. Se neutralizó (`PENDIENTES = []`, `main()` no hace nada) y se sincronizó el disco local con el GitHub ya corregido. Si en el futuro Olga reporta que una imagen "ya corregida" volvió a mostrar datos sin tapar, revisar primero: (a) si alguien reactivó manualmente `subir-imagenes-erp.py`, y (b) si el disco local de `C:\erp-bot` volvió a desincronizarse de GitHub por algún otro medio — no asumir automáticamente un "proceso externo" sin verificarlo primero.

## 10. Migración a Vercel con usuario/contraseña — 25/07/2026

- **Motivo:** el sitio público (`index.html`, servido por GitHub Pages) es visible por cualquiera sin autenticación. GitHub Pages en su plan gratuito no soporta usuario/contraseña. Olga necesita que el sitio no sea público mientras no viva en el servidor propio de Manager.
- **Decisión:** migrar el hosting público a Vercel (plan gratuito Hobby), manteniendo GitHub como fuente de datos (los scripts/tareas programadas siguen haciendo `git push` a este mismo repo — Vercel se redeploya solo en cada push).
- **Cómo se protegió:** Vercel no incluye "Password Protection" gratis (es función de pago del plan Pro). En vez de eso se agregó `middleware.js` en la raíz del repo: un Edge Middleware que exige usuario/contraseña (HTTP Basic Auth) antes de servir cualquier archivo, leyendo las credenciales desde las variables de entorno `SITE_USER` y `SITE_PASSWORD` configuradas en Vercel (Project Settings → Environment Variables) — la contraseña NO está en el código ni en git.
- **Archivos agregados:** `middleware.js`, `package.json` (mínimo, solo para que Vercel reconozca el proyecto), `vercel.json` (`outputDirectory: "."`, sin build).
- **Pendiente (fuera del alcance de Cowork — requiere login de Olga):** crear/conectar la cuenta de Vercel, importar este repo, configurar `SITE_USER`/`SITE_PASSWORD`, y deshabilitar GitHub Pages (Settings → Pages → Source: None) para que la URL vieja sin protección deje de servir contenido.
- **Cuando Manager tenga su propio servidor:** este mismo `middleware.js` se puede desactivar o quitar (o dejar como capa extra) al mover el sitio al servidor definitivo.

## 11. Bug encontrado y corregido — "PENDIENTE DE INVESTIGAR" se mostraba como paso de solución — 25/07/2026

- **Problema:** en las fichas #21, #23, #31 y #32, la nota interna "PENDIENTE DE INVESTIGAR: ... No publicado en el artículo de Intercom porque no es una solución real" se había guardado como el último elemento del array `solucion_pasos`. Ese array es el que `index.html` renderiza tal cual como pasos numerados de la solución (ver función `renderCard`, línea con `const pasos = (e.solucion_pasos || [])...`). Resultado: el sitio (que ahora usan los agentes de soporte con usuario/contraseña) mostraba esa nota interna como si fuera el paso 4 a seguir, en vez de excluirla como se había decidido.
- **La exclusión sí se aplicó correctamente en los artículos de Intercom** (verificado: 15453594, 15453612, 15453614 no contienen esa frase) — el error estaba solo en `datos.json`/`respaldo_errores.json`, que alimentan directamente el sitio.
- **Corrección:** se movió esa nota de `solucion_pasos` a un campo nuevo y separado, `pendiente_investigar` (string), en las 4 fichas afectadas, en `datos.json` y `respaldo_errores.json`. `index.html` no lee ese campo, así que ya no se muestra en el sitio ni se exporta en el CSV. Sigue disponible para quien abra el JSON directamente, para dar seguimiento.
- **Regla nueva para el futuro:** cuando una ficha no tenga solución confirmada y se agregue una nota de seguimiento interno, esa nota va SIEMPRE en el campo `pendiente_investigar`, nunca dentro de `solucion_pasos`. `solucion_pasos` es lo único que se muestra públicamente en el sitio y lo único que debe contener pasos reales y accionables.

## 12. Repositorio de GitHub cambiado a privado — 25/07/2026

- **Motivo:** Olga preguntó si alguien que abriera el link de GitHub vería contenido — confirmado que sí: el repo era público, así que cualquiera con la URL podía ver `datos.json` completo (los 50 errores con síntoma/causa/solución), las imágenes y todo el historial, sin ningún login. El usuario/contraseña de Vercel (sección 10) solo protegía el sitio bonito, no el repositorio en sí.
- **Decisión de Olga:** hacer el repositorio privado de inmediato, aceptando la consecuencia conocida (ver abajo), en vez de esperar a migrar las imágenes primero.
- **Consecuencia aceptada — imágenes rotas en Intercom:** los ~50 artículos ya publicados en Intercom referencian las imágenes vía `https://raw.githubusercontent.com/manager-procesos/repositorio-errores-erp/...`. Esa URL deja de servir el archivo cuando el repo es privado (a menos que la petición lleve un token de autenticación, lo cual Intercom no hace). Resultado esperado: las imágenes de esos artículos van a aparecer rotas/no cargar para quien los vea en Intercom o vía Fin AI.
- **Pendiente para una sesión futura:** migrar esas ~50 imágenes para que queden alojadas directamente en Intercom (subiéndolas dentro del editor de cada artículo, que las sube a su propio CDN) en vez de apuntar a GitHub. Es trabajo manual, artículo por artículo — no hay herramienta de subida masiva por API disponible en este momento.
- **Nota técnica:** el `GITHUB_TOKEN` que usan las tareas programadas (`repositorio-errores-erp`, `auto-repair-datos-json`, etc.) sigue funcionando igual con el repo privado — los tokens de acceso personal de GitHub no distinguen público/privado para repos donde el usuario tiene permiso. La integración de Vercel con GitHub tampoco se ve afectada (su GitHub App ya tenía acceso explícito a este repo).

## 13. Reset de credenciales del sitio (SITE_USER/SITE_PASSWORD) — 27/07/2026

- **Motivo:** Olga no tenía guardada la contraseña creada durante la migración a Vercel (sección 10). Al estar marcadas como "Sensitive" en Vercel, ni ella ni ninguna sesión de Claude/Cowork podían recuperar el valor original una vez guardado — es el comportamiento esperado de esa opción, no un fallo ni un olvido.
- **Acción:** desde esta sesión, usando Claude in Chrome con la sesión de Vercel ya autenticada como mbastias@manager.cl, se reemplazaron ambos valores en Project Settings → Environment Variables (Production and Preview) y se hizo Redeploy manual sobre `main`.
- **Nuevo usuario:** `soporte.erp`. La contraseña nueva quedó guardada únicamente en Vercel (marcada Sensitive) — por diseño, no se documenta en texto plano en este archivo ni en el repo.
- **Verificado:** con las credenciales nuevas el sitio (`repositorio-errores-erp.vercel.app`) responde y carga el listado de fichas (50 errores, 42 resueltos) — el Basic Auth quedó operativo.
- **Nota para el futuro:** si se vuelve a perder la contraseña, el único camino es repetir este mismo reset (Vercel no permite recuperar valores "Sensitive"). Considerar guardar la próxima contraseña en un gestor de contraseñas de Olga en vez de solo en Vercel, para no depender de rehacer este paso.

## 14. Corrida 29/07/2026 — nueva ficha, imagen rota confirmada por diseño (no error)

- Auto-reparación: `datos.json` estaba íntegro (coincidía con `respaldo_errores.json`, 50 errores). Nada que restaurar.
- Error nuevo documentado: **#51 — Error al importar comprobantes desde REX+ (centro de costo obligatorio no configurado)**, fuente Slack #customer-service-time (28/07/2026), con solución real (agregar centro de costo manualmente en el archivo, o solicitar a REX+ que lo configure en origen).
- **Imagen:** se descargó el adjunto real desde Slack (`F0BM92CE2QY`) y al revisarlo mostraba el nombre del cliente (razón social + logo) en el encabezado del informe exportado — dato sensible según sección 1 de este documento. No fue posible redactarlo por zonas con las herramientas de esta sesión: no hay forma de obtener los bytes crudos de un archivo de Slack para editarlo con PIL (el tool de lectura solo permite visualizar la imagen, no escribirla a disco). Se usó el placeholder genérico como excepción documentada (no por regla, sino por esta limitación técnica puntual). Si una sesión futura tiene forma de bajar el binario real, se puede reemplazar `imagenes/error-51-rex-centro-costo.png` y redactar por zonas como corresponde.
- **Confirmación de la sección 12 (repo privado):** al crear el artículo de Intercom con `imagen_github` apuntando a `raw.githubusercontent.com`, Intercom devolvió `unsupported_html — Image not found`. Confirma en vivo que la consecuencia aceptada el 25/07/2026 (URLs de GitHub rotas para Intercom por ser el repo privado) también aplica a fichas **nuevas**, no solo a las ~50 ya migradas antes de esa fecha. El artículo de la ficha #51 (ID 16131152) se publicó **sin** la etiqueta `<img>` para evitar el error de creación; `datos.json` sí conserva `imagen_github`/`imagen_local` para cuando se resuelva la migración de imágenes (sección 12, pendiente).

## 15. Corrección 29/07/2026 — imagen de la ficha #51 pasó de placeholder genérico a reconstrucción redactada

- Olga pidió aplicar el mismo tratamiento de siempre (tapar solo el dato sensible, conservar el resto) en vez del placeholder genérico usado inicialmente en la ficha #51.
- Aclaración importante: no se pudo editar el archivo PNG original bit a bit porque esta sesión no tiene forma de bajar los bytes crudos de un adjunto de Slack a disco (la herramienta de lectura solo permite visualizarlo, no descargarlo). En su lugar se reconstruyó el contenido manualmente: se transcribió el texto real visible en la captura (encabezado del informe, "Registros que no pudieron ser Importados desde Sucursales", "Descripción del Error", y las ~32 líneas "Linea:N. Cuenta:XXXXXX...") y se regeneró como imagen nueva, reemplazando únicamente el nombre/logo del cliente (antes "INPROCO SPA" + logo) por "NOMBRE CLIENTE" / "LOGO CLIENTE" genéricos. El resto del contenido (todas las líneas de error, cuentas, fecha, nombre de informe) es fiel a lo que mostraba la captura original.
- Esto no es idéntico a "tapar con un rectángulo sobre el archivo original" como se hace cuando sí se tiene el binario — es una recreación del mismo contenido. Se deja esta distinción documentada para que quede claro el método usado, por si una sesión futura sí logra obtener el archivo original y quiere reemplazarlo por una edición real.
