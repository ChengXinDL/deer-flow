import { getBackendBaseURL, getLangGraphBaseURL } from "../config";
import type { AgentThread } from "../threads";
import { env } from "@/env";

export function urlOfArtifact({
  filepath,
  threadId,
  download = false,
}: {
  filepath: string;
  threadId: string;
  download?: boolean;
}) {
  const baseURL = env.NEXT_PUBLIC_STATIC_WEBSITE_ONLY === "true" 
    ? getLangGraphBaseURL()
    : getBackendBaseURL();
  return `${baseURL}/threads/${threadId}/artifacts${filepath}${download ? "?download=true" : ""}`;
}

export function extractArtifactsFromThread(thread: AgentThread) {
  return thread.values.artifacts ?? [];
}

export function resolveArtifactURL(absolutePath: string, threadId: string) {
  const baseURL = env.NEXT_PUBLIC_STATIC_WEBSITE_ONLY === "true"
    ? getLangGraphBaseURL()
    : getBackendBaseURL();
  return `${baseURL}/threads/${threadId}/artifacts${absolutePath}`;
}
