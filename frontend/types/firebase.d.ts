import { Auth } from 'firebase/auth'
import { FirebaseApp } from 'firebase/app'

declare module '#app' {
  interface NuxtApp {
    $firebaseApp: FirebaseApp
    $firebaseAuth: Auth
  }
}

declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $firebaseApp: FirebaseApp
    $firebaseAuth: Auth
  }
}
