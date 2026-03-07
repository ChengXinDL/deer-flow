"use client";

import { Client as LangGraphClient } from "@langchain/langgraph-sdk/client";

import { getLangGraphBaseURL } from "../config";
import { env } from "@/env";

let _singleton: LangGraphClient | null = null;
export function getAPIClient(): LangGraphClient {
  const currentUrl = getLangGraphBaseURL();
  
  // If we're in static website mode or the URL has changed, create a new client
  if (!_singleton || env.NEXT_PUBLIC_STATIC_WEBSITE_ONLY === "true") {
    _singleton = new LangGraphClient({
      apiUrl: currentUrl,
    });
  }
  
  return _singleton;
}
