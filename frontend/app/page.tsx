import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <div className="text-center space-y-6 max-w-2xl">
        <h1 className="text-5xl font-bold tracking-tight">
          Welcome to{" "}
          <span className="text-primary">Openmailer</span>
        </h1>
        <p className="text-xl text-muted-foreground">
          Enterprise-grade email marketing, deliverability, and CRM platform
        </p>
        <div className="flex gap-4 justify-center pt-4">
          <Link
            href="/login"
            className="inline-flex items-center justify-center rounded-md bg-primary px-6 py-3 text-sm font-medium text-primary-foreground hover:bg-primary/90"
          >
            Sign In
          </Link>
          <Link
            href="/register"
            className="inline-flex items-center justify-center rounded-md border border-input bg-background px-6 py-3 text-sm font-medium hover:bg-accent"
          >
            Get Started
          </Link>
        </div>
        <div className="grid grid-cols-3 gap-6 pt-12 text-left">
          <div className="space-y-2 p-4 rounded-lg border">
            <h3 className="font-semibold">Email Marketing</h3>
            <p className="text-sm text-muted-foreground">
              Smart campaigns with AI-powered sending, A/B testing, and advanced analytics
            </p>
          </div>
          <div className="space-y-2 p-4 rounded-lg border">
            <h3 className="font-semibold">Deliverability</h3>
            <p className="text-sm text-muted-foreground">
              SPF/DKIM/DMARC checks, warmup engine, and spam recovery system
            </p>
          </div>
          <div className="space-y-2 p-4 rounded-lg border">
            <h3 className="font-semibold">CRM & Automation</h3>
            <p className="text-sm text-muted-foreground">
              Built-in CRM, visual automation builder, and lead scoring engine
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}
