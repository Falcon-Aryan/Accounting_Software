<template>
  <div class="min-h-screen bg-gray-100 py-6 px-4 sm:px-6 lg:px-8">
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-2xl font-semibold text-gray-900">Reports</h1>
        <p class="mt-2 text-sm text-gray-500">View and analyze your business data with detailed reports</p>
      </div>

      <!-- Search Bar -->
      <div class="mb-6">
        <div class="max-w-xl">
          <label for="search" class="sr-only">Search reports</label>
          <div class="relative">
            <div class="pointer-events-none absolute inset-y-0 left-0 pl-3 flex items-center">
              <svg class="h-5 w-5 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
              </svg>
            </div>
            <input
              id="search"
              v-model="searchQuery"
              type="text"
              placeholder="Find report by name"
              class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500 sm:text-sm"
            />
          </div>
        </div>
      </div>

      <!-- Report Categories -->
      <div class="space-y-6">
        <!-- Favorites Section -->
        <div class="bg-white shadow rounded-lg overflow-hidden">
          <div class="p-4 border-b border-gray-200">
            <button 
              @click="toggleSection('favorites')" 
              class="flex items-center justify-between w-full text-left"
            >
              <h2 class="text-lg font-medium text-gray-900 flex items-center space-x-2">
                <svg 
                  :class="{'rotate-90': expandedSections.favorites}"
                  class="h-5 w-5 text-gray-500 transform transition-transform duration-200"
                  viewBox="0 0 20 20" 
                  fill="currentColor"
                >
                  <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                </svg>
                <span>Favorites</span>
              </h2>
            </button>
          </div>
          <div v-show="expandedSections.favorites" class="p-4">
            <div class="grid grid-cols-1 gap-4">
              <ReportLink
                v-for="report in favoriteReports"
                :key="report.id"
                :report="report"
                @toggle-favorite="toggleFavorite"
              />
            </div>
          </div>
        </div>

        <!-- Business Overview Section -->
        <div class="bg-white shadow rounded-lg overflow-hidden">
          <div class="p-4 border-b border-gray-200">
            <button 
              @click="toggleSection('businessOverview')" 
              class="flex items-center justify-between w-full text-left"
            >
              <h2 class="text-lg font-medium text-gray-900 flex items-center space-x-2">
                <svg 
                  :class="{'rotate-90': expandedSections.businessOverview}"
                  class="h-5 w-5 text-gray-500 transform transition-transform duration-200"
                  viewBox="0 0 20 20" 
                  fill="currentColor"
                >
                  <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                </svg>
                <span>Business Overview</span>
              </h2>
            </button>
          </div>
          <div v-show="expandedSections.businessOverview" class="p-4">
            <div class="grid grid-cols-1 gap-4">
              <ReportLink
                v-for="report in businessOverviewReports"
                :key="report.id"
                :report="report"
                @toggle-favorite="toggleFavorite"
              />
            </div>
          </div>
        </div>

        <!-- Customers & Sales Section -->
        <div class="bg-white shadow rounded-lg overflow-hidden">
          <div class="p-4 border-b border-gray-200">
            <button 
              @click="toggleSection('customersSales')" 
              class="flex items-center justify-between w-full text-left"
            >
              <h2 class="text-lg font-medium text-gray-900 flex items-center space-x-2">
                <svg 
                  :class="{'rotate-90': expandedSections.customersSales}"
                  class="h-5 w-5 text-gray-500 transform transition-transform duration-200"
                  viewBox="0 0 20 20" 
                  fill="currentColor"
                >
                  <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                </svg>
                <span>Customers & Sales</span>
              </h2>
            </button>
          </div>
          <div v-show="expandedSections.customersSales" class="p-4">
            <div class="grid grid-cols-1 gap-4">
              <ReportLink
                v-for="report in customersSalesReports"
                :key="report.id"
                :report="report"
                @toggle-favorite="toggleFavorite"
              />
            </div>
          </div>
        </div>

        <!-- Accounts & Balance Section -->
        <div class="bg-white shadow rounded-lg overflow-hidden">
          <div class="p-4 border-b border-gray-200">
            <button 
              @click="toggleSection('accountsBalance')" 
              class="flex items-center justify-between w-full text-left"
            >
              <h2 class="text-lg font-medium text-gray-900 flex items-center space-x-2">
                <svg 
                  :class="{'rotate-90': expandedSections.accountsBalance}"
                  class="h-5 w-5 text-gray-500 transform transition-transform duration-200"
                  viewBox="0 0 20 20" 
                  fill="currentColor"
                >
                  <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                </svg>
                <span>Accounts & Balance</span>
              </h2>
            </button>
          </div>
          <div v-show="expandedSections.accountsBalance" class="p-4">
            <div class="grid grid-cols-1 gap-4">
              <ReportLink
                v-for="report in accountsBalanceReports"
                :key="report.id"
                :report="report"
                @toggle-favorite="toggleFavorite"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// State
const searchQuery = ref('')
const expandedSections = ref({
  favorites: true,
  businessOverview: true,
  customersSales: true,
  accountsBalance: true
})

// Available reports data
const allReports = ref([
  // Business Overview Reports
  {
    id: 'profit-loss',
    name: 'Profit and Loss',
    description: 'Shows your income, expenses, and net profit or loss over time',
    category: 'businessOverview',
    favorite: true,
    path: '/reports/profit-loss'
  },
  {
    id: 'balance-sheet',
    name: 'Balance Sheet',
    description: 'Shows your assets, liabilities, and equity at a point in time',
    category: 'businessOverview',
    favorite: true,
    path: '/reports/balance-sheet'
  },
  {
    id: 'cash-flow',
    name: 'Statement of Cash Flows',
    description: 'Shows how changes in balance sheet accounts and income affect cash',
    category: 'businessOverview',
    favorite: false,
    path: '/reports/cash-flow'
  },
  // Customers & Sales Reports
  {
    id: 'sales-by-customer',
    name: 'Sales by Customer',
    description: 'Shows total sales and outstanding balances by customer',
    category: 'customersSales',
    favorite: false,
    path: '/reports/sales-by-customer'
  },
  {
    id: 'ar-aging',
    name: 'A/R Aging Summary',
    description: 'Shows unpaid customer invoices grouped by age',
    category: 'customersSales',
    favorite: true,
    path: '/reports/ar-aging'
  },
  {
    id: 'customer-balance',
    name: 'Customer Balance Summary',
    description: 'Shows balances for each customer',
    category: 'customersSales',
    favorite: false,
    path: '/reports/customer-balance'
  },
  // Accounts & Balance Reports
  {
    id: 'trial-balance',
    name: 'Trial Balance',
    description: 'Shows debit and credit balances for all accounts',
    category: 'accountsBalance',
    favorite: false,
    path: '/reports/trial-balance'
  },
  {
    id: 'account-balances',
    name: 'Account Balances',
    description: 'Shows balances for all accounts',
    category: 'accountsBalance',
    favorite: false,
    path: '/reports/account-balances'
  },
  {
    id: 'general-ledger',
    name: 'General Ledger',
    description: 'Shows all transactions by account',
    category: 'accountsBalance',
    favorite: false,
    path: '/reports/general-ledger'
  }
])

// Computed properties for filtered reports
const filteredReports = computed(() => {
  if (!searchQuery.value) return allReports.value
  const query = searchQuery.value.toLowerCase()
  return allReports.value.filter(report => 
    report.name.toLowerCase().includes(query) || 
    report.description.toLowerCase().includes(query)
  )
})

const favoriteReports = computed(() => 
  filteredReports.value.filter(report => report.favorite)
)

const businessOverviewReports = computed(() => 
  filteredReports.value.filter(report => report.category === 'businessOverview')
)

const customersSalesReports = computed(() => 
  filteredReports.value.filter(report => report.category === 'customersSales')
)

const accountsBalanceReports = computed(() => 
  filteredReports.value.filter(report => report.category === 'accountsBalance')
)

// Methods
const toggleSection = (section) => {
  expandedSections.value[section] = !expandedSections.value[section]
}

const toggleFavorite = (reportId) => {
  const report = allReports.value.find(r => r.id === reportId)
  if (report) {
    report.favorite = !report.favorite
  }
}
</script>

<script>
// Define the ReportLink component
export default {
  components: {
    ReportLink: {
      props: {
        report: {
          type: Object,
          required: true
        }
      },
      template: `
        <div class="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg">
          <div class="flex-1">
            <NuxtLink :to="report.path" class="block">
              <h3 class="text-sm font-medium text-gray-900">{{ report.name }}</h3>
              <p class="mt-1 text-sm text-gray-500">{{ report.description }}</p>
            </NuxtLink>
          </div>
          <div class="ml-4 flex-shrink-0">
            <button
              @click.prevent="$emit('toggle-favorite', report.id)"
              class="text-gray-400 hover:text-yellow-500 focus:outline-none"
              :class="{ 'text-yellow-500': report.favorite }"
            >
              <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
              </svg>
            </button>
          </div>
        </div>
      `
    }
  }
}
</script>
