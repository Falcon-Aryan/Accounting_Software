import { initializeApp } from 'firebase/app'
import { getAuth, setPersistence, browserSessionPersistence } from 'firebase/auth'
import { firebaseConfig } from '../config/firebase.config'
import { defineNuxtPlugin } from 'nuxt/app'

export default defineNuxtPlugin(async(nuxtApp) => {
  // Initialize Firebase only on client-side
  if (process.client) {
    try {
      console.log('Initializing Firebase...')
      const app = initializeApp(firebaseConfig)
      const auth = getAuth(app)
      await setPersistence(auth, browserSessionPersistence)
      console.log('Firebase initialized successfully')

      // Provide Firebase instances
      nuxtApp.provide('firebaseApp', app)
      nuxtApp.provide('firebaseAuth', auth)
    } catch (error) {
      console.error('Error initializing Firebase:', error)
      throw error // Re-throw to show the error in the console
    }
  }
})