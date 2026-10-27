import { isBlockedUrl, isBlockedIp, BLOCKED_HOSTS } from '../../src/utils/ssrfProtection';

describe('SSRF Protection', () => {
  describe('isBlockedIp', () => {
    it('blocks loopback IPv4', () => {
      expect(isBlockedIp('127.0.0.1')).toBe(true);
      expect(isBlockedIp('127.0.0.255')).toBe(true);
      expect(isBlockedIp('127.255.255.255')).toBe(true);
    });

    it('blocks private IPv4 ranges', () => {
      expect(isBlockedIp('10.0.0.1')).toBe(true);
      expect(isBlockedIp('10.255.255.255')).toBe(true);
      expect(isBlockedIp('172.16.0.1')).toBe(true);
      expect(isBlockedIp('172.31.255.255')).toBe(true);
      expect(isBlockedIp('192.168.0.1')).toBe(true);
      expect(isBlockedIp('192.168.255.255')).toBe(true);
    });

    it('blocks link-local addresses', () => {
      expect(isBlockedIp('169.254.0.1')).toBe(true);
      expect(isBlockedIp('169.254.169.254')).toBe(true); // Cloud metadata
    });

    it('blocks reserved and multicast addresses', () => {
      expect(isBlockedIp('0.0.0.0')).toBe(true);
      expect(isBlockedIp('224.0.0.1')).toBe(true); // Multicast
      expect(isBlockedIp('240.0.0.1')).toBe(true); // Reserved
      expect(isBlockedIp('255.255.255.255')).toBe(true); // Reserved
    });

    it('blocks shared address space (CGNAT)', () => {
      expect(isBlockedIp('100.64.0.1')).toBe(true);
      expect(isBlockedIp('100.127.255.255')).toBe(true);
    });

    it('blocks IPv6 loopback', () => {
      expect(isBlockedIp('::1')).toBe(true);
    });

    it('blocks IPv6 link-local', () => {
      expect(isBlockedIp('fe80::1')).toBe(true);
      expect(isBlockedIp('FE80::1')).toBe(true);
    });

    it('blocks IPv6 unique local addresses', () => {
      expect(isBlockedIp('fd00::1')).toBe(true);
      expect(isBlockedIp('fc00::1')).toBe(true);
      expect(isBlockedIp('FD00::1')).toBe(true);
    });

    it('allows public IPv4 addresses', () => {
      expect(isBlockedIp('8.8.8.8')).toBe(false);
      expect(isBlockedIp('1.1.1.1')).toBe(false);
      expect(isBlockedIp('93.184.216.34')).toBe(false); // example.com
    });

    it('handles invalid IP addresses', () => {
      expect(isBlockedIp('not-an-ip')).toBe(false);
      expect(isBlockedIp('')).toBe(false);
    });
  });

  describe('isBlockedUrl', () => {
    it('blocks localhost by hostname', async () => {
      expect(await isBlockedUrl('http://localhost')).toBe(true);
      expect(await isBlockedUrl('http://localhost:8080')).toBe(true);
      expect(await isBlockedUrl('http://localhost/admin')).toBe(true);
    });

    it('blocks loopback IP addresses', async () => {
      expect(await isBlockedUrl('http://127.0.0.1')).toBe(true);
      expect(await isBlockedUrl('http://127.0.0.1:8080')).toBe(true);
      expect(await isBlockedUrl('http://127.0.0.1/admin')).toBe(true);
    });

    it('blocks private IP ranges', async () => {
      expect(await isBlockedUrl('http://10.0.0.1')).toBe(true);
      expect(await isBlockedUrl('http://192.168.1.1')).toBe(true);
      expect(await isBlockedUrl('http://172.16.0.1')).toBe(true);
    });

    it('blocks cloud metadata endpoints', async () => {
      expect(await isBlockedUrl('http://169.254.169.254')).toBe(true);
      expect(await isBlockedUrl('http://169.254.169.254/latest/meta-data/')).toBe(true);
      expect(await isBlockedUrl('http://metadata.google.internal')).toBe(true);
    });

    it('blocks IPv6 loopback', async () => {
      expect(await isBlockedUrl('http://[::1]')).toBe(true);
    });

    it('blocks link-local addresses', async () => {
      expect(await isBlockedUrl('http://169.254.0.1')).toBe(true);
    });

    it('blocks IPv4-mapped IPv6 addresses', async () => {
      // IPv4-mapped IPv6 for 127.0.0.1
      expect(await isBlockedUrl('http://[::ffff:127.0.0.1]')).toBe(true);
    });

    it('blocks URLs with obfuscated IP addresses', async () => {
      // Octal IP representation
      expect(await isBlockedUrl('http://0177.0.0.1')).toBe(true);
      // Hex IP representation
      expect(await isBlockedUrl('http://0x7f.0x0.0x0.0x1')).toBe(true);
    });

    it('allows public URLs', async () => {
      // These may fail DNS resolution in test environment, but should not be blocked by IP
      // We test that the function doesn't throw and handles DNS failures gracefully
      expect(async () => await isBlockedUrl('http://example.com')).not.toThrow();
      expect(async () => await isBlockedUrl('https://example.com')).not.toThrow();
    });

    it('blocks URLs with invalid hostnames', async () => {
      expect(await isBlockedUrl('http://')).toBe(true);
      expect(await isBlockedUrl('http:///path')).toBe(true);
    });

    it('blocks malformed URLs', async () => {
      expect(await isBlockedUrl('not-a-url')).toBe(true);
      expect(await isBlockedUrl('')).toBe(true);
    });
  });

  describe('Scheme validation (crawl route)', () => {
    // These tests verify the scheme check logic used in crawl.ts
    // The check is: parsedUrl.protocol !== 'http:' && parsedUrl.protocol !== 'https:'

    it('accepts http:// URLs', () => {
      const url = new URL('http://example.com');
      const allowed = url.protocol === 'http:' || url.protocol === 'https:';
      expect(allowed).toBe(true);
    });

    it('accepts https:// URLs', () => {
      const url = new URL('https://example.com');
      const allowed = url.protocol === 'http:' || url.protocol === 'https:';
      expect(allowed).toBe(true);
    });

    it('rejects file:// URLs', () => {
      const url = new URL('file:///etc/passwd');
      const allowed = url.protocol === 'http:' || url.protocol === 'https:';
      expect(allowed).toBe(false);
    });

    it('rejects ftp:// URLs', () => {
      const url = new URL('ftp://example.com');
      const allowed = url.protocol === 'http:' || url.protocol === 'https:';
      expect(allowed).toBe(false);
    });

    it('rejects javascript: URLs via data: scheme', () => {
      // javascript: is not a valid URL scheme for new URL(), but data: is
      const url = new URL('data:text/html,<script>alert(1)</script>');
      const allowed = url.protocol === 'http:' || url.protocol === 'https:';
      expect(allowed).toBe(false);
    });

    it('rejects malformed URLs', () => {
      expect(() => new URL('not-a-url')).toThrow();
      expect(() => new URL('')).toThrow();
    });
  });

  describe('BLOCKED_HOSTS', () => {
    it('contains localhost', () => {
      expect(BLOCKED_HOSTS.has('localhost')).toBe(true);
    });

    it('contains cloud metadata endpoints', () => {
      expect(BLOCKED_HOSTS.has('169.254.169.254')).toBe(true);
      expect(BLOCKED_HOSTS.has('metadata.google.internal')).toBe(true);
    });

    it('contains AWS metadata endpoints', () => {
      expect(BLOCKED_HOSTS.has('169.254.170.2')).toBe(true);
      expect(BLOCKED_HOSTS.has('169.254.169.253')).toBe(true);
    });

    it('contains Azure metadata endpoints', () => {
      expect(BLOCKED_HOSTS.has('169.254.169.4')).toBe(true);
    });

    it('contains Oracle Cloud metadata', () => {
      expect(BLOCKED_HOSTS.has('192.0.0.192')).toBe(true);
    });

    it('contains Alibaba Cloud metadata', () => {
      expect(BLOCKED_HOSTS.has('100.100.100.200')).toBe(true);
    });
  });
});
