// Cloudflare Workers API Gateway for BrainSAIT Store
// This worker acts as an API gateway and proxy to the main FastAPI backend

import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { HTTPException } from 'hono/http-exception';

const app = new Hono();

// CORS configuration
app.use('*', cors({
  origin: ['https://store.brainsait.io', 'https://staging-store.brainsait.io'],
  allowMethods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
  allowHeaders: ['Content-Type', 'Authorization', 'X-Tenant-ID'],
  exposeHeaders: ['X-Total-Count', 'X-Rate-Limit-Remaining'],
  credentials: true,
}));

// Rate limiting using KV
async function rateLimit(c, key, limit = 100, window = 60) {
  const now = Math.floor(Date.now() / 1000);
  const windowStart = now - (now % window);
  const rateLimitKey = `rate_limit:${key}:${windowStart}`;
  
  const current = await c.env.RATE_LIMIT.get(rateLimitKey);
  const count = current ? parseInt(current) : 0;
  
  if (count >= limit) {
    throw new HTTPException(429, { message: 'Rate limit exceeded' });
  }
  
  await c.env.RATE_LIMIT.put(rateLimitKey, (count + 1).toString(), { expirationTtl: window });
  
  c.header('X-Rate-Limit-Remaining', (limit - count - 1).toString());
  c.header('X-Rate-Limit-Limit', limit.toString());
}

// Health check endpoint
app.get('/health', async (c) => {
  return c.json({
    status: 'healthy',
    version: '1.0.0',
    environment: c.env.ENVIRONMENT || 'production',
    worker: 'brainsait-store-api',
    timestamp: new Date().toISOString()
  });
});

// Basic store info endpoint
app.get('/api/v1/store/info', async (c) => {
  const clientIP = c.req.header('CF-Connecting-IP') || 'unknown';
  await rateLimit(c, clientIP);
  
  return c.json({
    store_name: 'BrainSAIT Store',
    supported_languages: ['en', 'ar'],
    supported_currencies: ['USD', 'SAR'],
    payment_methods: ['stripe', 'paypal', 'apple_pay', 'mada'],
    features: {
      multi_language: true,
      apple_pay: true,
      real_time_inventory: true,
      mobile_optimized: true
    }
  });
});

// Proxy requests to main FastAPI backend
app.all('/api/*', async (c) => {
  const clientIP = c.req.header('CF-Connecting-IP') || 'unknown';
  await rateLimit(c, clientIP);
  
  const backendUrl = c.env.BACKEND_BASE_URL || 'https://backend.brainsait.io';
  const url = new URL(c.req.url);
  const proxyUrl = `${backendUrl}${url.pathname}${url.search}`;
  
  // Forward headers
  const headers = new Headers();
  c.req.header('Authorization') && headers.set('Authorization', c.req.header('Authorization'));
  c.req.header('Content-Type') && headers.set('Content-Type', c.req.header('Content-Type'));
  c.req.header('X-Tenant-ID') && headers.set('X-Tenant-ID', c.req.header('X-Tenant-ID'));
  c.req.header('Accept-Language') && headers.set('Accept-Language', c.req.header('Accept-Language'));
  
  // Add Cloudflare specific headers
  headers.set('CF-Connecting-IP', clientIP);
  headers.set('CF-Ray', c.req.header('CF-Ray') || '');
  headers.set('CF-Worker', 'brainsait-store-api');
  
  try {
    const response = await fetch(proxyUrl, {
      method: c.req.method,
      headers,
      body: c.req.method !== 'GET' && c.req.method !== 'HEAD' ? await c.req.text() : undefined,
    });
    
    // Forward response headers
    const responseHeaders = new Headers();
    response.headers.forEach((value, key) => {
      if (!key.toLowerCase().startsWith('cf-') && key.toLowerCase() !== 'server') {
        responseHeaders.set(key, value);
      }
    });
    
    // Add cache headers for GET requests
    if (c.req.method === 'GET') {
      responseHeaders.set('Cache-Control', 'public, max-age=300');
    }
    
    return new Response(response.body, {
      status: response.status,
      headers: responseHeaders,
    });
  } catch (error) {
    console.error('Proxy error:', error);
    throw new HTTPException(502, { message: 'Backend service unavailable' });
  }
});

// Apple Pay domain verification
app.get('/.well-known/apple-developer-merchantid-domain-association*', async (c) => {
  const domainAssociation = `
7B227073704944223A2236443346333342524554375A46575855374E58494A4A4948464D4C4D5A474535595142563347474E5A475543414B554E4951222C2276657273696F6E223A312C22637265617465644F6E223A313634313734313033333530332C227369676E6174757265223A2233303435303232313030393141373441444636463341383734453242453841353245374431443030343442463431354532304331444138373330334146343444393144463845424544434532353237323144353132443836424645323232303932453744463444424346334545303032333633303236454444393530303433363931303737353231323743373341364135423235333137303437454644393737443332424439463445313243354530374232384636333131464638334143464538453938333841303330304637413846324539393346463341444246383444463045453632363937374533363633364544463246313433364130424332383145364635393541464238353336353631384245323238364331383835453534463644394231463342373345394635384642373439373231334630434437413531434334383530384538373535424530383142364331373831454634423036463730373632453344374336334242333741353642433031464234313243334331464143464143373030343632423035223A
`.trim();
  
  c.header('Content-Type', 'text/plain');
  c.header('Cache-Control', 'public, max-age=86400');
  return c.text(domainAssociation);
});

// Analytics endpoint
app.post('/api/v1/analytics/event', async (c) => {
  const clientIP = c.req.header('CF-Connecting-IP') || 'unknown';
  await rateLimit(c, clientIP, 1000); // Higher limit for analytics
  
  try {
    const event = await c.req.json();
    
    // Store analytics data in Analytics Engine if available
    if (c.env.ANALYTICS) {
      const datapoint = {
        blobs: [event.type, event.page, clientIP],
        doubles: [1], // count
        indexes: [event.timestamp || Date.now()]
      };
      
      c.env.ANALYTICS.writeDataPoint(datapoint);
    }
    
    return c.json({ success: true });
  } catch (error) {
    console.error('Analytics error:', error);
    return c.json({ success: false, error: 'Invalid event data' }, 400);
  }
});

// Default 404 handler
app.notFound((c) => {
  return c.json({ 
    error: 'Not Found',
    message: 'The requested resource was not found',
    worker: 'brainsait-store-api'
  }, 404);
});

// Error handler
app.onError((err, c) => {
  console.error('Worker error:', err);
  
  if (err instanceof HTTPException) {
    return c.json({ 
      error: err.message,
      status: err.status 
    }, err.status);
  }
  
  return c.json({ 
    error: 'Internal Server Error',
    message: 'An unexpected error occurred'
  }, 500);
});

export default app;