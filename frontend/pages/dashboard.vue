<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Navigation Bar -->
    <nav class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <h1 class="text-xl font-semibold">Dashboard</h1>
          </div>
          <div class="flex items-center space-x-4">
            <button
              @click="handleLogout"
              class="p-2 text-gray-600 hover:text-gray-900 rounded-full hover:bg-gray-100"
              title="Logout"
            >
              <span class="mr-2">Logout</span>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-6 w-6 inline-block"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                />
              </svg>
            </button>
            <NuxtLink 
              to="/settings"
              class="p-2 text-gray-600 hover:text-gray-900 rounded-full hover:bg-gray-100"
              title="Settings"
            >
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                class="h-6 w-6" 
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor"
              >
                <path 
                  stroke-linecap="round" 
                  stroke-linejoin="round" 
                  stroke-width="2" 
                  d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                />
                <path 
                  stroke-linecap="round" 
                  stroke-linejoin="round" 
                  stroke-width="2" 
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
            </NuxtLink>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="bg-white shadow rounded-lg p-6">
        <h2 class="text-lg font-medium mb-4">Welcome {{ currentUser?.email }}</h2>
        
        <!-- Quick Actions -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <!-- Add your dashboard content here -->
        </div>

        <!-- Recent Activity -->
        <div class="mt-8">
          <h3 class="text-lg font-medium mb-4">Recent Activity</h3>
          <div class="bg-gray-50 rounded-lg p-4">
            <p v-if="!recentActivity.length" class="text-sm text-gray-600">No recent activity to display</p>
            <ul v-else class="space-y-2">
              <li v-for="activity in recentActivity" :key="activity.id" class="text-sm text-gray-600">
                {{ activity.description }}
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
definePageMeta({
  middleware: ['auth']
})

import { ref, onMounted } from 'vue'
import { useFirebaseAuth } from '../composables/useFirebaseAuth'
import { useRuntimeConfig } from '#app'
import { initializeApp } from 'firebase/app'
import { firebaseConfig } from '../config/firebase.config'
import { getAuth, onAuthStateChanged } from 'firebase/auth'

const { user, logout } = useFirebaseAuth()
const config = useRuntimeConfig()
const currentUser = ref(null)
const recentActivity = ref([])
const estimatesSummary = ref({})
const invoicesSummary = ref({})
const customersSummary = ref({})

// Initialize Firebase
const app = initializeApp(firebaseConfig)
const auth = getAuth(app)

onAuthStateChanged(auth, (user) => {
  currentUser.value = user
  if (user) {
    fetchDashboardData()
  }
})

async function getIdToken() {
  const user = auth.currentUser
  if (!user) {
    throw new Error('No authenticated user')
  }
  return user.getIdToken()
}
async function fetchDashboardData() {
  try {
    const token = await getIdToken()
    
    // Fetch recent activity data
    const activityResponse = await fetch(`${config.public.apiBase}/api/activity/recent`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    recentActivity.value = await activityResponse.json()

    // Fetch estimates summary
    const estimatesResponse = await fetch(`${config.public.apiBase}/api/estimates/summary`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    estimatesSummary.value = await estimatesResponse.json()

    // Fetch invoices summary
    const invoicesResponse = await fetch(`${config.public.apiBase}/api/invoices/summary`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    invoicesSummary.value = await invoicesResponse.json()

    // Fetch customers summary
    const customersResponse = await fetch(`${config.public.apiBase}/api/customers/summary`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    customersSummary.value = await customersResponse.json()
  } catch (error) {
    console.error('Error fetching dashboard data:', error)
  }
}

onMounted(() => {
  if (auth.currentUser) {
    fetchDashboardData()
  }
})

const handleLogout = async () => {
  await logout()
}
</script>