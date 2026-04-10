import { useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore.js'
import { authApi, usersApi } from '../api/index.js'

export function useAuth() {
  const navigate  = useNavigate()
  const store     = useAuthStore()

  const register = useCallback(async (formData) => {
    const { data } = await authApi.register(formData)
    store.setTokens(data.access_token, data.refresh_token)

    const { data: user } = await usersApi.me()
    store.setUser(user)

    navigate('/feed')
  }, [store, navigate])

  const login = useCallback(async (formData, redirectTo = '/feed') => {
    const { data } = await authApi.login(formData)
    store.setTokens(data.access_token, data.refresh_token)

    const { data: user } = await usersApi.me()
    store.setUser(user)

    navigate(redirectTo)
  }, [store, navigate])

  const logout = useCallback(async () => {
    try {
      await authApi.logout()
    } catch {
      // Blacklist call failed — still clear local state
    } finally {
      store.logout()
      navigate('/login')
    }
  }, [store, navigate])

  const refreshUser = useCallback(async () => {
    const { data } = await usersApi.me()
    store.setUser(data)
  }, [store])

  return {
    user:            store.user,
    isAuthenticated: store.isAuthenticated,
    register,
    login,
    logout,
    refreshUser,
  }
}