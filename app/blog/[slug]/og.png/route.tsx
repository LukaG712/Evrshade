import { ImageResponse } from 'next/og'

export const runtime = 'edge'
export const alt = 'Evershade blog post'
export const size = {
  width: 1200,
  height: 630,
}
export const contentType = 'image/png'

export default async function Image({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params
  // Convert slug to title format
  const title = slug
    .split('-')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')

  return new ImageResponse(
    (
      <div
        style={{
          height: '100%',
          width: '100%',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          backgroundColor: '#fcfcfa',
          fontFamily: 'Geist, sans-serif',
          padding: '60px',
        }}
      >
        {/* Grid background */}
        <div
          style={{
            position: 'absolute',
            inset: 0,
            backgroundImage:
              'linear-gradient(to right, rgba(0,0,0,0.05) 1px, transparent 1px), linear-gradient(to bottom, rgba(0,0,0,0.05) 1px, transparent 1px)',
            backgroundSize: '80px 80px',
          }}
        />
        {/* Logo */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(2, 16px)',
            gap: '2px',
            marginBottom: '40px',
            position: 'relative',
          }}
        >
          <div style={{ width: 16, height: 16, backgroundColor: '#1a1a1a' }} />
          <div style={{ width: 16, height: 16, backgroundColor: '#1a1a1a' }} />
          <div style={{ width: 16, height: 16, backgroundColor: '#1a1a1a' }} />
          <div style={{ width: 16, height: 16, backgroundColor: '#4ade80' }} />
        </div>
        {/* Title */}
        <div
          style={{
            fontSize: 56,
            fontWeight: 600,
            textAlign: 'center',
            color: '#1a1a1a',
            letterSpacing: '-0.03em',
            lineHeight: 1.1,
            maxWidth: '900px',
            position: 'relative',
          }}
        >
          {title}
        </div>
        {/* Footer */}
        <div
          style={{
            marginTop: 'auto',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            position: 'relative',
          }}
        >
          <span style={{ fontSize: 20, color: '#737373', fontFamily: 'monospace' }}>
            evrshade.netlify.app/blog
          </span>
        </div>
      </div>
    ),
    { ...size }
  )
}
