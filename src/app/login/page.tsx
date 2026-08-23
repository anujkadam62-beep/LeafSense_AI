import type { Metadata } from "next";
import { LoginShowcase } from "@/components/LoginShowcase";
import { LoginForm } from "@/components/LoginForm";

export const metadata: Metadata = {
  title: "Login — CoffeeLeaf AI",
};

export default function LoginPage() {
  return (
    <div className="flex min-h-screen w-full flex-col lg:flex-row">
      <LoginShowcase />
      <LoginForm />
    </div>
  );
}
