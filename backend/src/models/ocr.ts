import { z } from 'zod';

export const saveOCRSchema = z.object({
  imageHash: z.string(),
  ocrText: z.string(),
  userEdits: z.string().optional(),
});

export const updateOCRSchema = z.object({
  userEdits: z.string(),
});

export type SaveOCRDTO = z.infer<typeof saveOCRSchema>;
export type UpdateOCRDTO = z.infer<typeof updateOCRSchema>;
