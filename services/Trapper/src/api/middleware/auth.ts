import { FastifyRequest, FastifyReply, HookHandlerDoneFunction } from 'fastify';
import { timingSafeEqual } from 'crypto';
import config from '../../config';

export async function apiKeyAuth(
  request: FastifyRequest,
  reply: FastifyReply,
  done: HookHandlerDoneFunction
) {
  const authHeader = request.headers.authorization;

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    reply.code(401).send({
      success: false,
      error: 'Missing or invalid Authorization header. Use: Authorization: Bearer <key>',
    });
    return;
  }

  const providedKey = authHeader.slice(7);

  // Use constant-time comparison to prevent timing attacks.
  // Pad the shorter buffer to avoid leaking the key length via timing differences.
  try {
    const a = Buffer.from(providedKey);
    const b = Buffer.from(config.apiKey);
    const maxLen = Math.max(a.length, b.length);
    const aPadded = Buffer.alloc(maxLen, 0);
    const bPadded = Buffer.alloc(maxLen, 0);
    a.copy(aPadded);
    b.copy(bPadded);
    if (!timingSafeEqual(aPadded, bPadded)) {
      reply.code(401).send({
        success: false,
        error: 'Invalid API key',
      });
      return;
    }
  } catch {
    reply.code(401).send({
      success: false,
      error: 'Invalid API key',
    });
    return;
  }

  done();
}
