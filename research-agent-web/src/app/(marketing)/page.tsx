import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function LandingPage() {
    return (
        <>
            <section className="space-y-6 pb-8 pt-6 md:pb-12 md:pt-10 lg:py-32">
                <div className="container mx-auto flex max-w-[64rem] flex-col items-center gap-4 text-center">
                    <h1 className="font-heading text-3xl sm:text-5xl md:text-6xl lg:text-7xl">
                        AI-Powered Research Assistant
                    </h1>
                    <p className="max-w-[42rem] leading-normal text-muted-foreground sm:text-xl sm:leading-8">
                        Accelerate your research with AI-driven insights, automated summaries, and visual explanations.
                    </p>
                    <div className="space-x-4">
                        <Link href="/signup">
                            <Button size="lg">Get Started</Button>
                        </Link>
                        <Link href="/login">
                            <Button variant="outline" size="lg">
                                View Demo
                            </Button>
                        </Link>
                    </div>
                </div>
            </section>

            <section
                id="features"
                className="container mx-auto space-y-6 bg-slate-50 py-8 dark:bg-transparent md:py-12 lg:py-24"
            >
                <div className="mx-auto flex max-w-[58rem] flex-col items-center space-y-4 text-center">
                    <h2 className="font-heading text-3xl leading-[1.1] sm:text-3xl md:text-6xl">
                        Features
                    </h2>
                    <p className="max-w-[85%] leading-normal text-muted-foreground sm:text-lg sm:leading-7">
                        Tools designed to help you understand complex topics faster.
                    </p>
                </div>
                <div className="mx-auto grid justify-center gap-4 sm:grid-cols-2 md:max-w-[64rem] md:grid-cols-3">
                    <div className="relative overflow-hidden rounded-lg border bg-background p-2">
                        <div className="flex h-[180px] flex-col justify-between rounded-md p-6">
                            <div className="space-y-2">
                                <h3 className="font-bold">Automated Summaries</h3>
                                <p className="text-sm text-muted-foreground">
                                    Upload PDFs and get instant, accurate summaries of research papers.
                                </p>
                            </div>
                        </div>
                    </div>
                    <div className="relative overflow-hidden rounded-lg border bg-background p-2">
                        <div className="flex h-[180px] flex-col justify-between rounded-md p-6">
                            <div className="space-y-2">
                                <h3 className="font-bold">Visual Explanations</h3>
                                <p className="text-sm text-muted-foreground">
                                    Generate visual aids and slides to better understand complex concepts.
                                </p>
                            </div>
                        </div>
                    </div>
                    <div className="relative overflow-hidden rounded-lg border bg-background p-2">
                        <div className="flex h-[180px] flex-col justify-between rounded-md p-6">
                            <div className="space-y-2">
                                <h3 className="font-bold">Interactive Chat</h3>
                                <p className="text-sm text-muted-foreground">
                                    Ask questions and get answers directly from your documents.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </>
    );
}
