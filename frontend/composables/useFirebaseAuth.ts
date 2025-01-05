import { createUserWithEmailAndPassword, signInWithEmailAndPassword, signOut } from 'firebase/auth'
import type { Auth, User } from 'firebase/auth'
import { useNuxtApp, useState, navigateTo, useRuntimeConfig } from 'nuxt/app'
import { ref } from 'vue'

export const useFirebaseAuth = () => {
  const { $firebaseAuth } = useNuxtApp()
  const user = useState<User | null>('user', () => null)
  const error = ref('')
  const loading = ref(false)

  // Type guard to check if auth is properly initialized
  const isAuthInitialized = (auth: any): auth is Auth => {
    return auth && typeof auth.signInWithEmailAndPassword === 'function'
  }

  const getErrorMessage = (code: string) => {
    console.error('Firebase Auth Error:', code)
    switch (code) {
      case 'auth/email-already-in-use':
        return 'This email is already registered. Please sign in instead.'
      case 'auth/invalid-email':
        return 'Please enter a valid email address.'
      case 'auth/operation-not-allowed':
        return 'Email/password accounts are not enabled. Please contact support.'
      case 'auth/weak-password':
        return 'Please choose a stronger password (at least 6 characters).'
      case 'auth/user-disabled':
        return 'This account has been disabled. Please contact support.'
      case 'auth/user-not-found':
      case 'auth/wrong-password':
        return 'Invalid email or password.'
      case 'auth/api-key-not-valid-please-pass-a-valid-api-key':
        console.error('Invalid API Key. Please check Firebase configuration.')
        return 'Authentication service configuration error. Please try again later.'
      default:
        console.error('Unhandled Firebase error:', code)
        return `Authentication error: ${code}`
    }
  }

  const signUp = async (email: string, password: string) => {
    error.value = ''
    loading.value = true

    try {
      const config = useRuntimeConfig()
      const response = await fetch(`${config.public.apiBase}/api/users/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password
        }),
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.message || 'Failed to create user')
      }

      const data = await response.json()
      user.value = data.user

      // Sync user data after successful creation
      await fetch(`${config.public.apiBase}/api/users/sync`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      })

      await navigateTo('/dashboard')
    } catch (e: any) {
      error.value = e.message || 'Failed to create account'
      console.error('Signup error:', e)
    } finally {
      loading.value = false
    }
  }

  const signIn = async (email: string, password: string) => {
    if (!$firebaseAuth) {
      console.error('Firebase Auth not initialized')
      error.value = 'Authentication service not initialized'
      return
    }

    error.value = ''
    loading.value = true

    try {
      const userCredential = await signInWithEmailAndPassword($firebaseAuth, email, password)
      user.value = userCredential.user
      await navigateTo('/dashboard')
    } catch (e: any) {
      error.value = getErrorMessage(e.code)
      console.error('Sign in error:', e)
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    if (!$firebaseAuth) {
      console.error('Firebase Auth not initialized')
      error.value = 'Authentication service not initialized'
      return
    }

    error.value = ''
    loading.value = true

    try {
      await signOut($firebaseAuth)
      user.value = null
      await navigateTo('/')
    } catch (e: any) {
      error.value = getErrorMessage(e.code)
      console.error('Logout error:', e)
    } finally {
      loading.value = false
    }
  }

  return {
    user,
    error,
    loading,
    signUp,
    signIn,
    logout
  }
}
