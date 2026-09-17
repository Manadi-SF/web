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

/**
 * Las tres ramas del catalogo, como estaban pensadas desde la nota original:
 * la coleccion propia, los productos agrupados por material y los
 * personalizados.
 *
 * Personalizados todavia no tiene productos cargados. No hace falta hacer
 * nada especial: el menu y el indice muestran solo las ramas que tienen algo,
 * asi que aparece sola el dia que se cargue el primero.
 */
export const RAMAS = {
  coleccion: {
    ruta: '/coleccion',
    titulo: 'Colección Manadi',
    /** Para el menu, donde el titulo completo no entra. */
    corto: 'Colección',
    /** Una linea, para el desplegable del menu. */
    resumen: 'Las piezas que diseñamos nosotros',
    meta:
      'Mesas materas, decoración para la pared, organizadores y más. ' +
      'Piezas diseñadas y cortadas con láser en Santa Fe.',
    intro:
      'Estos son los productos que diseñamos nosotros. Los hacemos a pedido y ' +
      'varios se personalizan: elegís el color, el grabado o le sumamos el ' +
      'nombre que quieras.',
  },
  materiales: {
    ruta: '/materiales',
    titulo: 'Productos por material',
    corto: 'Por material',
    resumen: 'Ecocuero, acrílico y MDF para tu marca',
    meta:
      'Etiquetas de ecocuero y piezas en acrílico y MDF, personalizadas con ' +
      'tu marca. Corte y grabado láser en Santa Fe.',
    intro:
      'Trabajamos el ecocuero, el acrílico y el MDF para otras marcas y ' +
      'proyectos: los cortamos y grabamos con tu logo, tu nombre o el diseño ' +
      'que nos pases.',
  },
  personalizados: {
    ruta: '/personalizados',
    titulo: 'Personalizados',
    corto: 'Personalizados',
    resumen: 'Contanos tu idea y la hacemos',
    meta:
      'Productos hechos a medida con corte y grabado láser en Santa Fe. ' +
      'Contanos tu idea y la diseñamos con vos.',
    intro: 'Contanos qué necesitás y lo diseñamos con vos.',
  },
} as const;

export type Rama = keyof typeof RAMAS;

/** Direccion de la ficha de un producto, segun la rama a la que pertenece. */
export function enlaceProducto(categoria: Rama, id: string): string {
  return `${RAMAS[categoria].ruta}/${id}`;
}

export const NAVEGACION = [
  { texto: 'Quiénes somos', href: '/quienes-somos' },
] as const;

/** Precios en pesos, con el formato que se usa en Argentina. */
export function pesos(monto: number): string {
  return `$${monto.toLocaleString('es-AR')}`;
}
