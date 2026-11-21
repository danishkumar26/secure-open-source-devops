export const metadata = {
  title: "Secure Open Source DevOps Platform",
  description: "DevSecOps dashboard for open-source projects",
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
