import { SignIn } from '@clerk/nextjs';

export default function SignInPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">SoloRealms</h1>
          <p className="text-gray-300">Welcome back, adventurer</p>
        </div>
        <SignIn 
          appearance={{
            elements: {
              formButtonPrimary: 
                "bg-purple-600 hover:bg-purple-700 text-sm normal-case",
              card: "bg-white/10 backdrop-blur-sm border border-white/20",
              headerTitle: "text-white",
              headerSubtitle: "text-gray-300",
              socialButtonsBlockButton: 
                "bg-white/10 border border-white/20 text-white hover:bg-white/20",
              formFieldLabel: "text-gray-200",
              formFieldInput: 
                "bg-white/10 border border-white/20 text-white placeholder:text-gray-400",
              footerActionLink: "text-purple-400 hover:text-purple-300",
            },
          }}
        />
      </div>
    </div>
  );
} 