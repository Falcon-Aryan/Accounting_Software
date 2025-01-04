import { createUserWithEmailAndPassword, signInWithEmailAndPassword, signOut, User, Auth } from 'firebase/auth'
import { useNuxtApp, useState, navigateTo } from 'nuxt/app'
import { ref } from 'vue'

export const useFirebaseAuth = () => {
  const { $firebaseAuth } = useNuxtApp()
  const user = useState<User | null>('user', () => null)
  const error = ref('')
  const loading = ref(false)

  // Type guard to check if auth is properly initialized
  const isAuthInitialized = (auth: any): auth is Auth => {
    return auth && typeof auth.createUserWithEmailAndPassword === 'function'
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
    if (!$firebaseAuth || !isAuthInitialized($firebaseAuth)) {
      console.error('Firebase Auth not initialized')
      error.value = 'Authentication service not initialized'
      return
    }

    error.value = ''
    loading.value = true
    
    try {
      console.log('Attempting to sign up with email:', email)
      const userCredential = await createUserWithEmailAndPassword($firebaseAuth, email, password)
      user.value = userCredential.user
      console.log('Sign up successful')
      await navigateTo('/dashboard')
    } catch (e: any) {
      console.error('Sign up error:', e)
      error.value = getErrorMessage(e.code)
    } finally {
      loading.value = false
    }
  }

  const signIn = async (email: string, password: string) => {
    if (!$firebaseAuth || !isAuthInitialized($firebaseAuth)) {
      console.error('Firebase Auth not initialized')
      error.value = 'Authentication service not initialized'
      return
    }

    error.value = ''
    loading.value = true
    
    try {
      console.log('Attempting to sign in with email:', email)
      const userCredential = await signInWithEmailAndPassword($firebaseAuth, email, password)
      user.value = userCredential.user
      console.log('Sign in successful')
      await navigateTo('/dashboard')
    } catch (e: any) {
      console.error('Sign in error:', e)
      error.value = getErrorMessage(e.code)
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    if (!$firebaseAuth || !isAuthInitialized($firebaseAuth)) {
      console.error('Firebase Auth not initialized')
      error.value = 'Authentication service not initialized'
      return
    }

    error.value = ''
    loading.value = true
    
    try {
      await signOut($firebaseAuth)
      user.value = null
      console.log('Logout successful')
      await navigateTo('/')
    } catch (e: any) {
      console.error('Logout error:', e)
      error.value = getErrorMessage(e.code)
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
