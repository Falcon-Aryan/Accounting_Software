import { getAuth } from 'firebase/auth'
import { useRuntimeConfig } from '#app'

export const useUserSync = () => {
  const config = useRuntimeConfig()

  const syncUser = async () => {
    try {
      const auth = getAuth()
      const idToken = await auth.currentUser?.getIdToken()
      
      if (!idToken) {
        console.warn('No user token available for sync')
        return
      }

      const response = await fetch(`${config.public.apiBase}/api/users/sync`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${idToken}`,
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        const data = await response.json()
        console.error('User sync failed:', data.error)
      }
    } catch (error) {
      console.error('Error syncing user:', error)
    }
  }

  return {
    syncUser
  }
}
