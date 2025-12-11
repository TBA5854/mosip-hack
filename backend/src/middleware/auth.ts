import { Elysia } from 'elysia';
import { jwt } from '@elysiajs/jwt';

export const jwtSetup = (app: Elysia) =>
  app.use(
    jwt({
      name: 'jwt',
      secret: process.env.JWT_SECRET || 'secret',
    })
  );

export const authMiddleware = (app: Elysia) =>
  app
    .use(jwtSetup)
    .derive(async ({ jwt, headers, set }) => {
      const authHeader = headers['authorization'];
      if (!authHeader) {
        set.status = 401;
        throw new Error('Unauthorized');
      }
      const token = authHeader.split(' ')[1];
      const profile = await jwt.verify(token);
      if (!profile) {
        set.status = 401;
        throw new Error('Unauthorized');
      }
      return { userId: profile.id };
    });
