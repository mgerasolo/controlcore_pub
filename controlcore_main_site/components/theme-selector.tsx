"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Check, Palette, Smartphone, Monitor, Sparkles, Moon } from "lucide-react"
import { useControlCoreTheme } from "@/components/theme-provider"
import { themes, type ThemeMode } from "@/lib/themes"

export function ThemeSelector() {
  const { themeMode, setThemeMode } = useControlCoreTheme()

  const getThemeIcon = (mode: ThemeMode) => {
    switch (mode) {
      case "simple-light":
        return <Smartphone className="w-4 h-4" />
      case "simple-dark":
        return <Moon className="w-4 h-4" />
      case "enhanced-light":
        return <Monitor className="w-4 h-4" />
      case "enhanced-dark":
        return <Sparkles className="w-4 h-4" />
      default:
        return <Palette className="w-4 h-4" />
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Palette className="w-5 h-5" />
          Theme Selection
        </CardTitle>
        <CardDescription>Choose your preferred visual style for ControlCore</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {themes.map((theme) => (
            <div
              key={theme.id}
              className={`relative border rounded-lg p-4 cursor-pointer transition-all hover:shadow-md ${
                themeMode === theme.id ? "ring-2 ring-primary border-primary" : "border-border"
              }`}
              onClick={() => setThemeMode(theme.id)}
            >
              {themeMode === theme.id && (
                <div className="absolute top-2 right-2">
                  <div className="bg-primary text-primary-foreground rounded-full p-1">
                    <Check className="w-3 h-3" />
                  </div>
                </div>
              )}

              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  {getThemeIcon(theme.id)}
                  <h3 className="font-medium">{theme.name}</h3>
                </div>

                <div className={`h-16 rounded-md ${theme.preview} flex items-center justify-center`}>
                  <div className="text-xs text-center opacity-70">Preview</div>
                </div>

                <p className="text-sm text-muted-foreground">{theme.description}</p>

                <div className="flex flex-wrap gap-1">
                  {theme.features.gradients && (
                    <Badge variant="secondary" className="text-xs">
                      Gradients
                    </Badge>
                  )}
                  {theme.features.animations && (
                    <Badge variant="secondary" className="text-xs">
                      Animations
                    </Badge>
                  )}
                  {theme.features.shadows && (
                    <Badge variant="secondary" className="text-xs">
                      Shadows
                    </Badge>
                  )}
                  {theme.features.glassEffect && (
                    <Badge variant="secondary" className="text-xs">
                      Glass Effect
                    </Badge>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-6 p-4 bg-muted rounded-lg">
          <h4 className="font-medium mb-2">Theme Recommendations</h4>
          <div className="space-y-2 text-sm text-muted-foreground">
            <p>
              <strong>Simple themes:</strong> Optimized for mobile devices and field use with minimal visual
              distractions
            </p>
            <p>
              <strong>Enhanced themes:</strong> Rich desktop experience with gradients, animations, and visual depth
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
