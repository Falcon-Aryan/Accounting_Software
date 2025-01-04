import { initializeApp, FirebaseApp } from 'firebase/app'
import { getAuth, Auth } from 'firebase/auth'
import { firebaseConfig } from '../config/firebase.config'
import { defineNuxtPlugin } from 'nuxt/app'

let app: FirebaseApp | undefined
let auth: Auth | undefined

export default defineNuxtPlugin(() => {
  if (!app) {
    try {
      // Initialize Firebase only on client-side
      if (process.client) {
        console.log('Initializing Firebase...')
        app = initializeApp(firebaseConfig)
        auth = getAuth(app)
        console.log('Firebase initialized successfully')
      }
    } catch (error) {
      console.error('Error initializing Firebase:', error)
    }
  }

  return {
    provide: {
      firebaseApp: app,
      firebaseAuth: auth
    }
  }
})
