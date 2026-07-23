# Decisiones y reglas confirmadas — Repositorio de Errores ERP

Este documento es la **fuente única de verdad** de todas las decisiones y reglas acordadas con Olga sobre este proyecto (búsqueda de errores de Manager ERP, publicación en este repositorio, y creación de artículos en Intercom para Fin AI).

**Regla para cualquier sesión de Claude/Cowork que trabaje en este proyecto: lee este archivo primero. Si algo aquí contradice lo que crees recordar de un chat, este archivo tiene prioridad — está confirmado con evidencia, no con memoria.**

Última actualización: 23/07/2026.

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

## 5. `datos.json` y el proceso externo "subir-imagenes-erp"

- Existe un proceso **externo, no controlado por Claude/Cowork**, llamado "subir-imagenes-erp", que sobrescribe `datos.json` completo (no lo fusiona) cada vez que corre. Esto ha borrado errores agregados por este pipeline al menos el 10/07, 14-15/07 y 22-23/07/2026.
- No es un problema de horarios — es que ese proceso reemplaza el archivo entero sin revisar qué había antes. Cambiar el horario de nuestras tareas no lo evita, porque no controlamos cuándo corre el otro proceso.
- **Mitigación en 3 capas (23/07/2026):**
  1. `respaldo_errores.json` es la fuente de verdad — solo la escribe `repositorio-errores-erp`, el proceso externo nunca lo toca.
  2. Tarea programada `auto-repair-datos-json` (cada 30 min) reconcilia `datos.json` contra `respaldo_errores.json` y hace push si faltan errores. Avisa a Olga por Slack solo si tuvo que reparar algo.
  3. **Pendiente**: GitHub Action (`.github/workflows/auto-repair-datos.yml`, ya escrito) que haría lo mismo en segundos en vez de cada 30 min, disparado por cualquier push. Bloqueado porque el token de GitHub actual no tiene el scope `workflow`. Cuando se consiga un token con ese scope, se sube y la tarea de 30 min pasa a ser redundante (se puede desactivar).

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
