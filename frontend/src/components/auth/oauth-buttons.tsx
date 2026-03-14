"use client";

import { Button } from "@/components/ui/button";
import { Github, Mail } from "lucide-react";
import { getBackendBaseURL } from "@/core/config";

interface OAuthButtonsProps {
  className?: string;
}

export function OAuthButtons({ className }: OAuthButtonsProps) {
  const backendURL = getBackendBaseURL() || "http://localhost:8001";

  const handleGithubLogin = () => {
    window.location.href = `${backendURL}/api/oauth/github/authorize`;
  };

  const handleGoogleLogin = () => {
    window.location.href = `${backendURL}/api/oauth/google/authorize`;
  };

  return (
    <div className={className}>
      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <span className="w-full border-t" />
        </div>
        <div className="relative flex justify-center text-xs uppercase">
          <span className="bg-background px-2 text-muted-foreground">
            或者使用
          </span>
        </div>
      </div>
      
      <div className="mt-4 grid gap-2">
        <Button
          variant="outline"
          type="button"
          onClick={handleGithubLogin}
          className="w-full"
        >
          <Github className="mr-2 h-4 w-4" />
          使用 GitHub 登录
        </Button>
        
        <Button
          variant="outline"
          type="button"
          onClick={handleGoogleLogin}
          className="w-full"
        >
          <Mail className="mr-2 h-4 w-4" />
          使用 Google 登录
        </Button>
      </div>
    </div>
  );
}
