import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const productos = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/productos' }),
  schema: ({ image }) =>
    z.object({
      nombre: z.string(),
      /** Frase corta para la tarjeta de la grilla. */
      resumen: z.string(),
      /** Menor primero. Manda el orden de la grilla. */
      orden: z.number(),
      /** Los destacados aparecen en la portada. */
      destacado: z.boolean().default(false),

      categoria: z
        .enum(['coleccion', 'materiales', 'personalizados'])
        .default('coleccion'),

      precio: z
        .object({
          /**
           * Una sola opción en la mayoría de los productos. Los posavasos se
           * venden por unidad y por juego, así que llevan varias.
           */
          opciones: z
            .array(
              z.object({
                etiqueta: z.string().optional(),
                monto: z.number(),
              }),
            )
            .min(1),
          cuotas: z.number().optional(),
          transferencia: z
            .object({ monto: z.number(), descuento: z.number() })
            .optional(),
          sena: z.object({ monto: z.number(), porcentaje: z.number() }).optional(),
        })
        .optional(),

      medidas: z.string().optional(),
      incluye: z.array(z.string()).default([]),
      /** Plazo de fabricación, tal como se lo comunica por WhatsApp. */
      entrega: z.string().optional(),

      /** Variantes a elegir: color de mesa, diseño de grabado, lado, etc. */
      opciones: z
        .array(
          z.object({
            titulo: z.string(),
            valores: z.array(z.string()),
            nota: z.string().optional(),
          }),
        )
        .default([]),

      fotos: z
        .array(z.object({ src: image(), alt: z.string() }))
        .min(1),
    }),
});

export const collections = { productos };
