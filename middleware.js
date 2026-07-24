// Proteccion con usuario/contrasena para el repositorio de errores ERP.
// Se ejecuta como Vercel Edge Middleware ANTES de servir cualquier archivo estatico
// (index.html, datos.json, imagenes/, etc.) - nadie ve el contenido sin pasar por aqui.
//
// Configuracion (Vercel -> Project Settings -> Environment Variables):
//   SITE_USER      = usuario que deben ingresar
//   SITE_PASSWORD  = contrasena que deben ingresar
//
// Si esas variables no estan configuradas, el sitio se bloquea por defecto
// (mejor fallar cerrado que dejarlo abierto por accidente).

export const config = {
  matcher: "/(.*)",
};

function unauthorized() {
  return new Response("Autenticacion requerida.", {
    status: 401,
    headers: {
      "WWW-Authenticate": 'Basic realm="Repositorio Errores ERP", charset="UTF-8"',
      "Content-Type": "text/plain; charset=utf-8",
    },
  });
}

export default function middleware(request) {
  const expectedUser = process.env.SITE_USER;
  const expectedPass = process.env.SITE_PASSWORD;

  if (!expectedUser || !expectedPass) {
    return unauthorized();
  }

  const authHeader = request.headers.get("authorization");
  if (!authHeader || !authHeader.startsWith("Basic ")) {
    return unauthorized();
  }

  let decoded;
  try {
    decoded = atob(authHeader.slice(6));
  } catch {
    return unauthorized();
  }

  const separatorIndex = decoded.indexOf(":");
  if (separatorIndex === -1) {
    return unauthorized();
  }

  const providedUser = decoded.slice(0, separatorIndex);
  const providedPass = decoded.slice(separatorIndex + 1);

  if (providedUser !== expectedUser || providedPass !== expectedPass) {
    return unauthorized();
  }

  // Usuario y contrasena correctos: no devolvemos Response, la request
  // sigue su curso normal hacia el archivo estatico solicitado.
}
