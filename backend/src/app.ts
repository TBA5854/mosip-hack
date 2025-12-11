import { Elysia } from "elysia";
import { cors } from "@elysiajs/cors";
import { authRoutes } from "./routes/auth";
import { ocrRoutes } from "./routes/ocr";

export const app = new Elysia()
  .use(cors({
    origin: process.env.FRONTEND_URL || 'http://localhost:5173'
  }))
  .use(authRoutes)
  .use(ocrRoutes)
  .get("/", () => "Hello Elysia");
