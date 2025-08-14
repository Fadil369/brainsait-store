// BrainSAIT API Gateway - Cloudflare Worker
// Multi-tenant routing with LinkedIn Lead webhooks and Zapier webhook support

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    const corsHeaders = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
      "Access-Control-Allow-Headers":
        "Content-Type, Authorization, X-Tenant-ID",
    };

    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders });
    }

    const clientIP = request.headers.get("CF-Connecting-IP") || "0.0.0.0";

    try {
      // Simple rate limiting via KV
      const rateKey = `rate:${clientIP}:${new Date().getUTCMinutes()}`;
      const count =
        parseInt((await env.RATE_LIMIT.get(rateKey)) || "0", 10) + 1;
      if (count > 120) {
        return json({ error: "Rate limit exceeded" }, 429, corsHeaders);
      }
      await env.RATE_LIMIT.put(rateKey, String(count), { expirationTtl: 120 });

      const tenantId = request.headers.get("X-Tenant-ID") || "default";

      // Webhooks: LinkedIn Lead Notifications
      if (url.pathname === "/webhooks/linkedin/lead-notifications") {
        return await handleLinkedInLeadWebhook(request, env, corsHeaders);
      }

      // Webhooks: Zapier (placeholder)
      if (url.pathname.startsWith("/webhooks/zapier")) {
        return await handleZapierWebhook(request, env, corsHeaders);
      }

      // Proxy API to backend
      if (url.pathname.startsWith("/api/v1")) {
        return await routeToBackend(request, tenantId, env, corsHeaders);
      }

      // Health check endpoint
      if (url.pathname === "/health") {
        return json(
          {
            status: "healthy",
            version: "1.0.0",
            environment: env.ENVIRONMENT || "development",
            timestamp: new Date().toISOString(),
            services: {
              gateway: "operational",
              backend: env.BACKEND_BASE_URL ? "configured" : "not_configured",
              kv_storage: env.RATE_LIMIT ? "operational" : "not_configured",
              document_storage: env.DOCUMENTS ? "operational" : "not_configured"
            }
          },
          200,
          corsHeaders
        );
      }

      return json(
        {
          message: "BrainSAIT Store API Gateway",
          version: "1.0.0",
          status: "operational",
          endpoints: {
            health: "/health",
            linkedinLeadWebhook: "/webhooks/linkedin/lead-notifications",
            storeAPI: "/api/v1/store",
            paymentsAPI: "/api/v1/payments", 
            oidAPI: "/api/v1/oid",
            documentation: "/api/docs"
          },
          features: {
            multiTenant: true,
            bilingual: true,
            rateLimiting: true,
            paymentProcessing: ["stripe", "mada", "stc_pay"],
            oidIntegration: true,
            zatcaCompliant: true
          }
        },
        200,
        corsHeaders
      );
    } catch (err) {
      try {
        env.ANALYTICS &&
          env.ANALYTICS.writeDataPoint({
            blobs: ["error", err?.message || String(err)],
            doubles: [Date.now()],
            indexes: [clientIP],
          });
      } catch (_) {}
      return json({ error: "Internal server error" }, 500, corsHeaders);
    }
  },
};

async function handleLinkedInLeadWebhook(request, env, corsHeaders) {
  const secret = env.LINKEDIN_WEBHOOK_SECRET || env.LINKEDIN_CLIENT_SECRET;
  if (!secret) {
    return json({ error: "Webhook secret not configured" }, 500, corsHeaders);
  }

  const raw = await request.clone().arrayBuffer();
  const signature =
    request.headers.get("x-li-signature") ||
    request.headers.get("X-LI-Signature");
  if (!(await verifyLinkedInSignature(raw, secret, signature))) {
    return json({ error: "Unauthorized" }, 401, corsHeaders);
  }

  const bodyText = new TextDecoder().decode(raw);
  let payload;
  try {
    payload = JSON.parse(bodyText);
  } catch (_) {
    payload = { raw: bodyText };
  }

  const ts = new Date().toISOString().replace(/[:.]/g, "-");
  const key = `linkedin/lead-notifications/${ts}.json`;
  try {
    if (env.DOCUMENTS) {
      await env.DOCUMENTS.put(key, JSON.stringify(payload));
    }
  } catch (_) {}

  try {
    if (env.WEBHOOK_QUEUE) {
      await env.WEBHOOK_QUEUE.send({
        source: "linkedin",
        type: "lead-notifications",
        payload,
        key,
      });
    }
  } catch (_) {}

  // Forward to backend for processing
  const backend =
    env.BACKEND_BASE_URL ||
    (env.ENVIRONMENT === "production"
      ? "https://api-internal.brainsait.com"
      : "http://localhost:8000");
  try {
    await fetch(
      `${backend}/api/v1/integrations/linkedin/webhooks/lead-notifications`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }
    );
  } catch (_) {}

  return json({ ok: true, id: key }, 200, corsHeaders);
}

async function verifyLinkedInSignature(rawBody, secret, signature) {
  if (!signature) return false;
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey(
    "raw",
    enc.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );
  const sig = await crypto.subtle.sign("HMAC", key, rawBody);
  // LinkedIn uses base64-encoded HMAC SHA-256
  const expected = btoa(String.fromCharCode(...new Uint8Array(sig)));
  return timingSafeEqual(expected, signature);
}

function timingSafeEqual(a, b) {
  if (typeof a !== "string" || typeof b !== "string") return false;
  const aBytes = new TextEncoder().encode(a);
  const bBytes = new TextEncoder().encode(b);
  if (aBytes.length !== bBytes.length) return false;
  let res = 0;
  for (let i = 0; i < aBytes.length; i++) {
    res |= aBytes[i] ^ bBytes[i];
  }
  return res === 0;
}

async function handleZapierWebhook(request, env, corsHeaders) {
  const body = await request.json().catch(() => ({}));
  const ts = new Date().toISOString().replace(/[:.]/g, "-");
  const key = `zapier/${ts}.json`;
  try {
    if (env.DOCUMENTS) {
      await env.DOCUMENTS.put(key, JSON.stringify(body));
    }
  } catch (_) {}
  return json({ ok: true, id: key }, 200, corsHeaders);
}

async function routeToBackend(request, tenantId, env, corsHeaders) {
  const backend =
    env.BACKEND_BASE_URL ||
    (env.ENVIRONMENT === "production"
      ? "https://api-internal.brainsait.com"
      : "http://localhost:8000");
  const url = new URL(request.url);
  const headers = new Headers(request.headers);
  headers.set("X-Tenant-ID", tenantId);
  const proxied = new Request(`${backend}${url.pathname}${url.search}`, {
    method: request.method,
    headers,
    body: ["GET", "HEAD"].includes(request.method) ? undefined : request.body,
    redirect: "follow",
  });
  const resp = await fetch(proxied);
  const respHeaders = new Headers(resp.headers);
  for (const [k, v] of Object.entries(corsHeaders)) respHeaders.set(k, v);
  return new Response(resp.body, { status: resp.status, headers: respHeaders });
}

function json(obj, status = 200, extraHeaders = {}) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "Content-Type": "application/json", ...extraHeaders },
  });
}

// Durable Object placeholder (optional)
export class TenantRouter {
  constructor(state, env) {
    this.state = state;
    this.env = env;
  }
  async fetch(request) {
    return new Response("OK");
  }
}
