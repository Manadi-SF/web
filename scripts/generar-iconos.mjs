/**
 * Genera los iconos PNG a partir de public/favicon.svg.
 *
 * El SVG alcanza para los navegadores modernos, pero Safari viejo y el "agregar
 * a pantalla de inicio" de iOS solo leen PNG, asi que los dejamos escritos en
 * public/. Correr con: node scripts/generar-iconos.mjs
 */
import sharp from 'sharp';
import { readFileSync, writeFileSync } from 'node:fs';

const svg = readFileSync('public/favicon.svg', 'utf8');

// iOS recorta el icono con su propia mascara, asi que va sin esquinas redondeadas.
const svgCuadrado = svg.replace(' rx="13"', '');

const iconos = [
  { archivo: 'public/favicon-96.png', tamano: 96, fuente: svg },
  { archivo: 'public/apple-touch-icon.png', tamano: 180, fuente: svgCuadrado },
];

for (const { archivo, tamano, fuente } of iconos) {
  const png = await sharp(Buffer.from(fuente), { density: 900 })
    .resize(tamano, tamano)
    .png()
    .toBuffer();
  writeFileSync(archivo, png);
  console.log(`${archivo} (${tamano}x${tamano})`);
}
