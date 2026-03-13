import { redirect } from "next/navigation";

export default function AuthPage() {
  // 重定向到登录页面
  redirect("/auth/login");
}
