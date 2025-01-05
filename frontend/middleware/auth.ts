import { getAuth, onAuthStateChanged } from 'firebase/auth'
import { defineNuxtRouteMiddleware, navigateTo } from '#app'

export default defineNuxtRouteMiddleware((to) => {
  // Public routes that don't require authentication
  const publicRoutes = ['/', '/login', '/signup']
  
  // Skip middleware on server-side
  if (process.server) {
    return
  }

  return new Promise<void>((resolve) => {
    // Set a timeout of 10 seconds
    const timeoutId = setTimeout(() => {
      console.log('Auth check timed out')
      resolve(navigateTo('/login') as unknown as void)
    }, 10000)

    try {
      const auth = getAuth()
      const unsubscribe = onAuthStateChanged(auth, 
        (user) => {
          clearTimeout(timeoutId)
          unsubscribe() // Clean up the listener
          console.log('Auth state changed:', { user: user?.email, path: to.path })

          // If user is authenticated and trying to access public routes
          if (user && publicRoutes.includes(to.path)) {
            console.log('Authenticated user trying to access public route, redirecting to dashboard')
            resolve(navigateTo('/dashboard') as unknown as void)
            return
          }

          // If user is not authenticated and trying to access protected route
          if (!user && !publicRoutes.includes(to.path)) {
            console.log('Unauthenticated user trying to access protected route')
            resolve(navigateTo('/login') as unknown as void)
            return
          }

          // Allow access to public routes for unauthenticated users
          // or protected routes for authenticated users
          console.log('Access granted')
          resolve()
        },
        (error) => {
          clearTimeout(timeoutId)
          unsubscribe()
          console.error('Auth state check failed:', error)
          resolve(navigateTo('/login') as unknown as void)
        }
      )
    } catch (error) {
      clearTimeout(timeoutId)
      console.error('Firebase initialization error:', error)
      resolve(navigateTo('/login') as unknown as void)
    }
  })
})
