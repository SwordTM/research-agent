import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function MarketingLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="flex min-h-screen flex-col">
            <header className="container mx-auto z-40 bg-background">
                <div className="flex h-20 items-center justify-between py-6">
                    <Link href="/" className="flex items-center space-x-2">
                        <span className="text-xl font-bold">Research Agent</span>
                    </Link>
                    <nav>
                        <Link href="/dashboard">
                            <Button variant="ghost" className="mr-4">
                                Dashboard
                            </Button>
                        </Link>

                        <Link href="/login">
                            <Button variant="ghost" className="mr-4">
                                Login
                            </Button>
                        </Link>
                        <Link href="/signup">
                            <Button>Sign Up</Button>
                        </Link>
                    </nav>
                </div>
            </header>
            <main className="flex-1">{children}</main>
            <footer className="py-6 md:px-8 md:py-0">
                <div className="container mx-auto flex flex-col items-center justify-between gap-4 md:h-24 md:flex-row">
                    <p className="text-center text-sm leading-loose text-muted-foreground md:text-left">
                        Built by{" "}
                        <a
                            href="#"
                            target="_blank"
                            rel="noreferrer"
                            className="font-medium underline underline-offset-4"
                        >
                            Research Agent Team
                        </a>
                        .
                    </p>
                </div>
            </footer>
        </div>
    );
}
