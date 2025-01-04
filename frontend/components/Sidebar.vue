<template>
  <aside class="w-64 bg-white border-r border-gray-200 h-screen fixed z-50">
    <!-- Logo -->
    <div class="px-6 py-4 border-b border-gray-200">
      <h1 class="text-xl font-bold text-gray-900">Accounting Software</h1>
    </div>

    <!-- Navigation -->
    <nav class="mt-4">
      <ul class="space-y-2">
        <!-- Dashboard -->
        <li>
          <NuxtLink to="/" class="flex items-center px-6 py-2 text-gray-700 hover:bg-gray-100">
            <span>Dashboard</span>
          </NuxtLink>
        </li>

        <!-- Sales with Dropdown -->
        <li class="relative group">
          <div class="flex items-center justify-between px-6 py-2 text-gray-700 hover:bg-gray-100 cursor-pointer">
            <span>Sales</span>
            <span class="transform group-hover:rotate-90 transition-transform">›</span>
          </div>
          <ul class="hidden group-hover:block absolute left-full top-0 w-48 bg-white border border-gray-200 shadow-lg">
            <li>
              <NuxtLink to="/estimates" class="block px-4 py-2 text-gray-700 hover:bg-gray-100">Estimates</NuxtLink>
            </li>
            <li>
              <NuxtLink to="/invoices" class="block px-4 py-2 text-gray-700 hover:bg-gray-100">Invoices</NuxtLink>
            </li>
            <li>
              <NuxtLink to="/prodServ" class="block px-4 py-2 text-gray-700 hover:bg-gray-100">Products & Services</NuxtLink>
            </li>
            <li>
              <NuxtLink to="/customers" class="block px-4 py-2 text-gray-700 hover:bg-gray-100">Customers</NuxtLink>
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
              <NuxtLink to="/transactions" class="block px-4 py-2 text-gray-700 hover:bg-gray-100">All Transactions</NuxtLink>
            </li>
            <li>
              <NuxtLink to="/chart-of-accounts" class="block px-4 py-2 text-gray-700 hover:bg-gray-100">Chart of Accounts</NuxtLink>
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
              <NuxtLink to="/expenses" class="block px-4 py-2 text-gray-700 hover:bg-gray-100">Expenses</NuxtLink>
            </li>
            <li>
              <NuxtLink to="/expenses/bills" class="block px-4 py-2 text-gray-700 hover:bg-gray-100">Bills</NuxtLink>
            </li>
            <li>
              <NuxtLink to="/expenses/vendors" class="block px-4 py-2 text-gray-700 hover:bg-gray-100">Vendors</NuxtLink>
            </li>
          </ul>
        </li>

        <!-- Reports -->
        <li>
          <NuxtLink to="/reports" class="flex items-center px-6 py-2 text-gray-700 hover:bg-gray-100">
            <span>Reports</span>
          </NuxtLink>
        </li>

        <!-- Settings -->
        <li>
          <NuxtLink to="/settings" class="flex items-center px-6 py-2 text-gray-700 hover:bg-gray-100">
            <span>Settings</span>
          </NuxtLink>
        </li>
      </ul>
    </nav>
  </aside>
</template>

<script setup>
import { useRoute } from '#app'
const route = useRoute()
</script>

<style scoped>
.group:hover .group-hover\:block {
  display: block;
}

.group:hover .group-hover\:rotate-90 {
  transform: rotate(90deg);
}
</style>