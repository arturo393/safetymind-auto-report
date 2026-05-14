import { useQuery } from "@tanstack/react-query"

export function useOllamaStatus() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080"

  const { data } = useQuery({
    queryKey: ["ollama"],
    queryFn: async () => {
      const res = await fetch("/api/ollama/health")
      return res.json() as Promise<{ status: string }>
    },
    staleTime: 30 * 1000,
    retry: 1,
    refetchInterval: 30 * 1000,
  })

  return data?.status || "unknown"
}

export function useProjects() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080"

  const { data, isLoading, error } = useQuery({
    queryKey: ["projects"],
    queryFn: async () => {
      const res = await fetch("/api/projects")
      if (!res.ok) throw new Error("Sync Failure")
      return res.json() as Promise<Record<string, string>>
    },
    staleTime: 5 * 60 * 1000,
    retry: 3,
  })

  const projects = data || (error ? { "SM-RESILIENT": "Modo Emergencia Activo" } : {})
  
  return { 
    projects, 
    loading: isLoading, 
    error: error ? (error as Error).message : null 
  }
}