import { Metadata } from "next";

export const metadata: Metadata = {
  title: "认证 - MagicFlow",
  description: "登录或注册 MagicFlow 账号",
};

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-background">
      {children}
    </div>
  );
}
