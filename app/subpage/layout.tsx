import { Header } from '@/components/site/header'
import { Footer } from '@/components/site/footer'
import { MobileToc } from '@/components/site/mobile-toc'
import { BackToTop } from '@/components/site/back-to-top'
import { HapticFeedback } from '@/components/site/haptic-feedback'
import { SwipeNavigation } from '@/components/site/swipe-navigation'

export default function SubpageLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <>
      <Header />
      <SwipeNavigation />
      <HapticFeedback />
      <MobileToc />
      <BackToTop />
      <main id="top">{children}</main>
      <Footer />
    </>
  )
}
