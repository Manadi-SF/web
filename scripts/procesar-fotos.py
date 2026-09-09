"""
Prepara las fotos de producto y el logo para la web.

Las fotos originales pesan entre 3 y 6 MB y miden mas de 4000 px: sin procesar
harian el build lentisimo y el repo enorme. Este script las deja en 2000 px de
lado maximo con nombres previsibles, y convierte los .NEF (crudos de camara)
que no puede leer ningun navegador.

Astro se encarga despues de generar WebP/AVIF en los tamanos que necesita cada
pagina, asi que aca solo dejamos un buen original.

Uso: npm run fotos
"""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageOps

RAIZ = Path(__file__).resolve().parent.parent
ORIGINALES = RAIZ / "fotos-originales"
DESTINO = RAIZ / "src" / "assets" / "productos"
LOGOS = RAIZ / "src" / "assets"
MARCA = RAIZ / "marca"

LADO_MAXIMO = 2000
CALIDAD = 85

# Origen de las fotos que mandaron por Drive y de las que llegaron por chat.
CARPETA_DRIVE = Path(
    r"C:\Users\Windows\Downloads\Coleccion-20260908T211139Z-1-001\Coleccion"
)
CARPETA_CHAT = Path(
    r"C:\Users\Windows\.cursor\projects\c-Users-Windows-Desktop-Mauro-Manadi\assets"
)
# El PDF original del logo vive en el repo, asi que esto se puede volver a
# correr en cualquier maquina.
LOGO_PDF = MARCA / "logo.pdf"

# Nombre original -> nombre final. Los nombres finales son los que usan las
# fichas de producto en src/content/productos/.
FOTOS: dict[str, str] = {
    # Mesa matera: los tres colores disponibles
    "1 MESA TAPIR.JPG": "mesa-matera-tapir-1",
    "1 MESA TAPIR (2).JPG": "mesa-matera-tapir-2",
    "1 MESA TAPIR (3).JPG": "mesa-matera-tapir-3",
    "2 MESA CALIZA.JPG": "mesa-matera-caliza-1",
    "2 MESA CALIZA (2).JPG": "mesa-matera-caliza-2",
    "2 MESA CALIZA (3).JPG": "mesa-matera-caliza-3",
    "3 MESA GRAFITO.JPG": "mesa-matera-grafito-1",
    "3 MESA GRAFITO (2).JPG": "mesa-matera-grafito-2",
    "MANTA DE LA MESA.JPG": "mesa-matera-manta",
    "MESA PLEGADA.JPG": "mesa-matera-plegada",
    # Los tres disenos de grabado de la mesa
    "1 Grabado del SOL.NEF": "grabado-sol",
    "1 Grabado ESTAMPITAS.JPG": "grabado-estampitas",
    "1 Grabado TAN ARGENTINO QUE DUELE.JPG": "grabado-tan-argentino",
    # Posavasos
    "1 PORTA POSAVASOS Y POSAVASOS.png": "posavasos-con-porta",
    "1 POSAVASOS (2).jpg": "posavasos-sueltos",
    # Argentina para pared
    "ARGENTINA PARA PARED 1.jpg": "argentina-pared-1",
    "ARGENTINA PARA PARED 2.jpg": "argentina-pared-2",
    # Huevera
    "1000414127.jpg": "huevera-1",
    "1000414128.jpg": "huevera-2",
    "1000414129.jpg": "huevera-3",
    "Huevera.jpeg": "huevera-4",
    # Portallaves
    "Portallaves de UP.jpeg": "portallaves-up-1",
}

# Fotos que llegaron por chat, con su nombre de archivo guardado.
FOTOS_CHAT: dict[str, str] = {
    "c__Users_Windows_AppData_Roaming_Cursor_User_workspaceStorage_f571ca1cb5a139a1a9c648188f5037a0_images_image-5f84b000-d1d9-488d-8c17-b6363ecd109b.png": "organizador-mesita-1",
    "c__Users_Windows_AppData_Roaming_Cursor_User_workspaceStorage_f571ca1cb5a139a1a9c648188f5037a0_images_image-92e81f3b-0a70-4759-b39c-a013d87b9477.png": "cuadro-futbol-colon",
}


def copiar_originales() -> None:
    """Guarda una copia local de los originales, fuera del control de versiones."""
    ORIGINALES.mkdir(parents=True, exist_ok=True)
    for carpeta, mapa in ((CARPETA_DRIVE, FOTOS), (CARPETA_CHAT, FOTOS_CHAT)):
        if not carpeta.exists():
            print(f"  aviso: no encuentro {carpeta}")
            continue
        for nombre in mapa:
            origen = carpeta / nombre
            if origen.exists():
                shutil.copy2(origen, ORIGINALES / nombre)


def abrir(ruta: Path) -> Image.Image:
    """Abre una imagen, revelando los crudos .NEF cuando hace falta."""
    if ruta.suffix.lower() == ".nef":
        import rawpy  # solo se necesita si hay crudos

        with rawpy.imread(str(ruta)) as crudo:
            return Image.fromarray(crudo.postprocess(use_camera_wb=True))
    return Image.open(ruta)


def procesar(origen: Path, nombre_final: str) -> str:
    imagen = abrir(origen)

    # Las fotos de celular traen la orientacion en los metadatos EXIF: si no la
    # aplicamos, algunas se ven acostadas.
    imagen = ImageOps.exif_transpose(imagen)

    tiene_transparencia = imagen.mode in ("RGBA", "LA", "P")
    imagen = imagen.convert("RGBA" if tiene_transparencia else "RGB")

    if max(imagen.size) > LADO_MAXIMO:
        imagen.thumbnail((LADO_MAXIMO, LADO_MAXIMO), Image.LANCZOS)

    if tiene_transparencia:
        destino = DESTINO / f"{nombre_final}.png"
        imagen.save(destino, "PNG", optimize=True)
    else:
        destino = DESTINO / f"{nombre_final}.jpg"
        imagen.save(destino, "JPEG", quality=CALIDAD, optimize=True, progressive=True)

    kb = destino.stat().st_size / 1024
    return f"{destino.name}  {imagen.size[0]}x{imagen.size[1]}  {kb:.0f} KB"


MARRON = "#57432d"
BEIGE = "#e8e3dd"

# El PDF viene de CorelDRAW y trae dos cosas que no queremos en la web: un marco
# de 1 punto que bordea toda la pagina, y una linea del isotipo en negro en vez
# de marron. Ademas el logo esta centrado con muchisimo aire alrededor.
MARCO = re.compile(
    r'<path[^>]*d="M0 0H708\.\d+V708\.\d+H0Z"[^>]*/>\s*', re.IGNORECASE
)
ESCALA_RENDER = 4
MARGEN_MARCO = 8  # px del render que hay que descartar para matar el marco


def generar_logo() -> None:
    """Saca el logo del PDF en vectorial, que es lo que conviene para la web.

    Deja un SVG recortado al logo y con fondo transparente (asi se puede usar
    sobre cualquier color de seccion), mas un PNG grande para compartir en redes,
    donde el SVG no funciona.
    """
    if not LOGO_PDF.exists():
        print(f"  aviso: no encuentro {LOGO_PDF}")
        return

    import pymupdf

    documento = pymupdf.open(LOGO_PDF)
    pagina = documento[0]

    # Render en alta para el PNG y, de paso, para medir donde esta el logo.
    pixeles = pagina.get_pixmap(matrix=pymupdf.Matrix(ESCALA_RENDER, ESCALA_RENDER))
    png = LOGOS / "logo.png"
    pixeles.save(str(png))

    logo = Image.open(png).convert("RGBA")
    # Descartamos el borde del render, donde vive el marco del PDF.
    ancho, alto = logo.size
    logo = logo.crop(
        (MARGEN_MARCO, MARGEN_MARCO, ancho - MARGEN_MARCO, alto - MARGEN_MARCO)
    )

    datos = []
    for r, g, b, _ in logo.getdata():
        es_fondo = r > 200 and g > 195 and b > 185 and abs(r - g) < 25 and abs(g - b) < 25
        # Los pixeles de fondo van a negro transparente: si les dejaramos el
        # beige, al escalar el logo aparece un halo claro en los bordes.
        datos.append((0, 0, 0, 0) if es_fondo else (r, g, b, 255))
    logo.putdata(datos)

    # El recorte se calcula sobre la transparencia, no sobre el color.
    recorte = logo.getchannel("A").getbbox()
    if not recorte:
        raise SystemExit("el logo quedo vacio al quitar el fondo")
    logo = logo.crop(recorte)
    logo.save(png, "PNG", optimize=True)

    # Las mismas medidas, pasadas a las unidades del PDF, sirven de viewBox para
    # que el SVG quede recortado igual que el PNG.
    x0, y0, x1, y1 = recorte
    caja = [
        (v + MARGEN_MARCO) / ESCALA_RENDER for v in (x0, y0, x1 - x0, y1 - y0)
    ]
    caja[2] = (x1 - x0) / ESCALA_RENDER
    caja[3] = (y1 - y0) / ESCALA_RENDER

    svg = pagina.get_svg_image(text_as_path=True)
    svg = MARCO.sub("", svg)
    svg = svg.replace("#231f20", MARRON)
    svg = re.sub(
        r'(<svg[^>]*?)width="[\d.]+"\s+height="[\d.]+"\s+viewBox="[^"]+"',
        rf'\1width="{caja[2]:.2f}" height="{caja[3]:.2f}" '
        rf'viewBox="{caja[0]:.2f} {caja[1]:.2f} {caja[2]:.2f} {caja[3]:.2f}"',
        svg,
        count=1,
    )
    (LOGOS / "logo.svg").write_text(svg, encoding="utf-8")

    generar_favicon(svg, pagina)
    generar_imagen_social(logo)

    documento.close()
    print(f"  logo.svg y logo.png ({logo.size[0]}x{logo.size[1]})")


def generar_favicon(svg: str, pagina) -> None:
    """Favicon con el isotipo solo.

    En 32 px el logo completo es una manchita ilegible, asi que usamos solo el
    trazo con el destello del laser, que si se reconoce en chico.
    """
    # Los dibujos del PDF son el isotipo; el unico que descartamos es el marco,
    # que ocupa la pagina entera.
    pagina_completa = pagina.rect.width * pagina.rect.height * 0.9
    cajas = [
        d["rect"]
        for d in pagina.get_drawings()
        if d["rect"].width * d["rect"].height < pagina_completa
    ]
    if not cajas:
        return

    x0 = min(c.x0 for c in cajas)
    y0 = min(c.y0 for c in cajas)
    x1 = max(c.x1 for c in cajas)
    y1 = max(c.y1 for c in cajas)

    margen = 12
    ancho, alto = x1 - x0 + margen * 2, y1 - y0 + margen * 2

    # Se quitan las letras: en el favicon solo va el trazo.
    solo_isotipo = re.sub(r"<use[^>]*/>\s*", "", svg)
    solo_isotipo = re.sub(
        r'(<svg[^>]*?)width="[\d.]+"\s+height="[\d.]+"\s+viewBox="[^"]+"',
        rf'\1width="{ancho:.2f}" height="{alto:.2f}" '
        rf'viewBox="{x0 - margen:.2f} {y0 - margen:.2f} {ancho:.2f} {alto:.2f}"',
        solo_isotipo,
        count=1,
    )
    (RAIZ / "public" / "favicon.svg").write_text(solo_isotipo, encoding="utf-8")
    # La misma pieza se usa en el encabezado, donde el logo completo no se lee.
    (LOGOS / "isotipo.svg").write_text(solo_isotipo, encoding="utf-8")
    print("  favicon.svg e isotipo.svg")


def generar_imagen_social(logo: Image.Image) -> None:
    """Imagen de 1200x630 para cuando se comparte el enlace por WhatsApp."""
    lienzo = Image.new("RGB", (1200, 630), BEIGE)

    marca = logo.copy()
    marca.thumbnail((720, 380), Image.LANCZOS)
    lienzo.paste(
        marca,
        ((1200 - marca.size[0]) // 2, (630 - marca.size[1]) // 2),
        marca,
    )

    destino = RAIZ / "public" / "og.png"
    lienzo.save(destino, "PNG", optimize=True)
    print(f"  og.png ({destino.stat().st_size / 1024:.0f} KB)")


def main() -> int:
    DESTINO.mkdir(parents=True, exist_ok=True)
    LOGOS.mkdir(parents=True, exist_ok=True)

    print("Copiando originales...")
    copiar_originales()

    print("Procesando fotos...")
    faltantes: list[str] = []
    for carpeta, mapa in ((CARPETA_DRIVE, FOTOS), (CARPETA_CHAT, FOTOS_CHAT)):
        for nombre, nombre_final in mapa.items():
            origen = carpeta / nombre
            if not origen.exists():
                origen = ORIGINALES / nombre
            if not origen.exists():
                faltantes.append(nombre)
                continue
            print(f"  {procesar(origen, nombre_final)}")

    print("Generando logo...")
    generar_logo()

    if faltantes:
        print("\nNo encontre estas fotos:")
        for nombre in faltantes:
            print(f"  - {nombre}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
