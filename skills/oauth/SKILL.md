---
name: OAuth Authentication
description: OAuth 2.0 and OIDC implementation best practices for secure authentication and authorization
version: 1.0.0
triggers:
  - oauth
  - oauth2
  - oidc
  - openid connect
  - jwt
  - access token
  - refresh token
  - authorization code
  - client credentials
---

# OAuth Authentication Skill

This skill automatically activates when implementing OAuth 2.0 or OpenID Connect to ensure secure authentication patterns and proper flow selection.

## Core Principle

**SECURE, STANDARDS-COMPLIANT AUTHENTICATION**

```
❌ Implicit flow, storing tokens insecurely, mixing auth patterns
✅ Authorization Code + PKCE, secure token storage, proper scope management
```

## OAuth 2.0 Flow Selection

```
FLOW SELECTION GUIDE
════════════════════════════════════════════════════════════

CLIENT TYPE           │ RECOMMENDED FLOW
──────────────────────┼────────────────────────────────────
Web App (server)      │ Authorization Code
SPA (browser)         │ Authorization Code + PKCE
Mobile App            │ Authorization Code + PKCE
CLI/Desktop           │ Authorization Code + PKCE (or Device)
Server-to-Server      │ Client Credentials
IoT/Limited Input     │ Device Authorization

❌ DEPRECATED FLOWS
├── Implicit Flow (use Auth Code + PKCE instead)
└── Resource Owner Password (except legacy migration)
```

## Authorization Code Flow with PKCE

```typescript
// Frontend: Initiate OAuth flow
function initiateOAuthFlow(): void {
  // Generate PKCE challenge
  const codeVerifier = generateRandomString(64);
  const codeChallenge = await sha256(codeVerifier);

  // Store verifier for later
  sessionStorage.setItem('code_verifier', codeVerifier);

  // Build authorization URL
  const params = new URLSearchParams({
    client_id: CLIENT_ID,
    redirect_uri: REDIRECT_URI,
    response_type: 'code',
    scope: 'openid profile email',
    state: generateRandomString(32),
    code_challenge: codeChallenge,
    code_challenge_method: 'S256',
  });

  window.location.href = `${AUTH_SERVER}/authorize?${params}`;
}

// Backend: Exchange code for tokens
async function exchangeCodeForTokens(
  code: string,
  codeVerifier: string
): Promise<TokenResponse> {
  const response = await fetch(`${AUTH_SERVER}/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      grant_type: 'authorization_code',
      code,
      redirect_uri: REDIRECT_URI,
      client_id: CLIENT_ID,
      client_secret: CLIENT_SECRET, // Only for confidential clients
      code_verifier: codeVerifier,
    }),
  });

  if (!response.ok) {
    throw new OAuthError('Token exchange failed');
  }

  return response.json();
}
```

## Token Management

```typescript
// Secure token storage
interface TokenStorage {
  // Server-side: HTTP-only cookies
  setTokens(accessToken: string, refreshToken: string): void;

  // Get access token (from memory for SPAs)
  getAccessToken(): string | null;

  // Refresh tokens before expiration
  refreshTokens(): Promise<void>;

  // Clear on logout
  clearTokens(): void;
}

// Token refresh with rotation
async function refreshAccessToken(): Promise<string> {
  const refreshToken = getRefreshToken();

  const response = await fetch(`${AUTH_SERVER}/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      grant_type: 'refresh_token',
      refresh_token: refreshToken,
      client_id: CLIENT_ID,
    }),
  });

  if (response.status === 401) {
    // Refresh token expired or revoked
    await logout();
    throw new SessionExpiredError();
  }

  const tokens = await response.json();

  // Store new refresh token (rotation)
  if (tokens.refresh_token) {
    storeRefreshToken(tokens.refresh_token);
  }

  return tokens.access_token;
}
```

## JWT Validation

```typescript
import jwt from 'jsonwebtoken';
import jwksClient from 'jwks-rsa';

// JWKS client for key rotation
const client = jwksClient({
  jwksUri: `${AUTH_SERVER}/.well-known/jwks.json`,
  cache: true,
  cacheMaxEntries: 5,
  cacheMaxAge: 600000, // 10 minutes
});

async function validateAccessToken(token: string): Promise<JWTPayload> {
  // Decode header to get key ID
  const decoded = jwt.decode(token, { complete: true });
  if (!decoded || !decoded.header.kid) {
    throw new InvalidTokenError('Invalid token structure');
  }

  // Get signing key
  const key = await client.getSigningKey(decoded.header.kid);
  const publicKey = key.getPublicKey();

  // Verify token
  try {
    const payload = jwt.verify(token, publicKey, {
      algorithms: ['RS256'],
      issuer: AUTH_SERVER,
      audience: CLIENT_ID,
    });

    return payload as JWTPayload;
  } catch (error) {
    if (error instanceof jwt.TokenExpiredError) {
      throw new TokenExpiredError();
    }
    throw new InvalidTokenError('Token validation failed');
  }
}

// Required claims validation
function validateClaims(payload: JWTPayload): void {
  const now = Math.floor(Date.now() / 1000);

  // Check expiration
  if (!payload.exp || payload.exp < now) {
    throw new TokenExpiredError();
  }

  // Check not-before
  if (payload.nbf && payload.nbf > now) {
    throw new InvalidTokenError('Token not yet valid');
  }

  // Check issued-at (not too old)
  if (payload.iat && payload.iat < now - 86400) {
    throw new InvalidTokenError('Token too old');
  }

  // Check required scopes
  const scopes = payload.scope?.split(' ') || [];
  if (!scopes.includes('openid')) {
    throw new InvalidTokenError('Missing openid scope');
  }
}
```

## Scope Management

```typescript
// Define scopes
const SCOPES = {
  // OpenID Connect
  openid: 'Required for OIDC',
  profile: 'Basic profile info',
  email: 'Email address',

  // API scopes
  'read:users': 'Read user data',
  'write:users': 'Modify user data',
  'admin': 'Administrative access',
};

// Request minimum required scopes
function getRequiredScopes(operation: string): string[] {
  const scopeMap: Record<string, string[]> = {
    login: ['openid', 'profile', 'email'],
    readProfile: ['openid', 'profile'],
    updateProfile: ['openid', 'profile', 'write:users'],
    adminDashboard: ['openid', 'admin'],
  };

  return scopeMap[operation] || ['openid'];
}

// Validate scopes on protected endpoints
function requireScopes(...requiredScopes: string[]) {
  return (req: Request, res: Response, next: NextFunction) => {
    const tokenScopes = req.user?.scope?.split(' ') || [];

    const hasAllScopes = requiredScopes.every(
      scope => tokenScopes.includes(scope)
    );

    if (!hasAllScopes) {
      return res.status(403).json({
        error: 'insufficient_scope',
        required_scopes: requiredScopes,
      });
    }

    next();
  };
}
```

## Security Patterns

```typescript
// State parameter for CSRF protection
function generateState(): { state: string; nonce: string } {
  const state = crypto.randomBytes(32).toString('base64url');
  const nonce = crypto.randomBytes(32).toString('base64url');

  // Store for validation
  sessionStorage.setItem('oauth_state', state);
  sessionStorage.setItem('oauth_nonce', nonce);

  return { state, nonce };
}

function validateCallback(callbackState: string): void {
  const storedState = sessionStorage.getItem('oauth_state');

  if (!storedState || storedState !== callbackState) {
    throw new SecurityError('State mismatch - possible CSRF attack');
  }

  sessionStorage.removeItem('oauth_state');
}

// Secure cookie settings for tokens
const COOKIE_OPTIONS = {
  httpOnly: true,     // Prevent XSS access
  secure: true,       // HTTPS only
  sameSite: 'lax',    // CSRF protection
  path: '/',
  maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days for refresh
};

// Token binding (DPoP)
async function createDPoPProof(
  method: string,
  url: string,
  accessToken?: string
): Promise<string> {
  const header = {
    typ: 'dpop+jwt',
    alg: 'ES256',
    jwk: await getPublicKey(),
  };

  const payload = {
    jti: crypto.randomUUID(),
    htm: method,
    htu: url,
    iat: Math.floor(Date.now() / 1000),
    ...(accessToken && { ath: await sha256(accessToken) }),
  };

  return signJWT(header, payload);
}
```

## OAuth Checklist

```
📋 OAuth Security Checklist

□ FLOW SELECTION
  □ Authorization Code for web apps
  □ PKCE for public clients (SPAs, mobile)
  □ No Implicit flow
  □ Client Credentials for M2M only

□ TOKEN SECURITY
  □ Short-lived access tokens (15min-1hr)
  □ Refresh token rotation
  □ HTTP-only cookies for web
  □ Secure storage for mobile

□ VALIDATION
  □ Verify JWT signature
  □ Validate issuer and audience
  □ Check expiration
  □ Validate state parameter

□ PROTECTION
  □ PKCE (code_challenge/verifier)
  □ State parameter for CSRF
  □ Nonce for replay protection
  □ Secure redirect URIs only
```

## Warning Triggers

Automatically warn when:

1. **Implicit flow usage**
   > "⚠️ OAUTH: Implicit flow is deprecated - use Authorization Code + PKCE"

2. **Missing PKCE**
   > "⚠️ OAUTH: Public clients MUST use PKCE"

3. **Token in URL**
   > "⚠️ OAUTH: Never pass tokens in URL parameters"

4. **Insecure storage**
   > "⚠️ OAUTH: Use HTTP-only cookies or secure storage for tokens"
