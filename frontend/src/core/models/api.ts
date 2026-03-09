import { getBackendBaseURL } from "../config";

import type { Model } from "./types";

export async function loadModels() {
  const baseUrl = getBackendBaseURL();
  const url = `${baseUrl}/api/models`;
  
  console.log("[loadModels] Fetching from:", url);
  
  try {
    const res = await fetch(url, {
      headers: {
        "Accept": "application/json",
      },
    });
    
    if (!res.ok) {
      console.error("[loadModels] HTTP error:", res.status, res.statusText);
      throw new Error(`HTTP error! status: ${res.status}`);
    }
    
    const data = await res.json();
    console.log("[loadModels] Response:", data);
    return data.models as Model[];
  } catch (error) {
    console.error("[loadModels] Fetch error:", error);
    throw error;
  }
}
