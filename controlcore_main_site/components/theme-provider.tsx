"use client"

import * as React from "react"
import { ThemeProvider as NextThemesProvider } from "next-themes"
import type { ThemeProviderProps } from "next-themes"
import { applyTheme, getStoredTheme, type ThemeMode } from "@/lib/themes"

interface ControlCoreThemeContextType {
  themeMode: ThemeMode
  setThemeMode: (mode: ThemeMode) => void
}

const ControlCoreThemeContext = React.createContext<ControlCoreThemeContextType | undefined>(undefined)

export function ThemeProvider({ children, ...props }: ThemeProviderProps) {
  const [themeMode, setThemeModeState] = React.useState<ThemeMode>("simple-light")

  React.useEffect(() => {
    const stored = getStoredTheme()
    setThemeModeState(stored)
    applyTheme(stored)
  }, [])

  const setThemeMode = React.useCallback((mode: ThemeMode) => {
    setThemeModeState(mode)
    applyTheme(mode)
  }, [])

  return (
    <NextThemesProvider {...props}>
      <ControlCoreThemeContext.Provider value={{ themeMode, setThemeMode }}>
        {children}
      </ControlCoreThemeContext.Provider>
    </NextThemesProvider>
  )
}

export function useControlCoreTheme() {
  const context = React.useContext(ControlCoreThemeContext)
  if (context === undefined) {
    throw new Error("useControlCoreTheme must be used within a ThemeProvider")
  }
  return context
}
