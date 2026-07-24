"""
subir-imagenes-erp.py — pipeline completo [NEUTRALIZADO el 24/07/2026]

*** ESTE SCRIPT YA NO HACE NADA (ver guard en main()). NO BORRAR — se deja
*** como referencia histórica, pero su lista PENDIENTES está permanentemente
*** desactualizada y es PELIGROSA si se reactiva. Ver explicación abajo.

Motivo de la desactivación:
- Este script sube imágenes/datos.json LEYENDO PRIMERO EL DISCO LOCAL de
  C:\\erp-bot y luego sobreescribe GitHub por completo (no hace merge/patch).
  Cada vez que corrió, revirtió silenciosamente correcciones de anonimización
  ya aplicadas directamente en GitHub (porque el disco local había quedado
  desactualizado respecto a GitHub).
- Además, la lista PENDIENTES está indexada por "ficha_numero", pero los
  números de ficha se reordenan cada vez que se agregan/quitan errores.
  Verificado el 24/07/2026: TODOS los 12 registros de PENDIENTES apuntan hoy
  a un error distinto al que apuntaban cuando se escribieron (ej: numero 24
  hoy es "faltan drivers", pero PENDIENTES intentaría pegarle la imagen
  antigua con datos de clientes sin tapar "Felipe Rosas / Francisco Gomez
  Cortes / Caja Concepción" — exactamente el tipo de dato que no puede
  mostrarse). Reactivar este script tal cual corrompería ~12 fichas.
- Conclusión: las imágenes que este script intentaba subir ya están todas
  resueltas en GitHub por otra vía. Este script no tiene ningún trabajo
  pendiente legítimo que hacer. Si en el futuro se necesita un pipeline
  similar, debe reescribirse para matchear por "stable_key" (slack_file_id /
  intercom id / sha del contenido), nunca por "ficha_numero".
"""
import base64, json, requests
from pathlib import Path
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

SLACK_TOKEN      = ""  # token removido 24/07/2026 al neutralizar el script (ya no se usa, ver docstring)
CARPETA_IMAGENES = Path(__file__).parent / "imagenes"
DATOS_JSON       = Path(__file__).parent / "datos.json"
GITHUB_TOKEN     = ""  # token removido 24/07/2026 al neutralizar el script (ya no se usa, ver docstring)
GITHUB_REPO      = "manager-procesos/repositorio-errores-erp"
GITHUB_API       = "https://api.github.com"
GITHUB_RAW       = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main"
GITHUB_HEADERS   = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}

# NEUTRALIZADO 24/07/2026: lista vaciada a propósito. Ver aviso al inicio del
# archivo — la lista original quedó completamente desactualizada (todos sus
# 12 registros ahora apuntan a fichas/imágenes equivocadas) y volver a
# poblarla sin reescribir el matching por stable_key volvería a corromper
# datos. No restaurar la lista original.
PENDIENTES = []


def descargar_slack(client, file_id, token):
    """Descarga imagen desde Slack. Retorna bytes o None."""
    try:
        info = client.files_info(file=file_id)
        url = info["file"].get("url_private_download") or info["file"].get("url_private")
        if url:
            r = requests.get(url, headers={"Authorization": f"Bearer {token}"})
            if r.status_code == 200 and len(r.content) > 1000:
                print(f"   Slack API ✓ ({len(r.content)//1024} KB)")
                return r.content
    except SlackApiError as e:
        print(f"   Slack API error: {e.response['error']}")
    # Fallback: URL directa
    url_directa = f"https://files.slack.com/files-pri/T041ULNK95X-{file_id}/image.png"
    r = requests.get(url_directa, headers={"Authorization": f"Bearer {token}"}, allow_redirects=True)
    if r.status_code == 200 and len(r.content) > 1000:
        print(f"   Slack URL directa ✓ ({len(r.content)//1024} KB)")
        return r.content
    print(f"   No se pudo descargar de Slack (status {r.status_code})")
    return None


def subir_imagen_github(imagen_bytes, nombre):
    """Sube imagen a GitHub. Retorna URL raw o None."""
    url = f"{GITHUB_API}/repos/{GITHUB_REPO}/contents/imagenes/{nombre}"
    b64 = base64.b64encode(imagen_bytes).decode()
    r = requests.get(url, headers=GITHUB_HEADERS)
    sha = r.json().get("sha") if r.status_code == 200 else None
    data = {"message": f"Imagen {nombre}", "content": b64, "branch": "main"}
    if sha:
        data["sha"] = sha
    r = requests.put(url, headers=GITHUB_HEADERS, json=data)
    if r.status_code in (200, 201):
        print(f"   GitHub imagen ✓")
        return f"{GITHUB_RAW}/imagenes/{nombre}"
    print(f"   Error GitHub imagen: {r.status_code} — {r.text[:120]}")
    return None


def push_datos_json(datos):
    """Reemplaza datos.json en GitHub con el contenido local completo."""
    url = f"{GITHUB_API}/repos/{GITHUB_REPO}/contents/datos.json"
    r = requests.get(url, headers=GITHUB_HEADERS)
    if r.status_code != 200:
        print(f"   Error leyendo datos.json en GitHub: {r.status_code}")
        return False
    sha = r.json()["sha"]
    contenido = json.dumps(datos, ensure_ascii=False, indent=2)
    b64 = base64.b64encode(contenido.encode("utf-8")).decode()
    r = requests.put(url, headers=GITHUB_HEADERS, json={
        "message": "Sync datos.json — pipeline subir-imagenes-erp",
        "content": b64,
        "sha": sha,
        "branch": "main"
    })
    ok = r.status_code in (200, 201)
    print(f"   datos.json GitHub {'✓' if ok else 'ERROR ' + str(r.status_code)}")
    return ok


def main():
    print("=" * 60)
    print("Pipeline: subir imágenes + sync datos.json")
    print("=" * 60)
    print()
    print("*** NEUTRALIZADO el 24/07/2026 — este script no hace nada. ***")
    print("PENDIENTES está vacía a propósito: la lista original quedó")
    print("desactualizada (todos sus 'ficha_numero' apuntan hoy a fichas")
    print("distintas) y reactivarla corrompería imágenes/datos ya corregidos.")
    print("Ver el docstring al inicio del archivo para el detalle completo.")
    print("Si necesitas subir una imagen puntual, hazlo directo a GitHub")
    print("(git push) en vez de reactivar este pipeline.")
    return

    CARPETA_IMAGENES.mkdir(exist_ok=True)

    # Cargar datos.json local
    if not DATOS_JSON.exists():
        print("ERROR: datos.json no encontrado en", DATOS_JSON)
        return
    with open(DATOS_JSON, encoding="utf-8") as f:
        datos = json.load(f)

    # Índice por número para actualizar imagen_github
    indice = {e["numero"]: e for e in datos.get("errores", [])}

    client = WebClient(token=SLACK_TOKEN)
    try:
        auth = client.auth_test()
        print(f"Slack: {auth['user']} ✓\n")
    except SlackApiError as e:
        print(f"Error auth Slack: {e.response['error']}")
        return

    ok = 0
    sin_imagen = []

    for item in PENDIENTES:
        num = item["ficha_numero"]
        nombre = item["nombre_archivo"]
        ruta = CARPETA_IMAGENES / nombre
        print(f"─── #{num} {nombre} ───")

        # 1. Obtener bytes: disco primero, Slack si no está
        if ruta.exists():
            imagen = ruta.read_bytes()
            print(f"   En disco ✓ ({len(imagen)//1024} KB)")
        elif item["slack_file_id"]:
            print(f"   Descargando desde Slack {item['slack_file_id']}...")
            imagen = descargar_slack(client, item["slack_file_id"], SLACK_TOKEN)
            if imagen:
                ruta.write_bytes(imagen)
        else:
            print(f"   Sin imagen en disco y sin slack_file_id — omitido")
            sin_imagen.append(num)
            continue

        if not imagen:
            print(f"   No se pudo obtener imagen — omitido")
            sin_imagen.append(num)
            continue

        # 2. Subir imagen a GitHub
        url_github = subir_imagen_github(imagen, nombre)
        if not url_github:
            continue

        # 3. Actualizar campo imagen_github en datos local
        if num in indice:
            indice[num]["imagen_github"] = url_github
            ok += 1
        else:
            print(f"   Advertencia: ficha #{num} no encontrada en datos.json")

    # 4. Push datos.json completo a GitHub (una sola operación)
    print(f"\n─── Sync datos.json → GitHub ───")
    push_datos_json(datos)

    # 5. Guardar datos.json local actualizado
    with open(DATOS_JSON, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    print("   datos.json local ✓")

    print(f"\n{ok}/{len(PENDIENTES) - len(sin_imagen)} imágenes subidas a GitHub")
    if sin_imagen:
        print(f"Sin imagen (omitidos): {sin_imagen}")
    print("Portal: https://manager-procesos.github.io/repositorio-errores-erp/")


if __name__ == "__main__":
    main()
