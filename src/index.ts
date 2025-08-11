// Minimal test for Hyperdrive DNS issue in containers
import { Container } from "@cloudflare/containers";

// Container class that runs the Python test
export class HyperdriveTestBackend extends Container {
  defaultPort = 8000;
  enableInternet = true;

  constructor(state: DurableObjectState, env: Env) {
    super(state, env);
    
    console.log('[Container Constructor] Initializing...');
    console.log(`[Container Constructor] Hyperdrive present: ${!!env.HYPERDRIVE}`);
    
    // Pass Hyperdrive connection string to the container
    this.envVars = {
      ...(env.HYPERDRIVE && { 
        HYPERDRIVE_CONNECTION_STRING: env.HYPERDRIVE.connectionString 
      }),
    };
    
    if (env.HYPERDRIVE?.connectionString) {
      const url = new URL(env.HYPERDRIVE.connectionString);
      console.log(`[Container Constructor] Hyperdrive hostname: ${url.hostname}`);
    }
  }
}

// Main worker
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    
    console.log(`[Worker] Request: ${request.method} ${url.pathname}`);
    console.log(`[Worker] Hyperdrive binding present: ${!!env.HYPERDRIVE}`);
    
    if (url.pathname === '/test') {
      // Get container instance
      const id = env.BACKEND.idFromName("test-instance");
      const backend = env.BACKEND.get(id);
      
      console.log('[Worker] Forwarding to container...');
      return backend.fetch(request);
    }
    
    return new Response('Hyperdrive DNS Test\n\nEndpoint: /test', {
      headers: { 'Content-Type': 'text/plain' }
    });
  },
};

interface Env {
  BACKEND: DurableObjectNamespace;
  HYPERDRIVE?: {
    connectionString: string;
  };
}