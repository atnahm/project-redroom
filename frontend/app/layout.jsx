import './globals.css'

export const metadata = {
  title: 'Redroom | Deepfake Forensics SaaS',
  description: 'Tier-1 Deepfake Detection System',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-900 text-slate-100 font-sans">
        {children}
      </body>
    </html>
  )
}
