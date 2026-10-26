/** Trapper — SSRF protection utilities. */

import { URL } from 'url';

// Private/reserved IP ranges per RFC 1918 and others
const PRIVATE_RANGES = [
  '10.', '100.64.', '127.', '169.254.', '172.16.', '172.17.', '172.18.',
  '172.19.', '172.20.', '172.21.', '172.22.', '172.23.', '172.24.',
  '172.25.', '172.26.', '172.27.', '172.28.', '172.29.', '172.30.',
  '172.31.', '192.168.', '0.', '192.0.0.', '192.0.2.', '198.51.100.',
  '203.0.113.', '224.', '225.', '226.', '227.', '228.', '229.', '230.',
  '231.', '232.', '233.', '234.', '235.', '236.', '237.', '238.', '239.',
  '240.', '241.', '242.', '243.', '244.', '245.', '246.', '247.', '248.',
  '249.', '250.', '251.', '252.', '253.', '254.', '255.',
];

const BLOCKED_HOSTS = new Set([
  'localhost', '0.0.0.0', 'metadata.google.internal',
  '169.254.169.254', 'internal',
]);

function isPrivateIP(ip: string): boolean {
  for (const prefix of PRIVATE_RANGES) {
    if (ip.startsWith(prefix)) return true;
  }
  return false;
}

/**
 * Validate a URL to prevent SSRF attacks.
 * Returns true if the URL is safe to access.
 */
export function isUrlSafe(urlString: string): boolean {
  try {
    const url = new URL(urlString);

    // Only allow http/https
    if (url.protocol !== 'http:' && url.protocol !== 'https:') {
      return false;
    }

    // Block known dangerous hosts
    const host = url.hostname.toLowerCase();
    if (BLOCKED_HOSTS.has(host)) {
      return false;
    }

    // Block private IP ranges (basic check — DNS resolution happens later)
    if (isPrivateIP(host)) {
      return false;
    }

    // Block IPv6 loopback
    if (host === '::1' || host === '[::1]') {
      return false;
    }

    return true;
  } catch {
    return false;
  }
}

/**
 * Check if a resolved IP address is safe (post-DNS check).
 */
export function isIpSafe(ip: string): boolean {
  if (BLOCKED_HOSTS.has(ip)) return false;
  if (isPrivateIP(ip)) return false;
  return true;
}
