import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/auth";
import apiClient from "@/lib/api-client";

export function useAuth() {
  const router = useRouter();
  const { user, isAuthenticated, setAuth, logout } = useAuthStore();

  const login = async (email: string, password: string) => {
    const { data } = await apiClient.post("/api/v1/auth/login", { email, password });
    setAuth(data.user, data.access_token, data.refresh_token);
    router.push("/dashboard");
  };

  const register = async (email: string, password: string, full_name: string, workspace_name?: string) => {
    await apiClient.post("/api/v1/auth/register", { email, password, full_name, workspace_name });
  };

  const logoutUser = () => {
    logout();
    router.push("/login");
  };

  return { user, isAuthenticated, login, register, logout: logoutUser };
}
