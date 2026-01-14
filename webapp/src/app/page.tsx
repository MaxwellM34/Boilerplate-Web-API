"use client";

import Script from "next/script";
import { useCallback, useEffect, useRef, useState } from "react";

type GoogleCredentialResponse = {
  credential?: string;
};

type ApiUser = {
  email: string;
  firstname: string;
  lastname?: string | null;
  is_admin?: boolean;
};

type TokenResponse = {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: ApiUser;
};

declare global {
  interface Window {
    google?: {
      accounts?: {
        id?: {
          initialize: (options: {
            client_id: string;
            callback: (response: GoogleCredentialResponse) => void;
            auto_select?: boolean;
            cancel_on_tap_outside?: boolean;
          }) => void;
          renderButton: (
            parent: HTMLElement,
            options?: {
              theme?: "outline" | "filled_blue" | "filled_black";
              size?: "large" | "medium" | "small";
              shape?: "rectangular" | "pill" | "circle" | "square";
              text?: "signin_with" | "signup_with" | "continue_with" | "signin";
              width?: number;
            }
          ) => void;
          prompt: () => void;
        };
      };
    };
  }
}

const apiBaseUrl = (
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"
).replace(/\/$/, "");
const googleClientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "";

const formatDuration = (seconds: number) => {
  if (seconds <= 0) {
    return "expired";
  }
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  if (hours > 0) {
    return `${hours}h ${minutes % 60}m`;
  }
  return `${minutes}m`;
};

export default function HomePage() {
  const googleButtonRef = useRef<HTMLDivElement | null>(null);
  const [scriptReady, setScriptReady] = useState(false);
  const [statusTone, setStatusTone] = useState<
    "idle" | "loading" | "success" | "error"
  >("idle");
  const [statusMessage, setStatusMessage] = useState(
    "Waiting for Google sign-in."
  );
  const [token, setToken] = useState<string | null>(null);
  const [expiresIn, setExpiresIn] = useState<number | null>(null);
  const [user, setUser] = useState<ApiUser | null>(null);
  const [copied, setCopied] = useState(false);

  const handleCredential = useCallback(
    async (response: GoogleCredentialResponse) => {
      if (!response.credential) {
        setStatusTone("error");
        setStatusMessage("Google did not return a credential.");
        return;
      }

      setStatusTone("loading");
      setStatusMessage("Verifying Google token with the API...");
      setCopied(false);

      try {
        const apiResponse = await fetch(`${apiBaseUrl}/api/auth/google`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ id_token: response.credential }),
          cache: "no-store",
        });

        if (!apiResponse.ok) {
          const message = await apiResponse.text();
          throw new Error(
            message || `Token exchange failed (${apiResponse.status})`
          );
        }

        const data = (await apiResponse.json()) as TokenResponse;
        setToken(data.access_token);
        setUser(data.user);
        setExpiresIn(data.expires_in);
        localStorage.setItem("betterbmr_jwt", data.access_token);

        const healthResponse = await fetch(`${apiBaseUrl}/health`, {
          headers: { Authorization: `Bearer ${data.access_token}` },
          cache: "no-store",
        });

        if (!healthResponse.ok) {
          setStatusTone("error");
          setStatusMessage("JWT saved, but /health did not accept it.");
          return;
        }

        setStatusTone("success");
        setStatusMessage(`Signed in as ${data.user.email}.`);
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "Login failed.";
        setStatusTone("error");
        setStatusMessage(message);
      }
    },
    []
  );

  useEffect(() => {
    if (!scriptReady) {
      return;
    }
    if (!googleClientId) {
      setStatusTone("error");
      setStatusMessage("Missing NEXT_PUBLIC_GOOGLE_CLIENT_ID.");
      return;
    }

    const googleId = window.google?.accounts?.id;
    if (!googleId || !googleButtonRef.current) {
      setStatusTone("error");
      setStatusMessage("Google sign-in is not available.");
      return;
    }

    googleId.initialize({
      client_id: googleClientId,
      callback: handleCredential,
      auto_select: false,
      cancel_on_tap_outside: false,
    });

    if (googleButtonRef.current.childElementCount === 0) {
      googleId.renderButton(googleButtonRef.current, {
        theme: "outline",
        size: "large",
        shape: "pill",
        text: "continue_with",
        width: 320,
      });
    }
  }, [scriptReady, handleCredential]);

  const handleCopy = useCallback(async () => {
    if (!token) {
      return;
    }
    try {
      await navigator.clipboard.writeText(token);
      setCopied(true);
    } catch {
      setCopied(false);
    }
  }, [token]);

  return (
    <main className="page">
      <Script
        src="https://accounts.google.com/gsi/client"
        strategy="afterInteractive"
        onLoad={() => setScriptReady(true)}
      />
      <div className="shell">
        <section className="hero">
          <span className="badge fade-up">BetterBMR</span>
          <h1 className="hero-title fade-up delay-1">
            Turn daily metabolism into a plan you can trust.
          </h1>
          <p className="hero-subtitle fade-up delay-2">
            Sign in with Google to pull a JWT, then use it on every API request
            without storing anything on disk.
          </p>
          <div className="hero-grid fade-up delay-3">
            <div className="stat-card">
              <p className="stat-label">Step 1</p>
              <p className="stat-value">Google login</p>
              <p className="stat-detail">Get a verified ID token.</p>
            </div>
            <div className="stat-card">
              <p className="stat-label">Step 2</p>
              <p className="stat-value">JWT exchange</p>
              <p className="stat-detail">Confirm with the API.</p>
            </div>
            <div className="stat-card">
              <p className="stat-label">Step 3</p>
              <p className="stat-value">Ship faster</p>
              <p className="stat-detail">Use it on protected routes.</p>
            </div>
          </div>
        </section>
        <section className="panel fade-up delay-2">
          <div className="panel-card">
            <div className="panel-header">
              <p className="eyebrow">Secure access</p>
              <h2>Continue with Google</h2>
              <p>
                We verify your Google ID token and return it as your API JWT.
              </p>
            </div>
            <div className="google-wrap">
              <div ref={googleButtonRef} className="google-button" />
              {!googleClientId && (
                <div className="notice error">
                  Add NEXT_PUBLIC_GOOGLE_CLIENT_ID to webapp/.env.local and
                  restart the dev server.
                </div>
              )}
            </div>
            <div className={`status ${statusTone}`}>
              <span className="dot" />
              <span>{statusMessage}</span>
            </div>
            {user && token && (
              <div className="token-card">
                <div className="token-meta">
                  <span className="token-label">JWT</span>
                  <span className="token-expiry">
                    Expires in {formatDuration(expiresIn ?? 0)}
                  </span>
                </div>
                <div className="token-value">{token}</div>
                <div className="token-actions">
                  <button
                    className="copy-button"
                    type="button"
                    onClick={handleCopy}
                  >
                    {copied ? "Copied" : "Copy JWT"}
                  </button>
                  <span className="token-user">
                    Signed in as {user.firstname}
                  </span>
                </div>
              </div>
            )}
          </div>
          <div className="panel-footer">
            Your JWT stays in the browser. Nothing is written to local files.
          </div>
        </section>
      </div>
    </main>
  );
}
