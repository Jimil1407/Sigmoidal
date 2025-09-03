import AuthCard from "@/components/AuthCard";

export default function SignInPage() {
  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center px-4 py-12">
      <AuthCard mode="signin" />
    </div>
  );
}


