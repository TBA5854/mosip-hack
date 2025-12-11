import { Elysia } from 'elysia';
import { registerSchema, loginSchema } from '../models/auth';
import * as authController from '../controllers/auth';
import { jwtSetup } from '../middleware/auth';

export const authRoutes = (app: Elysia) =>
  app
    .use(jwtSetup)
    .group('/auth', (app) =>
      app
        .post('/register', authController.register, {
          body: registerSchema,
        })
        .post('/login', authController.login, {
          body: loginSchema,
        })
    );
