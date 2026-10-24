import { Apple, Monitor, Terminal } from 'lucide-react'

export type Installer = {
  label: string
  subtitle: string
  file: string
  icon: typeof Apple
}

export const INSTALLERS: Installer[] = [
  {
    label: 'macOS',
    subtitle: 'Apple Silicon (M1/M2/M3)',
    file: 'evershade-darwin-arm64.tar.gz',
    icon: Apple,
  },
  {
    label: 'macOS',
    subtitle: 'Intel (x86_64)',
    file: 'evershade-darwin-amd64.tar.gz',
    icon: Apple,
  },
  {
    label: 'Windows',
    subtitle: 'x86_64 (Installer)',
    file: 'evershade-windows-amd64.exe',
    icon: Monitor,
  },
  {
    label: 'Linux',
    subtitle: 'x86_64 (Debian/Ubuntu)',
    file: 'evershade-linux-amd64.tar.gz',
    icon: Terminal,
  },
  {
    label: 'Linux',
    subtitle: 'ARM64',
    file: 'evershade-linux-arm64.tar.gz',
    icon: Terminal,
  },
]

export const RELEASES_BASE_URL = 'https://github.com/LukaG712/Evershade/releases/latest/download'
