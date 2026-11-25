const API_BASE = '/api';

/**
 * Core API fetch utility.
 * Auto-injects session_id from localStorage on GET requests.
 * On 400/401, clears stale session and redirects to /upload.
 * Returns null on any error so callers can handle gracefully.
 */
async function fetchAPI(endpoint, options = {}) {
    const storedSession = localStorage.getItem('atlas-session-id');
    const isGet = !options.method || options.method.toUpperCase() === 'GET';

    if (storedSession && isGet && !endpoint.includes('session_id') && !options.body) {
        endpoint += (endpoint.includes('?') ? '&' : '?') + 'session_id=' + storedSession;
    }

    try {
        const res = await fetch(API_BASE + endpoint, {
            headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
            ...options
        });

        if (res.status === 400 || res.status === 401) {
            let body = {};
            try { body = await res.json(); } catch (_) {}
            localStorage.removeItem('atlas-session-id');
            if (body.redirect) {
                window.location.href = body.redirect;
            }
            return null;
        }

        if (!res.ok) {
            const errBody = await res.json().catch(() => ({}));
            return null;
        }

        return await res.json();
    } catch (_error) {
        return null;
    }
}
