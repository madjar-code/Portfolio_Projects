import { StrictMode } from "react"
import { createRoot } from "react-dom/client"
import { ThemeProvider } from "styled-components"
import { GlobalStyles } from "./styles/GlobalStyles"
import { theme } from "./styles/theme"
import { GoogleOAuthProvider } from "@react-oauth/google"
import App from "./App"

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <ThemeProvider theme={theme}>
        <GlobalStyles/>
        <App/>
      </ThemeProvider>
    </GoogleOAuthProvider>
  </StrictMode>
)