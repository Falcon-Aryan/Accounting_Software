<template>
  <aside class="w-64 bg-white border-r border-gray-200 h-screen fixed z-50 flex flex-col">
    <!-- Logo -->
    <div class="px-6 py-4 border-b border-gray-200">
      <h1 class="text-xl font-bold text-gray-900">Accounting Software</h1>
    </div>

    <!-- Navigation -->
    <nav class="mt-4 flex-grow">
      <ul class="space-y-2">
        <!-- Dashboard -->
        <li>
          <a @click.prevent="handleNavigation('/dashboard')" class="flex items-center px-6 py-2 text-gray-700 hover:bg-gray-100 cursor-pointer">
            <span>Dashboard</span>
          </a>
        </li>

        <!-- Sales with Dropdown -->
        <li class="relative group">
          <div class="flex items-center justify-between px-6 py-2 text-gray-700 hover:bg-gray-100 cursor-pointer">
            <span>Sales</span>
            <span class="transform group-hover:rotate-90 transition-transform">›</span>
          </div>
          <ul class="hidden group-hover:block absolute left-full top-0 w-48 bg-white border border-gray-200 shadow-lg">
            <li>
              <a @click.prevent="handleNavigation('/estimates')" class="block px-4 py-2 text-gray-700 hover:bg-gray-100 cursor-pointer">Estimates</a>
            </li>
            <li>
              <a @click.prevent="handleNavigation('/invoices')" class="block px-4 py-2 text-gray-700 hover:bg-gray-100 cursor-pointer">Invoices</a>
            </li>
            <li>
              <a @click.prevent="handleNavigation('/prodServ')" class="block px-4 py-2 text-gray-700 hover:bg-gray-100 cursor-pointer">Products & Services</a>
            </li>
            <li>
              <a @click.prevent="handleNavigation('/customers')" class="block px-4 py-2 text-gray-700 hover:bg-gray-100 cursor-pointer">Customers</a>
            </li>
          </ul>
        </li>

        <!-- Transactions with Dropdown -->
        <li class="relative group">
          <div class="flex items-center justify-between px-6 py-2 text-gray-700 hover:bg-gray-100 cursor-pointer">
            <span>Transactions</span>
            <span class="transform group-hover:rotate-90 transition-transform">›</span>
          </div>
          <ul class="hidden group-hover:block absolute left-full top-0 w-48 bg-white border border-gray-200 shadow-lg">
            <li>
              <a @click.prevent="handleNavigation('/transactions')" class="block px-4 py-2 text-gray-700 hover:bg-gray-100 cursor-pointer">All Transactions</a>
            </li>
            <li>
              <a @click.prevent="handleNavigation('/chart-of-accounts')" class="block px-4 py-2 text-gray-700 hover:bg-gray-100 cursor-pointer">Chart of Accounts</a>
            </li>
          </ul>
        </li>

        <!-- Expenses -->
        <li class="relative group">
          <div class="flex items-center justify-between px-6 py-2 text-gray-700 hover:bg-gray-100 cursor-pointer">
            <span>Expenses</span>
            <span class="transform group-hover:rotate-90 transition-transform">›</span>
          </div>
          <ul class="hidden group-hover:block absolute left-full top-0 w-48 bg-white border border-gray-200 shadow-lg">
            <li>
              <a @click.prevent="handleNavigation('/expenses')" class="block px-4 py-2 text-gray-700 hover:bg-gray-100 cursor-pointer">Expenses</a>
            </li>
            <li>
              <a @click.prevent="handleNavigation('/expenses/bills')" class="block px-4 py-2 text-gray-700 hover:bg-gray-100 cursor-pointer">Bills</a>
            </li>
            <li>
              <a @click.prevent="handleNavigation('/expenses/vendors')" class="block px-4 py-2 text-gray-700 hover:bg-gray-100 cursor-pointer">Vendors</a>
            </li>
          </ul>
        </li>

        <!-- Reports -->
        <li>
          <a @click.prevent="handleNavigation('/reports')" class="flex items-center px-6 py-2 text-gray-700 hover:bg-gray-100 cursor-pointer">
            <span>Reports</span>
          </a>
        </li>

        <!-- Settings -->
        <li>
          <a @click.prevent="handleNavigation('/settings')" class="flex items-center px-6 py-2 text-gray-700 hover:bg-gray-100 cursor-pointer">
            <span>Settings</span>
          </a>
        </li>
      </ul>
    </nav>

    <!-- Logout Button -->
    <div class="border-t border-gray-200 p-4">
      <a @click.prevent="handleLogout" class="w-full px-4 py-2 text-red-600 hover:bg-gray-100 rounded-md flex items-center cursor-pointer">
        <span class="flex-grow">Logout</span>
      </a>
    </div>
  </aside>
</template>

<script setup>
import { useUserSync } from '~/composables/useUserSync'
import { getAuth, signOut } from 'firebase/auth'
import { useRouter } from 'vue-router'

const router = useRouter()
const { syncUser } = useUserSync()

// Function to handle navigation with user sync
const handleNavigation = async (path) => {
  await syncUser()
  router.push(path)
}

const handleLogout = async () => {
  try {
    const auth = getAuth()
    await signOut(auth)
    router.push('/login')
  } catch (error) {
    console.error('Error signing out:', error)
  }
}
</script>

<style scoped>
.group:hover .group-hover\:block {
  display: block;
}

.group:hover .group-hover\:rotate-90 {
  transform: rotate(90deg);
}
</style>