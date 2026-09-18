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
# Fotos que no son de producto: la del equipo, ejemplos, y lo que venga.
DESTINO_SITIO = RAIZ / "src" / "assets" / "sitio"
DESTINO_TRABAJOS = RAIZ / "src" / "assets" / "trabajos"
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
    "c__Users_Windows_AppData_Roaming_Cursor_User_workspaceStorage_f571ca1cb5a139a1a9c648188f5037a0_images_PRODUCTO_ETIQUETA_ECO_CUERO-b3684696-f7a8-4909-898a-8bf58a7c0a3f.jpg": "etiquetas-ecocuero-1",
    "c__Users_Windows_AppData_Roaming_Cursor_User_workspaceStorage_f571ca1cb5a139a1a9c648188f5037a0_images_FOTO_EJEMPLO_DERECHO_E_IZQUIERDO-5414e224-9ee7-4ad7-8e1b-89a014977f43.jpg": "organizador-mesita-2",
    "c__Users_Windows_AppData_Roaming_Cursor_User_workspaceStorage_f571ca1cb5a139a1a9c648188f5037a0_images_WhatsApp_Image_2026-091-17_at_15.23.09-9e617ee6-43aa-47cc-a1f2-726e644a1c3b.jpg": "argentina-luces-1",
    "c__Users_Windows_AppData_Roaming_Cursor_User_workspaceStorage_f571ca1cb5a139a1a9c648188f5037a0_images_WhatsApp_Image_2026-09-17_at_15.23.107-0dc51875-e3b2-41d2-b9ec-4c89a1082ffa.jpg": "argentina-luces-2",
    "c__Users_Windows_AppData_Roaming_Cursor_User_workspaceStorage_f571ca1cb5a139a1a9c648188f5037a0_images_WhatsApp_Image_2026-09-17_at_15.23.07-7dfb8087-f59d-40fb-a306-dbc4a1fe9c58.jpg": "argentina-luces-3",
    "c__Users_Windows_AppData_Roaming_Cursor_User_workspaceStorage_f571ca1cb5a139a1a9c648188f5037a0_images_Copia_de_Llaveros_en_acrilico-efc6f55d-8105-41f8-8f42-a7a3b35e1aca.jpg": "llaveros-acrilico-1",
    "c__Users_Windows_AppData_Roaming_Cursor_User_workspaceStorage_f571ca1cb5a139a1a9c648188f5037a0_images_Copia_de_LLaveros_en_acrilico__2_-b6dc9b25-9452-46c9-83d7-6309ade92c85.jpg": "llaveros-acrilico-2",
    "c__Users_Windows_AppData_Roaming_Cursor_User_workspaceStorage_f571ca1cb5a139a1a9c648188f5037a0_images_Copia_de_LLaveros_en_acrilico-02c654fa-79f7-43c1-b9f5-edbf398f4dc5.jpg": "llaveros-acrilico-3",
}

# Fotos del sitio que no son de producto. Van a src/assets/sitio/.
FOTOS_SITIO: dict[str, str] = {
    "c__Users_Windows_AppData_Roaming_Cursor_User_workspaceStorage_f571ca1cb5a139a1a9c648188f5037a0_images_FOTO_-_QUIENES_SOMOS-a3a24b4e-5813-492f-95c7-e4de6ba22070.jpg": "quienes-somos",
}

# Galeria de encargos de clientes. Van a src/assets/trabajos/.
FOTOS_TRABAJOS: dict[str, str] = {
    "c__Users_Windows_AppData_Roaming_Cursor_User_workspaceStorage_f571ca1cb5a139a1a9c648188f5037a0_images_Cajas_de_t___2_-e0ee0d90-af8f-4113-b746-09dac87a749d.jpg": "cajas-te",
    "c__Users_Windows_AppData_Roaming_Cursor_User_workspaceStorage_f571ca1cb5a139a1a9c648188f5037a0_images_Caja_de_truco-208fdaa8-da88-4223-8ba3-f4cc104c204c.jpg": "caja-truco",
    "c__Users_Windows_AppData_Roaming_Cursor_User_workspaceStorage_f571ca1cb5a139a1a9c648188f5037a0_images_Adorno_para_arbol_de_navidad-ff62608d-0483-45fb-8379-5bd64684cb67.jpg": "adorno-navidad",
    "c__Users_Windows_AppData_Roaming_Cursor_User_workspaceStorage_f571ca1cb5a139a1a9c648188f5037a0_images_Anotadores-dd9ceb43-d268-46a4-a939-ee9c4089e885.jpg": "anotadores",
    "c__Users_Windows_AppData_Roaming_Cursor_User_workspaceStorage_f571ca1cb5a139a1a9c648188f5037a0_images_Enebrador_de_gato-2a76ce30-4426-49b1-a1a2-3904e8ccc6ab.jpg": "enhebrador-gato",
    "c__Users_Windows_AppData_Roaming_Cursor_User_workspaceStorage_f571ca1cb5a139a1a9c648188f5037a0_images_Enhebrador_de_manzana-49016628-b367-4446-ac6a-ce581b6f66e6.jpg": "enhebrador-manzana",
    "c__Users_Windows_AppData_Roaming_Cursor_User_workspaceStorage_f571ca1cb5a139a1a9c648188f5037a0_images_Centro_de_mesa_portaservilletas-9e2c841b-e6de-4326-bc6e-bc19347dbccc.jpg": "centros-mesa",
    "c__Users_Windows_AppData_Roaming_Cursor_User_workspaceStorage_f571ca1cb5a139a1a9c648188f5037a0_images_Cuadro_personalizado__2_-9aefb62e-9e3b-47e7-b08b-8b3cdf1050ac.jpg": "cuadro-perro",
    "c__Users_Windows_AppData_Roaming_Cursor_User_workspaceStorage_f571ca1cb5a139a1a9c648188f5037a0_images_Exhibidor__4_-bd46a343-1591-42a1-a582-c79726022b23.jpg": "exhibidor",
    "c__Users_Windows_AppData_Roaming_Cursor_User_workspaceStorage_f571ca1cb5a139a1a9c648188f5037a0_images_Fichero-e2b91d3a-35ea-47d7-91ae-120f3129c61c.jpg": "fichero",
    "c__Users_Windows_AppData_Roaming_Cursor_User_workspaceStorage_f571ca1cb5a139a1a9c648188f5037a0_images_Figuras_para_pintar-72b8412f-facd-42d2-943b-49836687c5c2.jpg": "figuras-pintar-1",
    "c__Users_Windows_AppData_Roaming_Cursor_User_workspaceStorage_f571ca1cb5a139a1a9c648188f5037a0_images_Figuras_para_pintar__2_-7fe05ab0-c139-49c7-aca0-9c628f8e1b3d.jpg": "figuras-pintar-2",
    "c__Users_Windows_AppData_Roaming_Cursor_User_workspaceStorage_f571ca1cb5a139a1a9c648188f5037a0_images_Medallas_en_MDF-3790cfaa-a41c-43a5-addc-c025f766a3d1.jpg": "medallas",
    "c__Users_Windows_AppData_Roaming_Cursor_User_workspaceStorage_f571ca1cb5a139a1a9c648188f5037a0_images_Organizador_de_escritorio-2be33ec6-0644-4bbe-95f7-75b450a383ce.jpg": "organizador-escritorio",
    "c__Users_Windows_AppData_Roaming_Cursor_User_workspaceStorage_f571ca1cb5a139a1a9c648188f5037a0_images_Memotest__2_-741bf70f-963f-409f-9b0f-0ea2a07c2f9c.jpg": "memotest",
    "c__Users_Windows_AppData_Roaming_Cursor_User_workspaceStorage_f571ca1cb5a139a1a9c648188f5037a0_images_Llaveros-5a60334a-035c-46ee-b19f-bef489878a9a.jpg": "llaveros-moto",
    "c__Users_Windows_AppData_Roaming_Cursor_User_workspaceStorage_f571ca1cb5a139a1a9c648188f5037a0_images_Portacelulares-9731369d-2755-47df-8d5d-5876ba1f20bc.jpg": "portacelulares",
    "c__Users_Windows_AppData_Roaming_Cursor_User_workspaceStorage_f571ca1cb5a139a1a9c648188f5037a0_images_Portallaves__2_-fb8998ee-c3f9-46bc-b5a3-75c08a225234.jpg": "portallaves-familia",
    "c__Users_Windows_AppData_Roaming_Cursor_User_workspaceStorage_f571ca1cb5a139a1a9c648188f5037a0_images_Portacinturones_de_karate-0b580d07-11a0-4974-ada3-0f1a26fa0a25.jpg": "portacinturones",
    "c__Users_Windows_AppData_Roaming_Cursor_User_workspaceStorage_f571ca1cb5a139a1a9c648188f5037a0_images_Porta_sahumerio-3ede29cc-a5cd-40d9-9252-b61ca9d641eb.jpg": "porta-sahumerio",
    "c__Users_Windows_AppData_Roaming_Cursor_User_workspaceStorage_f571ca1cb5a139a1a9c648188f5037a0_images_Portamedallas__2_-86e84b65-0100-4b99-a0e3-cd87b10eb71e.jpg": "portamedallas",
    "c__Users_Windows_AppData_Roaming_Cursor_User_workspaceStorage_f571ca1cb5a139a1a9c648188f5037a0_images_Portallaves-fc9e2dec-8098-43c3-9fc8-bbf85c06b46a.jpg": "portallaves-boca",
    "c__Users_Windows_AppData_Roaming_Cursor_User_workspaceStorage_f571ca1cb5a139a1a9c648188f5037a0_images_Portaretratos__2_-ce5dba35-4be2-4d76-a56a-10c541d2c390.jpg": "portaretratos",
    "c__Users_Windows_AppData_Roaming_Cursor_User_workspaceStorage_f571ca1cb5a139a1a9c648188f5037a0_images_Reglas_personalizadas-605908c7-950d-4aac-a9c0-d9f2af3195e9.jpg": "reglas",
    "c__Users_Windows_AppData_Roaming_Cursor_User_workspaceStorage_f571ca1cb5a139a1a9c648188f5037a0_images_Portasahumerios-5df9bf3e-f2ad-40d4-ba0b-d173a5d4448c.jpg": "portasahumerios",
    "c__Users_Windows_AppData_Roaming_Cursor_User_workspaceStorage_f571ca1cb5a139a1a9c648188f5037a0_images_Tablero_para_pendulo-d6a9116f-3c6c-4e71-a734-fa5b88e707f9.jpg": "tablero-pendulo",
    "c__Users_Windows_AppData_Roaming_Cursor_User_workspaceStorage_f571ca1cb5a139a1a9c648188f5037a0_images_Tapas_para_velas-0dd88f4f-0af4-4bab-aafa-16bf5e147d03.jpg": "tapas-velas",
    "c__Users_Windows_AppData_Roaming_Cursor_User_workspaceStorage_f571ca1cb5a139a1a9c648188f5037a0_images_Trofeo_de_bailarina-f19552ab-0d3e-49a7-a4b5-ec6d8e28d06d.jpg": "trofeo-bailarina",
    "c__Users_Windows_AppData_Roaming_Cursor_User_workspaceStorage_f571ca1cb5a139a1a9c648188f5037a0_images_Trabado-9432492e-3b0e-42e8-a91c-73b773c6098d.jpg": "trabado",
    "c__Users_Windows_AppData_Roaming_Cursor_User_workspaceStorage_f571ca1cb5a139a1a9c648188f5037a0_images_Rompecabezas-8242031f-478a-4d95-80d1-4ad9f7871c5a.jpg": "rompecabezas",
    "c__Users_Windows_AppData_Roaming_Cursor_User_workspaceStorage_f571ca1cb5a139a1a9c648188f5037a0_images_Tateti-e7ee1d20-fe6c-4b43-8e4e-f5a7561961b7.jpg": "tateti",
}

# Cada origen con su destino, que es lo que recorre main().
ORIGENES = (
    (CARPETA_DRIVE, FOTOS, DESTINO),
    (CARPETA_CHAT, FOTOS_CHAT, DESTINO),
    (CARPETA_CHAT, FOTOS_SITIO, DESTINO_SITIO),
    (CARPETA_CHAT, FOTOS_TRABAJOS, DESTINO_TRABAJOS),
)


def copiar_originales() -> None:
    """Guarda una copia local de los originales, fuera del control de versiones."""
    ORIGINALES.mkdir(parents=True, exist_ok=True)
    for carpeta, mapa, _ in ORIGENES:
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


def procesar(origen: Path, nombre_final: str, carpeta: Path = DESTINO) -> str:
    imagen = abrir(origen)

    # Las fotos de celular traen la orientacion en los metadatos EXIF: si no la
    # aplicamos, algunas se ven acostadas.
    imagen = ImageOps.exif_transpose(imagen)

    tiene_transparencia = imagen.mode in ("RGBA", "LA", "P")
    imagen = imagen.convert("RGBA" if tiene_transparencia else "RGB")

    if max(imagen.size) > LADO_MAXIMO:
        imagen.thumbnail((LADO_MAXIMO, LADO_MAXIMO), Image.LANCZOS)

    carpeta.mkdir(parents=True, exist_ok=True)
    if tiene_transparencia:
        destino = carpeta / f"{nombre_final}.png"
        imagen.save(destino, "PNG", optimize=True)
    else:
        destino = carpeta / f"{nombre_final}.jpg"
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

    generar_isotipo(svg, pagina)
    generar_imagen_social(logo)

    documento.close()
    print(f"  logo.svg y logo.png ({logo.size[0]}x{logo.size[1]})")


def generar_isotipo(svg: str, pagina) -> None:
    """Isotipo solo, sin las letras, para el encabezado.

    En chico el logo completo es una manchita ilegible, asi que usamos solo el
    trazo con el destello del laser, que si se reconoce.

    Ojo: esto NO genera el favicon. El de public/ lleva fondo marron para que
    se vea en la pestana del navegador, y se regenera con generar-iconos.mjs.
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
    (LOGOS / "isotipo.svg").write_text(solo_isotipo, encoding="utf-8")
    print("  isotipo.svg")


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
    for carpeta, mapa, destino in ORIGENES:
        for nombre, nombre_final in mapa.items():
            origen = carpeta / nombre
            if not origen.exists():
                origen = ORIGINALES / nombre
            if not origen.exists():
                faltantes.append(nombre)
                continue
            print(f"  {procesar(origen, nombre_final, destino)}")

    print("Generando logo...")
    generar_logo()

    if faltantes:
        print("\nNo encontre estas fotos:")
        for nombre in faltantes:
            print(f"  - {nombre}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
