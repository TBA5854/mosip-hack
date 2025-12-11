import { Elysia, t } from 'elysia';
import { saveOCRSchema } from '../models/ocr';
import * as ocrController from '../controllers/ocr';
import { authMiddleware } from '../middleware/auth';

export const ocrRoutes = (app: Elysia) =>
  app
    .group('/ocr', (app) =>
      app
        .use(authMiddleware)
        .post('/extract', ocrController.extract, {
          body: t.Object({
            file: t.File(),
          }),
        })
        .post('/cache', ocrController.cache, {
          body: saveOCRSchema,
        })
        .get('/:imageHash', ocrController.getCache)
    );
