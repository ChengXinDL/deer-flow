import type { HumanMessage } from "@langchain/core/messages";
import type { AIMessage } from "@langchain/langgraph-sdk";
import type { ThreadsClient } from "@langchain/langgraph-sdk/client";
import { useStream, type UseStream } from "@langchain/langgraph-sdk/react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";

import type { PromptInputMessage } from "@/components/ai-elements/prompt-input";

import { getAPIClient, resolveGraphIdToAssistantId } from "../api";
import { useLocalSettings } from "../settings";
import { useUpdateSubtask } from "../tasks/context";
import { uploadFiles } from "../uploads";

import type {
  AgentThread,
  AgentThreadContext,
  AgentThreadState,
} from "./types";

export function useThreadStream({
  threadId,
  isNewThread,
  onFinish,
}: {
  isNewThread: boolean;
  threadId: string | null | undefined;
  onFinish?: (state: AgentThreadState) => void;
}) {
  const queryClient = useQueryClient();
  const updateSubtask = useUpdateSubtask();
  const [settings] = useLocalSettings();
  const graphId = settings.agent.assistant_id;
  const [resolvedAssistantId, setResolvedAssistantId] = useState<string | null>(null);
  
  useEffect(() => {
    let isMounted = true;
    const resolveId = async () => {
      const assistantId = await resolveGraphIdToAssistantId(graphId);
      if (isMounted && assistantId) {
        setResolvedAssistantId(assistantId);
      }
    };
    resolveId();
    return () => {
      isMounted = false;
    };
  }, [graphId]);
  
  const thread = useStream<AgentThreadState>({
    client: getAPIClient(),
    assistantId: resolvedAssistantId || graphId,
    threadId: isNewThread ? undefined : threadId,
    reconnectOnMount: true,
    fetchStateHistory: { limit: 1 },
    onCustomEvent(event: unknown) {
      console.info(event);
      if (
        typeof event === "object" &&
        event !== null &&
        "type" in event &&
        event.type === "task_running"
      ) {
        const e = event as {
          type: "task_running";
          task_id: string;
          message: AIMessage;
        };
        updateSubtask({ id: e.task_id, latestMessage: e.message });
      }
    },
    onFinish(state) {
      onFinish?.(state.values);
      queryClient.setQueriesData(
        {
          queryKey: ["threads", "search"],
          exact: false,
        },
        (oldData: Array<AgentThread>) => {
          return oldData.map((t) => {
            if (t.thread_id === threadId) {
              return {
                ...t,
                values: {
                  ...t.values,
                  title: state.values.title,
                },
              };
            }
            return t;
          });
        },
      );
    },
  });
  
  return thread;
}

export function useSubmitThread({
  threadId,
  thread,
  threadContext,
  isNewThread,
  afterSubmit,
}: {
  isNewThread: boolean;
  threadId: string | null | undefined;
  thread: UseStream<AgentThreadState>;
  threadContext: Omit<AgentThreadContext, "thread_id">;
  afterSubmit?: () => void;
}) {
  const queryClient = useQueryClient();
  const [settings] = useLocalSettings();
  const callback = useCallback(
    async (message: PromptInputMessage) => {
      const text = message.text.trim();

      if (message.files && message.files.length > 0) {
        try {
          const filePromises = message.files.map(async (fileUIPart) => {
            if (fileUIPart.url && fileUIPart.filename) {
              try {
                const response = await fetch(fileUIPart.url);
                const blob = await response.blob();
                return new File([blob], fileUIPart.filename, {
                  type: fileUIPart.mediaType || blob.type,
                });
              } catch (error) {
                console.error(
                  `Failed to fetch file ${fileUIPart.filename}:`,
                  error,
                );
                return null;
              }
            }
            return null;
          });

          const conversionResults = await Promise.all(filePromises);
          const files = conversionResults.filter(
            (file): file is File => file !== null,
          );
          const failedConversions = conversionResults.length - files.length;

          if (failedConversions > 0) {
            throw new Error(
              `Failed to prepare ${failedConversions} attachment(s) for upload. Please retry.`,
            );
          }

          if (!threadId) {
            throw new Error("Thread is not ready for file upload.");
          }

          if (files.length > 0) {
            await uploadFiles(threadId, files);
          }
        } catch (error) {
          console.error("Failed to upload files:", error);
          const errorMessage =
            error instanceof Error ? error.message : "Failed to upload files.";
          toast.error(errorMessage);
          throw error;
        }
      }

      const configurable: Record<string, unknown> = {
        thread_id: threadId,
      };
      
      const graphId = settings.agent.assistant_id;
      if (graphId === "sql-agent") {
        configurable.db_url = process.env.NEXT_PUBLIC_DB_URL || "mysql+mysqlconnector://app:sykj_1234A@192.168.8.221:3307/bim_data";
        configurable.building_id = process.env.NEXT_PUBLIC_BUILDING_ID || "335834679343";
      }
      
      const submitConfig = {
        threadId: isNewThread ? threadId! : undefined,
        streamSubgraphs: true,
        streamResumable: true,
        streamMode: ["values", "messages-tuple", "custom"] as const,
        config: {
          recursion_limit: 1000,
          configurable: configurable,
        },
      };

      await thread.submit(
        {
          messages: [
            {
              type: "human",
              content: [
                {
                  type: "text",
                  text,
                },
              ],
            },
          ] as HumanMessage[],
        },
        submitConfig
      );
      void queryClient.invalidateQueries({ queryKey: ["threads", "search"] });
      afterSubmit?.();
    },
    [thread, isNewThread, threadId, threadContext, queryClient, afterSubmit, settings],
  );
  return callback;
}

export function useThreads(
  params: Parameters<ThreadsClient["search"]>[0] = {
    limit: 50,
    sortBy: "updated_at",
    sortOrder: "desc",
    select: ["thread_id", "updated_at", "values"],
  },
) {
  const apiClient = getAPIClient();
  return useQuery<AgentThread[]>({
    queryKey: ["threads", "search", params],
    queryFn: async () => {
      const response = await apiClient.threads.search<AgentThreadState>(params);
      return response as AgentThread[];
    },
    refetchOnWindowFocus: false,
  });
}

export function useDeleteThread() {
  const queryClient = useQueryClient();
  const apiClient = getAPIClient();
  return useMutation({
    mutationFn: async ({ threadId }: { threadId: string }) => {
      await apiClient.threads.delete(threadId);
    },
    onSuccess(_, { threadId }) {
      queryClient.setQueriesData(
        {
          queryKey: ["threads", "search"],
          exact: false,
        },
        (oldData: Array<AgentThread>) => {
          return oldData.filter((t) => t.thread_id !== threadId);
        },
      );
    },
  });
}

export function useRenameThread() {
  const queryClient = useQueryClient();
  const apiClient = getAPIClient();
  return useMutation({
    mutationFn: async ({
      threadId,
      title,
    }: {
      threadId: string;
      title: string;
    }) => {
      await apiClient.threads.updateState(threadId, {
        values: { title },
      });
    },
    onSuccess(_, { threadId, title }) {
      queryClient.setQueriesData(
        {
          queryKey: ["threads", "search"],
          exact: false,
        },
        (oldData: Array<AgentThread>) => {
          return oldData.map((t) => {
            if (t.thread_id === threadId) {
              return {
                ...t,
                values: {
                  ...t.values,
                  title,
                },
              };
            }
            return t;
          });
        },
      );
    },
  });
}
