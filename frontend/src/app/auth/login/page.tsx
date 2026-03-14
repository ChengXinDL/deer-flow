"use client";

import { useState, useEffect, useRef, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Checkbox } from "@/components/ui/checkbox";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { useAuth } from "@/core/auth";
import { getBackendBaseURL } from "@/core/config";
import { Loader2, Mail, Lock, Eye, EyeOff, Phone, LogIn, Github, ArrowLeft } from "lucide-react";

function LoginContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login, forgotPassword, isLoading, error, clearError } = useAuth();
  const backendURL = getBackendBaseURL() || "http://localhost:8001";
  
  const [loginType, setLoginType] = useState<"phone" | "email">("email");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [wechatState, setWechatState] = useState("");
  const [wechatQrCodeUrl, setWechatQrCodeUrl] = useState("");
  const [wechatStatus, setWechatStatus] = useState<"pending" | "scanned" | "confirmed" | "expired">("pending");
  const [wechatLoading, setWechatLoading] = useState(false);
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [forgotPasswordEmail, setForgotPasswordEmail] = useState("");
  const [forgotPasswordLoading, setForgotPasswordLoading] = useState(false);
  const [forgotPasswordError, setForgotPasswordError] = useState<string | null>(null);
  const [forgotPasswordSuccess, setForgotPasswordSuccess] = useState(false);
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const registered = searchParams.get("registered");
    if (registered === "true") {
      // 可以显示注册成功提示
    }
  }, [searchParams]);

  useEffect(() => {
    fetchWechatQrCode();
    
    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, []);

  const fetchWechatQrCode = async () => {
    setWechatLoading(true);
    try {
      const response = await fetch(`${backendURL}/api/oauth/wechat/qrcode`);
      const data = await response.json();
      setWechatState(data.state);
      setWechatQrCodeUrl(data.qr_code_url);
      startPolling(data.state);
    } catch (err) {
      console.error("获取微信二维码失败:", err);
    } finally {
      setWechatLoading(false);
    }
  };

  const startPolling = (state: string) => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
    }

    pollIntervalRef.current = setInterval(async () => {
      try {
        const response = await fetch(`${backendURL}/api/oauth/wechat/status/${state}`);
        const data = await response.json();
        
        setWechatStatus(data.status);

        if (data.status === "confirmed" && data.user) {
          if (pollIntervalRef.current) {
            clearInterval(pollIntervalRef.current);
          }
          router.push("/workspace/chats/new");
        } else if (data.status === "expired") {
          if (pollIntervalRef.current) {
            clearInterval(pollIntervalRef.current);
          }
          setWechatState("");
          setWechatStatus("pending");
        }
      } catch (err) {
        console.error("查询微信登录状态失败:", err);
      }
    }, 2000);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();

    try {
      await login({
        login_type: loginType,
        identifier: loginType === "phone" ? phone : email,
        password,
        remember_me: rememberMe,
      });
      
      router.push("/workspace/chats/new");
    } catch (err) {
      // 错误已在 hook 中处理
    }
  };

  const handleForgotPasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setForgotPasswordError(null);
    setForgotPasswordSuccess(false);
    setForgotPasswordLoading(true);

    try {
      await forgotPassword({ identifier: forgotPasswordEmail });
      setForgotPasswordSuccess(true);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "发送重置链接失败";
      setForgotPasswordError(errorMessage);
    } finally {
      setForgotPasswordLoading(false);
    }
  };

  const handleGithubLogin = () => {
    window.location.href = `${backendURL}/api/oauth/github/authorize`;
  };

  const handleGoogleLogin = () => {
    window.location.href = `${backendURL}/api/oauth/google/authorize`;
  };

  const refreshWechatQrCode = () => {
    setWechatState("");
    setWechatQrCodeUrl("");
    setWechatStatus("pending");
    fetchWechatQrCode();
  };

  const handleBackToLogin = () => {
    setShowForgotPassword(false);
    setForgotPasswordEmail("");
    setForgotPasswordError(null);
    setForgotPasswordSuccess(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <Card className="w-full max-w-4xl p-0 overflow-hidden">
        <div className="flex">
          {/* WeChat QR Code Section */}
          <div className="w-[320px] bg-gradient-to-br from-indigo-600 to-purple-700 p-8 flex flex-col items-center justify-center text-white flex-shrink-0">
            <div className="text-center w-full flex flex-col items-center">
              <h3 className="text-xl font-bold mb-3">微信登录</h3>
              <p className="text-indigo-100 text-sm mb-5">扫码即可快速登录</p>
              
              <Card className="bg-white p-3 rounded-xl shadow-lg border-0">
                {wechatLoading ? (
                  <div className="w-40 h-40 bg-gray-100 flex items-center justify-center rounded-lg">
                    <Loader2 className="h-10 w-10 animate-spin text-gray-400" />
                  </div>
                ) : wechatQrCodeUrl ? (
                  <img 
                    src={wechatQrCodeUrl}
                    alt="微信登录二维码"
                    className="w-40 h-40"
                    onError={() => {
                      console.error("二维码加载失败");
                      setWechatQrCodeUrl("");
                    }}
                  />
                ) : (
                  <div className="w-40 h-40 bg-gray-100 flex items-center justify-center rounded-lg">
                    <div className="text-center text-gray-400">
                      <p className="text-sm">二维码加载失败</p>
                      <Button 
                        variant="link" 
                        size="sm" 
                        onClick={refreshWechatQrCode}
                        className="mt-2"
                      >
                        点击刷新
                      </Button>
                    </div>
                  </div>
                )}
              </Card>
              
              {wechatStatus === "scanned" && (
                <p className="text-sm text-green-300 mt-4">已扫描，请在手机上确认登录</p>
              )}
              {wechatStatus === "expired" && (
                <div className="mt-4">
                  <p className="text-sm text-red-300 mb-2">二维码已过期</p>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={refreshWechatQrCode}
                    className="bg-white/10 border-white/20 text-white hover:bg-white/20"
                  >
                    刷新二维码
                  </Button>
                </div>
              )}
              {wechatStatus === "pending" && !wechatLoading && (
                <p className="text-sm text-indigo-200 mt-4">请使用微信扫描二维码</p>
              )}
            </div>
          </div>

          {/* Right Section - Login Form or Forgot Password */}
          <div className="flex-1 p-7 flex flex-col min-h-[520px]">
            {showForgotPassword ? (
              /* Forgot Password Panel */
              <div className="flex flex-col h-full">
                <CardHeader className="p-0 mb-4">
                  <div className="flex items-center gap-2">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={handleBackToLogin}
                      className="h-8 w-8 -ml-2"
                    >
                      <ArrowLeft className="h-4 w-4" />
                    </Button>
                    <CardTitle className="text-2xl font-bold text-gray-900">
                      忘记密码
                    </CardTitle>
                  </div>
                  <CardDescription>
                    输入您的邮箱地址，我们将发送重置链接
                  </CardDescription>
                </CardHeader>

                <div className="flex-1 flex flex-col">
                  {forgotPasswordError && (
                    <Alert variant="destructive" className="mb-3">
                      <AlertDescription>{forgotPasswordError}</AlertDescription>
                    </Alert>
                  )}

                  {forgotPasswordSuccess ? (
                    <div className="flex-1 flex flex-col items-center justify-center text-center">
                      <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
                        <Mail className="h-8 w-8 text-green-600" />
                      </div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">
                        邮件已发送
                      </h3>
                      <p className="text-sm text-gray-600 mb-4">
                        如果账号存在，重置链接已发送到您的邮箱
                      </p>
                      <p className="text-xs text-gray-500 mb-6">
                        请检查您的收件箱（包括垃圾邮件文件夹）。重置链接将在 15 分钟后失效。
                      </p>
                      <Button
                        onClick={handleBackToLogin}
                        className="bg-indigo-600 hover:bg-indigo-700"
                      >
                        返回登录
                      </Button>
                    </div>
                  ) : (
                    <form className="space-y-4 flex-1 flex flex-col" onSubmit={handleForgotPasswordSubmit}>
                      <div className="space-y-2">
                        <Label htmlFor="forgot-email">邮箱地址</Label>
                        <div className="relative">
                          <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                          <Input
                            id="forgot-email"
                            name="forgot-email"
                            type="email"
                            autoComplete="email"
                            required
                            value={forgotPasswordEmail}
                            onChange={(e) => setForgotPasswordEmail(e.target.value)}
                            className="pl-12"
                            placeholder="请输入邮箱地址"
                          />
                        </div>
                      </div>

                      <div className="flex-1"></div>

                      <Button
                        type="submit"
                        disabled={forgotPasswordLoading}
                        className="w-full bg-indigo-600 hover:bg-indigo-700"
                      >
                        {forgotPasswordLoading ? (
                          <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            发送中...
                          </>
                        ) : (
                          "发送重置链接"
                        )}
                      </Button>
                    </form>
                  )}
                </div>
              </div>
            ) : (
              /* Login Form Panel */
              <>
                <CardHeader className="p-0 mb-4">
                  <CardTitle className="text-2xl font-bold text-gray-900">
                    登录
                  </CardTitle>
                  <CardDescription>
                    输入您的账号信息登录
                  </CardDescription>
                </CardHeader>

                <div className="flex-1 flex flex-col">
                  {/* Login Type Tabs */}
                  <Tabs value={loginType} onValueChange={(value) => setLoginType(value as "phone" | "email")} className="w-full">
                    <TabsList className="grid w-full grid-cols-2 mb-4">
                      <TabsTrigger value="email">邮箱登录</TabsTrigger>
                      <TabsTrigger value="phone">手机登录</TabsTrigger>
                    </TabsList>
                  </Tabs>

                  {/* Error Alert */}
                  {error && (
                    <Alert variant="destructive" className="mb-3">
                      <AlertDescription>{error}</AlertDescription>
                    </Alert>
                  )}

                  <form className="space-y-3" onSubmit={handleSubmit}>
                    {/* Phone/Email Input */}
                    {loginType === "phone" ? (
                      <div className="space-y-2">
                        <Label htmlFor="phone" className="sr-only">手机号</Label>
                        <div className="relative">
                          <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                          <Input
                            id="phone"
                            name="phone"
                            type="tel"
                            autoComplete="tel"
                            required
                            value={phone}
                            onChange={(e) => setPhone(e.target.value)}
                            className="pl-12"
                            placeholder="请输入手机号"
                          />
                        </div>
                      </div>
                    ) : (
                      <div className="space-y-2">
                        <Label htmlFor="email" className="sr-only">邮箱</Label>
                        <div className="relative">
                          <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                          <Input
                            id="email"
                            name="email"
                            type="email"
                            autoComplete="email"
                            required
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="pl-12"
                            placeholder="请输入邮箱"
                          />
                        </div>
                      </div>
                    )}

                    {/* Password Input */}
                    <div className="space-y-2">
                      <Label htmlFor="password" className="sr-only">密码</Label>
                      <div className="relative">
                        <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                        <Input
                          id="password"
                          name="password"
                          type={showPassword ? "text" : "password"}
                          autoComplete="current-password"
                          required
                          value={password}
                          onChange={(e) => setPassword(e.target.value)}
                          className="pl-12 pr-12"
                          placeholder="请输入密码"
                        />
                        <Button
                          type="button"
                          variant="ghost"
                          size="icon"
                          onClick={() => setShowPassword(!showPassword)}
                          className="absolute right-1 top-1/2 transform -translate-y-1/2 h-8 w-8 text-gray-400 hover:text-gray-500"
                        >
                          {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                        </Button>
                      </div>
                    </div>

                    {/* Remember Me & Forgot Password */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Checkbox
                          id="remember-me"
                          checked={rememberMe}
                          onCheckedChange={(checked) => setRememberMe(checked as boolean)}
                        />
                        <Label htmlFor="remember-me" className="text-sm text-gray-900 cursor-pointer">
                          记住我
                        </Label>
                      </div>

                      <Button
                        type="button"
                        variant="link"
                        onClick={() => setShowForgotPassword(true)}
                        className="text-sm p-0 h-auto text-indigo-600 hover:text-indigo-500"
                      >
                        忘记密码？
                      </Button>
                    </div>

                    {/* Submit Button */}
                    <Button
                      type="submit"
                      disabled={isLoading}
                      className="w-full bg-indigo-600 hover:bg-indigo-700"
                    >
                      {isLoading ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          登录中...
                        </>
                      ) : (
                        <>
                          <LogIn className="mr-2 h-4 w-4" />
                          登录
                        </>
                      )}
                    </Button>
                  </form>

                  {/* OAuth Login */}
                  <div className="mt-4">
                    <div className="relative">
                      <div className="absolute inset-0 flex items-center">
                        <Separator className="w-full" />
                      </div>
                      <div className="relative flex justify-center text-sm">
                        <span className="px-3 bg-white text-gray-500">或者使用</span>
                      </div>
                    </div>

                    <div className="mt-3 grid grid-cols-2 gap-3">
                      <Button
                        type="button"
                        variant="outline"
                        onClick={handleGithubLogin}
                        className="w-full"
                      >
                        <Github className="h-5 w-5 mr-2" />
                        GitHub 登录
                      </Button>

                      <Button
                        type="button"
                        variant="outline"
                        onClick={handleGoogleLogin}
                        className="w-full"
                      >
                        <svg className="h-5 w-5 mr-2" viewBox="0 0 24 24" fill="currentColor">
                          <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                          <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                          <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                          <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
                        </svg>
                        Google 登录
                      </Button>
                    </div>
                  </div>
                </div>

                {/* Register Link */}
                <div className="text-center text-sm text-gray-600 mt-3">
                  还没有账号？{" "}
                  <Link
                    href="/auth/register"
                    className="font-medium text-indigo-600 hover:text-indigo-500"
                  >
                    立即注册
                  </Link>
                </div>
              </>
            )}
          </div>
        </div>
      </Card>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-background p-4">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      }
    >
      <LoginContent />
    </Suspense>
  );
}
