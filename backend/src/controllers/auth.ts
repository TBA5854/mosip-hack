import { prisma } from '../utils/prisma';
import { hashPassword, comparePassword } from '../utils/auth';

export const register = async ({ body, set }: any) => {
  const { username, password } = body;

  const existingUser = await prisma.user.findUnique({
    where: { username },
  });

  if (existingUser) {
    set.status = 400;
    return { error: 'Username already exists' };
  }

  const hashedPassword = await hashPassword(password);

  const user = await prisma.user.create({
    data: {
      username,
      password: hashedPassword,
    },
  });

  return { id: user.id, username: user.username };
};

export const login = async ({ body, jwt, set }: any) => {
  const { username, password } = body;

  const user = await prisma.user.findUnique({
    where: { username },
  });

  if (!user) {
    set.status = 400;
    return { error: 'Invalid credentials' };
  }

  const isMatch = await comparePassword(password, user.password);

  if (!isMatch) {
    set.status = 400;
    return { error: 'Invalid credentials' };
  }

  const token = await jwt.sign({
    id: user.id,
    username: user.username,
  });

  return { token };
};
