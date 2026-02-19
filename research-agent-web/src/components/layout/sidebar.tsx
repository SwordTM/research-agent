"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, FileText, Settings, FlaskConical } from "lucide-react";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

type SidebarProps = React.HTMLAttributes<HTMLDivElement>;

export function Sidebar({ className }: SidebarProps) {
    const pathname = usePathname();

    return (
        <div className={cn("pb-12 w-64 border-r bg-background", className)}>
            <div className="space-y-4 py-4">
                <div className="px-3 py-2">
                    <div className="flex items-center px-4 mb-4">
                        <FlaskConical className="h-6 w-6 mr-2" />
                        <h2 className="text-lg font-semibold tracking-tight">
                            Research Agent
                        </h2>
                    </div>
                    <div className="space-y-1">
                        <Link href="/dashboard">
                            <Button
                                variant={pathname === "/dashboard" ? "secondary" : "ghost"}
                                className="w-full justify-start"
                            >
                                <LayoutDashboard className="mr-2 h-4 w-4" />
                                Dashboard
                            </Button>
                        </Link>
                        <Link href="/dashboard/projects">
                            <Button
                                variant={pathname === "/dashboard/projects" ? "secondary" : "ghost"}
                                className="w-full justify-start"
                            >
                                <FileText className="mr-2 h-4 w-4" />
                                Projects
                            </Button>
                        </Link>
                        <Link href="/dashboard/settings">
                            <Button
                                variant={pathname === "/dashboard/settings" ? "secondary" : "ghost"}
                                className="w-full justify-start"
                            >
                                <Settings className="mr-2 h-4 w-4" />
                                Settings
                            </Button>
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
}
