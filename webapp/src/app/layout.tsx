import './globals.css';

export const metadata = {
  title: 'Webapp',
  description: 'Base Next.js webapp',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
