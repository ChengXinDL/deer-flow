import { env } from "@/env";

export function getBackendBaseURL() {
  if (env.NEXT_PUBLIC_BACKEND_BASE_URL) {
    return env.NEXT_PUBLIC_BACKEND_BASE_URL;
  } else {
    return "";
  }
}

export function getLangGraphBaseURL() {
  if (env.NEXT_PUBLIC_STATIC_WEBSITE_ONLY === "true") {
    // Use mock API in static website mode
    if (typeof window !== "undefined") {
      return `${window.location.origin}/mock/api`;
    }
    // Fallback for SSR
    return "http://localhost:3002/mock/api";
  } else if (env.NEXT_PUBLIC_LANGGRAPH_BASE_URL) {
    return env.NEXT_PUBLIC_LANGGRAPH_BASE_URL;
  } else {
    // LangGraph SDK requires a full URL, construct it from current origin
    if (typeof window !== "undefined") {
      return `${window.location.origin}/api/langgraph`;
    }
    // Fallback for SSR
    return "http://localhost:2026/api/langgraph";
  }
}
