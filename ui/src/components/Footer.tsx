export default function Footer() {
  const privacyUrl = process.env.NEXT_PUBLIC_PRIVACY_POLICY_URL || "#";
  const termsUrl = process.env.NEXT_PUBLIC_TERMS_URL || "#";

  return (
    <footer className="fixed bottom-0 left-0 right-0 bg-background border-t border-border py-4 px-6">
      <div className="flex justify-center items-center gap-6 text-sm text-muted-foreground">
        <a
          href={privacyUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="hover:text-foreground transition-colors"
        >
          Privacy Policy
        </a>
        <span className="text-border">|</span>
        <a
          href={termsUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="hover:text-foreground transition-colors"
        >
          Terms of Service
        </a>
      </div>
    </footer>
  );
}
