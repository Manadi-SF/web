/** Datos de contacto y textos que se repiten en todo el sitio. */

export const SITIO = {
  nombre: 'Manadi',
  bajada: 'Diseño y corte láser',
  descripcion:
    'Diseño, corte y grabado láser en Santa Fe. Mesas materas, decoración, ' +
    'organizadores y productos personalizados en MDF, acrílico y ecocuero.',
  ciudad: 'Santa Fe, Argentina',
  url: 'https://manadi.com.ar',
} as const;

export const CONTACTO = {
  /** Formato internacional sin signos, como lo pide el enlace de WhatsApp. */
  whatsapp: '5493425162793',
  whatsappVisible: '342 516-2793',
  instagram: 'manadi.sf',
  mail: 'manadi.sf@gmail.com',
} as const;

/**
 * Arma el enlace de WhatsApp con el mensaje ya escrito.
 *
 * Que el mensaje venga cargado sirve para dos cosas: le ahorra al cliente
 * tener que explicar qué vio, y del otro lado se sabe de qué producto viene
 * la consulta.
 */
export function enlaceWhatsapp(producto?: string): string {
  const mensaje = producto
    ? `¡Hola Manadi! Me interesa ${producto}. ¿Me pasan más información?`
    : '¡Hola Manadi! Quería hacerles una consulta.';

  return `https://wa.me/${CONTACTO.whatsapp}?text=${encodeURIComponent(mensaje)}`;
}

export const NAVEGACION = [
  { texto: 'Colección', href: '/coleccion' },
  { texto: 'Quiénes somos', href: '/quienes-somos' },
] as const;

/** Precios en pesos, con el formato que se usa en Argentina. */
export function pesos(monto: number): string {
  return `$${monto.toLocaleString('es-AR')}`;
}
