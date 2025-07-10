"use client";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Brain,
  Globe,
  Network,
  Zap,
  Droplets,
  Factory,
  Home,
  FlaskConical,
  Satellite,
  BarChart3,
  ArrowLeft,
} from "lucide-react";
import Link from "next/link";
import { Navigation } from "@/components/navigation";

export default function AboutPage() {
  return (
    <>
      <Navigation />
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
        <div className="container mx-auto px-4 py-12 max-w-6xl">
          {/* Back Navigation */}
          <div className="mb-8">
            <Button variant="ghost" asChild className="mb-4">
              <Link href="/" className="flex items-center gap-2">
                <ArrowLeft className="h-4 w-4" />
                Back to Dashboard
              </Link>
            </Button>
          </div>

          {/* Hero Section */}
          <div className="text-center mb-16">
            <div className="flex items-center justify-center gap-3 mb-6">
              <Brain className="h-12 w-12 text-blue-600" />
              <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                About ControlCore
              </h1>
            </div>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
              A modular control system for intelligent automation—designed to
              sense, think, and act in real-world environments.
            </p>
          </div>

          {/* Core Description */}
          <Card className="mb-12 border-0 shadow-lg">
            <CardHeader className="pb-6">
              <CardTitle className="text-2xl flex items-center gap-2">
                <Network className="h-6 w-6 text-blue-600" />
                Intelligent Control Architecture
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <p className="text-lg leading-relaxed">
                At its heart is a core logic engine capable of ingesting sensor
                data, analyzing patterns, making contextual decisions, and
                dispatching targeted actions through connected hardware. It is
                structured around a human-first interface and AI-enhanced
                planning loop, blending autonomy with oversight.
              </p>
              <div className="grid md:grid-cols-3 gap-6 mt-8">
                <div className="text-center p-6 rounded-lg bg-blue-50 dark:bg-blue-950/20">
                  <BarChart3 className="h-8 w-8 text-blue-600 mx-auto mb-3" />
                  <h3 className="font-semibold mb-2">Sense</h3>
                  <p className="text-sm text-muted-foreground">
                    Continuous data ingestion from multiple sensor sources
                  </p>
                </div>
                <div className="text-center p-6 rounded-lg bg-purple-50 dark:bg-purple-950/20">
                  <Brain className="h-8 w-8 text-purple-600 mx-auto mb-3" />
                  <h3 className="font-semibold mb-2">Think</h3>
                  <p className="text-sm text-muted-foreground">
                    AI-enhanced analysis and contextual decision making
                  </p>
                </div>
                <div className="text-center p-6 rounded-lg bg-green-50 dark:bg-green-950/20">
                  <Zap className="h-8 w-8 text-green-600 mx-auto mb-3" />
                  <h3 className="font-semibold mb-2">Act</h3>
                  <p className="text-sm text-muted-foreground">
                    Targeted actions through connected hardware systems
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Applications Grid */}
          <Card className="mb-12 border-0 shadow-lg">
            <CardHeader className="pb-6">
              <CardTitle className="text-2xl flex items-center gap-2">
                <Globe className="h-6 w-6 text-green-600" />
                Versatile Applications
              </CardTitle>
              <CardDescription className="text-base">
                While our current testbed demonstrates precision irrigation
                control, the underlying architecture is intentionally flexible.
                ControlCore is engineered to support a wide range of
                applications:
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div className="flex items-start gap-4 p-4 rounded-lg border bg-card hover:shadow-md transition-shadow">
                  <Droplets className="h-8 w-8 text-blue-500 mt-1 flex-shrink-0" />
                  <div>
                    <h3 className="font-semibold mb-2">Smart Agriculture</h3>
                    <p className="text-sm text-muted-foreground">
                      Environmental monitoring and precision irrigation systems
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-4 p-4 rounded-lg border bg-card hover:shadow-md transition-shadow">
                  <Factory className="h-8 w-8 text-orange-500 mt-1 flex-shrink-0" />
                  <div>
                    <h3 className="font-semibold mb-2">
                      Industrial Automation
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      Manufacturing and process control systems
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-4 p-4 rounded-lg border bg-card hover:shadow-md transition-shadow">
                  <Home className="h-8 w-8 text-green-500 mt-1 flex-shrink-0" />
                  <div>
                    <h3 className="font-semibold mb-2">Home Automation</h3>
                    <p className="text-sm text-muted-foreground">
                      Smart home systems and energy management
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-4 p-4 rounded-lg border bg-card hover:shadow-md transition-shadow">
                  <FlaskConical className="h-8 w-8 text-purple-500 mt-1 flex-shrink-0" />
                  <div>
                    <h3 className="font-semibold mb-2">Research Frameworks</h3>
                    <p className="text-sm text-muted-foreground">
                      Modular data collection and experimental control
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-4 p-4 rounded-lg border bg-card hover:shadow-md transition-shadow">
                  <Satellite className="h-8 w-8 text-red-500 mt-1 flex-shrink-0" />
                  <div>
                    <h3 className="font-semibold mb-2">Remote Sensing</h3>
                    <p className="text-sm text-muted-foreground">
                      AI-assisted analysis of remote sensor networks
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-4 p-4 rounded-lg border bg-card hover:shadow-md transition-shadow">
                  <BarChart3 className="h-8 w-8 text-cyan-500 mt-1 flex-shrink-0" />
                  <div>
                    <h3 className="font-semibold mb-2">Lab Control Systems</h3>
                    <p className="text-sm text-muted-foreground">
                      Experimental control in laboratory and field environments
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Live Instance */}
          <div className="grid lg:grid-cols-2 gap-8 mb-12">
            <Card className="border-0 shadow-lg">
              <CardHeader className="pb-6">
                <CardTitle className="text-2xl flex items-center gap-2">
                  <Globe className="h-6 w-6 text-green-600" />
                  Live Instance
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-2 mb-4">
                  <div className="h-3 w-3 bg-green-500 rounded-full animate-pulse"></div>
                  <Badge
                    variant="secondary"
                    className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                  >
                    Live Beta Active
                  </Badge>
                </div>
                <p className="leading-relaxed">
                  You're viewing the live beta of ControlCore at work. Connected
                  hardware can be controlled through this interface, with all
                  decisions running through the central core planner.
                </p>
                <p className="leading-relaxed">
                  Users may interact with active modules, monitor decision
                  paths, and test real-time updates.
                </p>
                <Button asChild className="mt-4">
                  <Link href="/">View Live Dashboard</Link>
                </Button>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg">
              <CardHeader className="pb-6">
                <CardTitle className="text-2xl flex items-center gap-2">
                  <Network className="h-6 w-6 text-blue-600" />
                  System Flow
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="leading-relaxed">
                  The system processes information from user intent or raw
                  sensor data to real-world action through an 8-node logic
                  engine.
                </p>
                <p className="leading-relaxed">
                  Each step is observable, inspectable, and extendable,
                  providing full transparency in the decision-making process.
                </p>
                <div className="mt-6">
                  <Button variant="outline" asChild>
                    <a
                      href="https://wink-tomato-31906713.figma.site"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2"
                    >
                      <Network className="h-4 w-4" />
                      View Interactive System Flow
                    </a>
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Technical Highlights */}
          <Card className="border-0 shadow-lg">
            <CardHeader className="pb-6">
              <CardTitle className="text-2xl">Key Features</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-8">
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-blue-600">
                    Architecture
                  </h3>
                  <ul className="space-y-2 text-muted-foreground">
                    <li className="flex items-start gap-2">
                      <div className="h-1.5 w-1.5 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
                      Modular, extensible design
                    </li>
                    <li className="flex items-start gap-2">
                      <div className="h-1.5 w-1.5 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
                      Real-time sensor data processing
                    </li>
                    <li className="flex items-start gap-2">
                      <div className="h-1.5 w-1.5 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
                      AI-enhanced decision making
                    </li>
                    <li className="flex items-start gap-2">
                      <div className="h-1.5 w-1.5 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
                      Hardware abstraction layer
                    </li>
                  </ul>
                </div>
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-green-600">
                    Interface
                  </h3>
                  <ul className="space-y-2 text-muted-foreground">
                    <li className="flex items-start gap-2">
                      <div className="h-1.5 w-1.5 bg-green-600 rounded-full mt-2 flex-shrink-0"></div>
                      Human-first design principles
                    </li>
                    <li className="flex items-start gap-2">
                      <div className="h-1.5 w-1.5 bg-green-600 rounded-full mt-2 flex-shrink-0"></div>
                      Observable decision paths
                    </li>
                    <li className="flex items-start gap-2">
                      <div className="h-1.5 w-1.5 bg-green-600 rounded-full mt-2 flex-shrink-0"></div>
                      Real-time monitoring and control
                    </li>
                    <li className="flex items-start gap-2">
                      <div className="h-1.5 w-1.5 bg-green-600 rounded-full mt-2 flex-shrink-0"></div>
                      Autonomous with human oversight
                    </li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </>
  );
}
