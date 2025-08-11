# Cloudflare Hyperdrive DNS Resolution Issue - Minimal Reproduction for cloudflare/workers-sdk#10320

## Issue Description

When deploying a containerized Python application to Cloudflare Workers that uses psycopg2 to connect to PostgreSQL via Hyperdrive, the connection fails with a DNS resolution error:

```
psycopg2.OperationalError: could not translate host name "66c4c2b923f89002cbc61b8192b83e63.hyperdrive.local" to address: Name or service not known
```

I assume this behaviour would be the same for other languages but havent checked.

## Environment

- **Platform**: Cloudflare Workers with Containers
- **Runtime**: Python 3.13 in container
- **Database Library**: psycopg2-binary 2.9.10
- **Hyperdrive**: Configured and working in non-container deployments

## Steps to Reproduce

1. **Setup Hyperdrive** (if not already done):
   ```bash
   wrangler hyperdrive create test-hyperdrive \
     --connection-string "postgresql://user:pass@your-db-host:5432/dbname"
   ```

2. **Update wrangler.toml** with your Hyperdrive ID:
   ```toml
   [[hyperdrive]]
   binding = "HYPERDRIVE"
   id = "YOUR_HYPERDRIVE_ID"
   ```

3. **Deploy the container**:
   ```bash
   wrangler deploy
   ```

4. **Test the endpoint**:
   ```bash
   curl https://your-worker.workers.dev/test
   ```

## Expected Behavior

The container should successfully connect to PostgreSQL through Hyperdrive, as Cloudflare should handle the special `.hyperdrive.local` hostname internally.

## Actual Behavior

The psycopg2 library attempts to resolve the `.hyperdrive.local` hostname using standard DNS, which fails because of "reasons" i guess.

you could, i suppose, add some manual dns teats too.

This demo will return e.g.

```
{
  "success": false,
  "hyperdrive_url": "postgresql://8227bb2523784c3a8e72d2d5ccea5aff:8e92...",
  "error": "could not translate host name \"7915595237da56712b28f73cfe4f1f6c.hyperdrive.local\" to address: Name or service not known\n",
  "error_type": "psycopg2.OperationalError",
  "traceback": "Traceback (most recent call last):\n  File \"/app/test_connection.py\", line 80, in test_hyperdrive_connection\n    conn = psycopg2.connect(hyperdrive_url)\n  File \"/usr/local/lib/python3.13/site-packages/psycopg2/__init__.py\", line 122, in connect\n    conn = _connect(dsn, connection_factory=connection_factory, **kwasync)\npsycopg2.OperationalError: could not translate host name \"7915595237da56712b28f73cfe4f1f6c.hyperdrive.local\" to address: Name or service not known\n\n",
  "environment_vars": {
    "HYPERDRIVE_CONNECTION_STRING": "postgresql://8227bb2..."
  },
  "headers_received": {}
}
```

## Files in This Repository

- `Dockerfile` - Minimal Python container with psycopg2
- `test_connection.py` - Simple script that attempts database connection
- `wrangler.toml` - Cloudflare Workers configuration
- `src/index.js` - Worker script to route requests to container

## Logs

When the error occurs, you'll see this in the logs:
```
2025-08-11 12:46:57 - ERROR - Error during startup: 
(psycopg2.OperationalError) could not translate host name "66c4c2b923f89002cbc61b8192b83e63.hyperdrive.local" to address: Name or service not known
```
