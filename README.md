# Web de Manadi

Sitio de [manadi.com.ar](https://manadi.com.ar). Catálogo de la Colección
Manadi y contacto; la venta se cierra por WhatsApp.

Hecho con [Astro](https://astro.build) y Tailwind CSS. Es un sitio estático:
no tiene base de datos ni servidor propio.

## Trabajar en el proyecto

```bash
npm install     # la primera vez
npm run dev     # abre http://localhost:4321
npm run build   # genera el sitio en dist/
```

## Cambiar un precio

Los productos están en `src/content/productos/`, un archivo por producto. Para
cambiar un precio se edita el número y listo:

```yaml
precio:
  opciones:
    - monto: 120000
  cuotas: 3
  transferencia:
    monto: 90000
    descuento: 25
```

Los montos van sin puntos ni signo `$`: el formato lo pone el sitio.

## Agregar un producto

1. Poner las fotos en `src/assets/productos/`.
2. Copiar un archivo de `src/content/productos/` y cambiarle los datos.
3. El `orden` define la posición en la grilla; `destacado: true` lo suma a la
   portada.

Si las fotos vienen directo de la cámara (pesadas o en formato `.NEF`), el
script las prepara:

```bash
npm run fotos
```

Ese script también regenera el logo, el favicon y la imagen que se ve al
compartir el enlace, todo a partir de `Logo.pdf`.

## Estructura

- `src/content/productos/` — los productos, un archivo por cada uno
- `src/pages/` — las páginas del sitio
- `src/components/` — piezas reutilizables (galería, tarjeta, precio)
- `src/lib/sitio.ts` — teléfono, mail, Instagram y textos generales
- `src/styles/global.css` — colores y tipografías de la marca
- `scripts/procesar-fotos.py` — preparación de fotos y logo

## Marca

- Beige `#E8E3DD`, marrón `#57432D`
- Títulos en Engravers Gothic BT (la fuente del logo), textos en Manrope
