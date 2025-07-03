export type ThemeMode = "simple-light" | "simple-dark" | "enhanced-light" | "enhanced-dark"

export interface ThemeConfig {
  id: ThemeMode
  name: string
  description: string
  preview: string
  cssVars: Record<string, string>
  features: {
    gradients: boolean
    animations: boolean
    shadows: boolean
    patterns: boolean
    glassEffect: boolean
  }
}

export const themes: ThemeConfig[] = [
  {
    id: "simple-light",
    name: "Simple Light",
    description: "Clean, minimal design perfect for field use",
    preview: "bg-white border border-gray-200",
    cssVars: {
      "--background": "0 0% 100%",
      "--foreground": "222.2 84% 4.9%",
      "--card": "0 0% 100%",
      "--card-foreground": "222.2 84% 4.9%",
      "--primary": "142 76% 36%",
      "--primary-foreground": "355.7 100% 97.3%",
      "--secondary": "210 40% 98%",
      "--muted": "210 40% 98%",
      "--accent": "210 40% 98%",
      "--border": "214.3 31.8% 91.4%",
    },
    features: {
      gradients: false,
      animations: false,
      shadows: false,
      patterns: false,
      glassEffect: false,
    },
  },
  {
    id: "simple-dark",
    name: "Simple Dark",
    description: "Clean dark theme for low-light conditions",
    preview: "bg-gray-900 border border-gray-700",
    cssVars: {
      "--background": "222.2 84% 4.9%",
      "--foreground": "210 40% 98%",
      "--card": "222.2 84% 4.9%",
      "--card-foreground": "210 40% 98%",
      "--primary": "142 76% 36%",
      "--primary-foreground": "355.7 100% 97.3%",
      "--secondary": "217.2 32.6% 17.5%",
      "--muted": "217.2 32.6% 17.5%",
      "--accent": "217.2 32.6% 17.5%",
      "--border": "217.2 32.6% 17.5%",
    },
    features: {
      gradients: false,
      animations: false,
      shadows: false,
      patterns: false,
      glassEffect: false,
    },
  },
  {
    id: "enhanced-light",
    name: "Enhanced Light",
    description: "Rich visuals with gradients and animations",
    preview: "bg-gradient-to-br from-blue-50 to-green-50 border border-blue-200",
    cssVars: {
      "--background": "0 0% 100%",
      "--foreground": "222.2 84% 4.9%",
      "--card": "0 0% 100%",
      "--card-foreground": "222.2 84% 4.9%",
      "--primary": "142 76% 36%",
      "--primary-foreground": "355.7 100% 97.3%",
      "--secondary": "210 40% 98%",
      "--muted": "210 40% 98%",
      "--accent": "210 40% 98%",
      "--border": "214.3 31.8% 91.4%",
      "--enhanced-bg": "linear-gradient(135deg, hsl(210 100% 97%) 0%, hsl(142 100% 97%) 100%)",
      "--enhanced-card": "rgba(255, 255, 255, 0.8)",
      "--enhanced-shadow": "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
    },
    features: {
      gradients: true,
      animations: true,
      shadows: true,
      patterns: true,
      glassEffect: true,
    },
  },
  {
    id: "enhanced-dark",
    name: "Enhanced Dark",
    description: "Sophisticated dark theme with visual depth",
    preview: "bg-gradient-to-br from-gray-900 to-blue-900 border border-blue-800",
    cssVars: {
      "--background": "222.2 84% 4.9%",
      "--foreground": "210 40% 98%",
      "--card": "222.2 84% 4.9%",
      "--card-foreground": "210 40% 98%",
      "--primary": "142 76% 36%",
      "--primary-foreground": "355.7 100% 97.3%",
      "--secondary": "217.2 32.6% 17.5%",
      "--muted": "217.2 32.6% 17.5%",
      "--accent": "217.2 32.6% 17.5%",
      "--border": "217.2 32.6% 17.5%",
      "--enhanced-bg": "linear-gradient(135deg, hsl(222 84% 4%) 0%, hsl(230 84% 6%) 100%)",
      "--enhanced-card": "rgba(15, 23, 42, 0.8)",
      "--enhanced-shadow": "0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 10px 10px -5px rgba(0, 0, 0, 0.3)",
    },
    features: {
      gradients: true,
      animations: true,
      shadows: true,
      patterns: true,
      glassEffect: true,
    },
  },
]

export function getTheme(mode: ThemeMode): ThemeConfig {
  return themes.find((theme) => theme.id === mode) || themes[0]
}

export function applyTheme(mode: ThemeMode) {
  const theme = getTheme(mode)
  const root = document.documentElement

  // Apply CSS variables
  Object.entries(theme.cssVars).forEach(([key, value]) => {
    root.style.setProperty(key, value)
  })

  // Apply theme class for enhanced features
  root.className = root.className.replace(/theme-\w+/g, "")
  root.classList.add(`theme-${mode}`)

  // Store preference
  localStorage.setItem("controlcore-theme", mode)
}

export function getStoredTheme(): ThemeMode {
  if (typeof window === "undefined") return "simple-light"
  return (localStorage.getItem("controlcore-theme") as ThemeMode) || "simple-light"
}
