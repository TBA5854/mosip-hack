import { prisma } from '../utils/prisma';

export const extract = async ({ body, userId, set }: any) => {
  const file = body.file;
  
  if (!file) {
    set.status = 400;
    return { error: 'No file provided' };
  }

  try {
    // Create FormData for the Python service
    const formData = new FormData();
    formData.append('file', file);
    formData.append('include_quality_score', 'true');

    // Forward to Python OCR Service
    const ocrUrl = process.env.OCR_SERVICE_URL || 'http://localhost:8000';
    const pythonResponse = await fetch(`${ocrUrl}/api/extract`, {
      method: 'POST',
      body: formData,
    });

    if (!pythonResponse.ok) {
      const errorText = await pythonResponse.text();
      throw new Error(`OCR Service failed: ${errorText}`);
    }

    const result = await pythonResponse.json();

    // Generate hash for the file to use as imageHash
    const arrayBuffer = await file.arrayBuffer();
    const hashBuffer = await crypto.subtle.digest('SHA-256', arrayBuffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const imageHash = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');

    // Cache the result
    await prisma.oCRCache.create({
      data: {
        imageHash,
        ocrText: JSON.stringify(result.extracted_fields),
        userId: Number(userId),
      },
    });

    return { ...result, imageHash };
  } catch (error) {
    console.error('OCR Error:', error);
    set.status = 500;
    return { error: 'Failed to process OCR' };
  }
};

export const cache = async ({ body, userId }: any) => {
  const { imageHash, ocrText, userEdits } = body;

  const cached = await prisma.oCRCache.create({
    data: {
      imageHash,
      ocrText,
      userEdits,
      userId: Number(userId),
    },
  });

  return cached;
};

export const getCache = async ({ params: { imageHash }, userId }: any) => {
  const cached = await prisma.oCRCache.findFirst({
    where: {
      imageHash,
      userId: Number(userId),
    },
  });

  return cached || { found: false };
};
