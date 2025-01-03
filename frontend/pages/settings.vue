<template>
  <div>
    <!-- Navigation Bar -->
    <nav class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <h1 class="text-xl font-semibold">Settings</h1>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="flex flex-col space-y-8">
        <label for="settings-nav" class="block text-sm font-medium text-gray-700 mb-1">Settings Navigation</label>
        <select 
          id="settings-nav"
          v-model="activeSection"
          class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
        >
          <option v-for="tab in tabs" :key="tab.name" :value="tab.name">
            {{ tab.label }}
          </option>
        </select>
      </div>

      <!-- Settings Content -->
      <div class="mt-8 flex-1 bg-white rounded-lg shadow">
        <!-- Company Section -->
        <div v-if="activeSection === 'company'" id="company" class="p-6">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-lg font-medium">Company Information</h2>
          </div>
          
          <!-- Company Name Information -->
          <div class="space-y-6">
            <div class="bg-gray-50 p-4 rounded-lg">
              <h3 class="text-md font-medium mb-4">Company Name Information</h3>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700">Company Name</label>
                  <input 
                    v-model="companyData.company_name_info.company_name" 
                    type="text" 
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" 
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700">Legal Name</label>
                  <input 
                    v-model="companyData.company_name_info.legal_name" 
                    type="text" 
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" 
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700">Identity Type</label>
                  <select
                    v-model="companyData.company_name_info.identity"
                    class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                    >
                    <option value="">Select an identity type</option>
                    <option v-for="type in fieldOptions.identity_types" :key="type" :value="type">
                      {{ type }}
                    </option>
                  </select>
                </div>
                <div v-if="companyData.company_name_info.identity">
                  <label class="block text-sm font-medium text-gray-700">
                    {{ companyData.company_name_info.identity === 'SSN' ? 'Social Security Number' : 'Employer Identification Number' }}
                  </label>
                  <input
                    v-model="companyData.company_name_info.tax_id"
                    type="text"
                    :placeholder="companyData.company_name_info.identity === 'SSN' ? 'XXX-XX-XXXX' : 'XX-XXXXXXX'"
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  />
                </div>
                <div class="col-span-2">
                  <label class="flex items-center">
                    <input 
                      type="checkbox" 
                      v-model="companyData.company_name_info.same_as_company_name" 
                      class="rounded border-gray-300 text-indigo-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                    />
                    <span class="ml-2 text-sm text-gray-600">Legal name same as company name</span>
                  </label>
                </div>
              </div>
            </div>

            <!-- Company Type -->
            <div class="bg-gray-50 p-4 rounded-lg mt-4">
              <h3 class="text-md font-medium mb-4">Company Type</h3>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700">Tax Form</label>
                  <select
                    v-model="companyData.company_type.tax_form"
                    class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                    >
                    <option value="">Select a tax form</option>
                    <option v-for="form in fieldOptions.tax_forms" :key="form" :value="form">
                      {{ form }}
                    </option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700">Industry</label>
                  <input 
                    v-model="companyData.company_type.industry" 
                    type="text" 
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" 
                  />
                </div>
              </div>
            </div>

            <!-- Contact Information -->
            <div class="bg-gray-50 p-4 rounded-lg">
              <h3 class="text-md font-medium mb-4">Contact Information</h3>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700">Company Email</label>
                  <input 
                    v-model="companyData.contact_info.company_email" 
                    type="email" 
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" 
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700">Customer-Facing Email</label>
                  <input 
                    v-model="companyData.contact_info.customer_facing_email" 
                    type="email" 
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" 
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700">Phone</label>
                  <input 
                    v-model="companyData.contact_info.company_phone" 
                    type="tel" 
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" 
                  />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700">Website</label>
                  <input 
                    v-model="companyData.contact_info.website" 
                    type="url" 
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" 
                  />
                </div>
                <div class="col-span-2">
                  <label class="flex items-center">
                    <input 
                      type="checkbox" 
                      v-model="companyData.contact_info.same_as_company_email" 
                      class="rounded border-gray-300 text-indigo-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                    />
                    <span class="ml-2 text-sm text-gray-600">Customer-facing email same as company email</span>
                  </label>
                </div>
              </div>
            </div>

            <!-- Address Section -->
            <div class="mt-6">
              <h3 class="text-lg font-medium text-gray-900">Address Information</h3>
              
              <!-- Company Address -->
              <div class="mt-4 bg-gray-50 rounded-lg p-4">
                <h4 class="font-medium text-gray-700">Company Address</h4>
                <div class="mt-2 grid grid-cols-1 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700">Street</label>
                    <input type="text" v-model="companyData.Address.company_address.street" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" />
                  </div>
                  <div class="grid grid-cols-2 gap-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700">City</label>
                      <input type="text" v-model="companyData.Address.company_address.city" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" />
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700">State</label>
                      <select
                        v-model="companyData.Address.company_address.state"
                        class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                        >
                        <option value="">Select a state</option>
                        <option v-for="state in fieldOptions.states" :key="state" :value="state">
                          {{ state }}
                        </option>
                      </select>
                    </div>
                  </div>
                  <div class="grid grid-cols-2 gap-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700">ZIP Code</label>
                      <input type="text" v-model="companyData.Address.company_address.zip_code" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" />
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700">Country</label>
                      <input type="text" v-model="companyData.Address.company_address.country" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" />
                    </div>
                  </div>
                </div>
              </div>

              <!-- Legal Address -->
              <div class="mt-4 bg-gray-50 rounded-lg p-4">
                <h4 class="font-medium text-gray-700">Legal Address</h4>
                <div class="mt-2 grid grid-cols-1 gap-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700">Street</label>
                    <input type="text" v-model="companyData.Address.legal_address.street" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" />
                  </div>
                  <div class="grid grid-cols-2 gap-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700">City</label>
                      <input type="text" v-model="companyData.Address.legal_address.city" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" />
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700">State</label>
                      <select
                        v-model="companyData.Address.legal_address.state"
                        class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                        >
                        <option value="">Select a state</option>
                        <option v-for="state in fieldOptions.states" :key="state" :value="state">
                          {{ state }}
                        </option>
                      </select>
                    </div>
                  </div>
                  <div class="grid grid-cols-2 gap-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700">ZIP Code</label>
                      <input type="text" v-model="companyData.Address.legal_address.zip_code" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" />
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700">Country</label>
                      <input type="text" v-model="companyData.Address.legal_address.country" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" />
                    </div>
                  </div>
                </div>
              </div>

              <div class="mt-4">
                <label class="flex items-center">
                  <input 
                    type="checkbox" 
                    v-model="companyData.Address.same_as_company_address" 
                    class="rounded border-gray-300 text-indigo-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  />
                  <span class="ml-2 text-sm text-gray-600">Legal address same as company address</span>
                </label>
              </div>
            </div>

            <!-- Save Button -->
            <div class="flex justify-end">
              <button 
                @click="saveCompanySettings" 
                class="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>

        <!-- Advanced Settings Content -->
        <div v-if="activeSection === 'advanced'" id="advanced" class="p-6">
          <div class="flex justify-between items-center mb-4">
            <h2 class="text-lg font-medium">Advanced Settings</h2>
          </div>
          
          <div class="space-y-6">
            <!-- Accounting Section -->
            <div class="bg-gray-50 p-4 rounded-lg">
              <h3 class="text-md font-medium mb-4">Accounting</h3>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700">First Month of Fiscal Year</label>
                  <select v-model="advancedData.accounting.fiscal_year_start"     
                    class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                  >
                    <option value="">Select Fiscal Year Start</option>
                    <option v-for="month in fieldOptions.fiscal_year_start" :key="month" :value="month">
                      {{ month }}
                    </option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700">First Month of Income Tax Year</label>
                  <select v-model="advancedData.accounting.income_tax_year_start"
                  class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                  >
                    <option value="">Select Income Tax Year Start</option>
                    <option v-for="month in fieldOptions.income_tax_year_start" :key="month" :value="month">
                      {{ month }}
                    </option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700">Accounting Method</label>
                  <select v-model="advancedData.accounting.accounting_method"
                    class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                  >
                    <option value="">Select Accounting Method</option>
                    <option v-for="method in fieldOptions.accounting_methods" :key="method" :value="method">
                      {{ method }}
                    </option>
                  </select>
                </div>
                <div class="col-span-2">
                  <label class="flex items-center">
                    <input 
                      type="checkbox" 
                      v-model="advancedData.accounting.close_the_books" 
                      class="rounded border-gray-300 text-indigo-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                    />
                    <span class="ml-2 text-sm text-gray-600">Close the Books</span>
                  </label>
                </div>
              </div>
            </div>

            <!-- Company Type Section -->
            <div class="bg-gray-50 p-4 rounded-lg">
              <h3 class="text-md font-medium mb-4">Company Type</h3>
              <div>
                <label class="block text-sm font-medium text-gray-700">Tax Form</label>
                <select v-model="advancedData.company_type.tax_form"
                class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                >
                  <option value="">Select Tax Form</option>
                  <option v-for="form in fieldOptions.tax_forms" :key="form" :value="form">
                    {{ form }}
                  </option>
                </select>
              </div>
            </div>

            <!-- Chart of Accounts -->
            <div class="bg-gray-50 p-4 rounded-lg">
              <h3 class="text-md font-medium mb-4">Chart of Accounts</h3>
              <div class="space-y-4">
                <div class="flex items-center">
                  <input type="checkbox" v-model="advancedData.chart_of_accounts.enable_account_numbers" class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded">
                  <label class="ml-2 block text-sm text-gray-900">Enable Account Numbers</label>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700">Tips Account</label>
                  <select v-model="advancedData.chart_of_accounts.tips_account"
                    class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                  >
                    <option value="">Select Tips Account</option>
                    <option v-for="account in fieldOptions.tips_accounts" :key="account" :value="account">
                      {{ account }}
                    </option>
                  </select>
                </div>
              </div>
            </div>

            <!-- Categories -->
            <div class="bg-gray-50 p-4 rounded-lg">
              <h3 class="text-md font-medium mb-4">Categories</h3>
              <div class="space-y-4">
                <div class="flex items-center">
                  <input type="checkbox" v-model="advancedData.categories.track_classes" class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded">
                  <label class="ml-2 block text-sm text-gray-900">Track Classes</label>
                </div>
                <div class="flex items-center">
                  <input type="checkbox" v-model="advancedData.categories.track_locations" class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded">
                  <label class="ml-2 block text-sm text-gray-900">Track Locations</label>
                </div>
              </div>
            </div>

            <!-- Automation -->
            <div class="bg-gray-50 p-4 rounded-lg">
              <h3 class="text-md font-medium mb-4">Automation</h3>
              <div class="space-y-4">
                <div class="flex items-center">
                  <input type="checkbox" v-model="advancedData.automation.pre_fill_forms" class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded">
                  <label class="ml-2 block text-sm text-gray-900">Pre-fill Forms</label>
                </div>
                <div class="flex items-center">
                  <input type="checkbox" v-model="advancedData.automation.auto_apply_credits" class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded">
                  <label class="ml-2 block text-sm text-gray-900">Auto Apply Credits</label>
                </div>
                <div class="flex items-center">
                  <input type="checkbox" v-model="advancedData.automation.auto_apply_payments" class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded">
                  <label class="ml-2 block text-sm text-gray-900">Auto Apply Payments</label>
                </div>
              </div>
            </div>

            <!-- Projects -->
            <div class="bg-gray-50 p-4 rounded-lg">
              <h3 class="text-md font-medium mb-4">Projects</h3>
              <div class="flex items-center">
                <input type="checkbox" v-model="advancedData.projects.organize_job_activity" class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded">
                <label class="ml-2 block text-sm text-gray-900">Organize Job Activity</label>
              </div>
            </div>

            <!-- Currency -->
            <div class="bg-gray-50 p-4 rounded-lg">
              <h3 class="text-md font-medium mb-4">Currency</h3>
              <div class="space-y-4">
                <div>
                  <select v-model="advancedData.other_preferences.currency"
                    class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                  >
                    <option value="">Select Home Currency</option>
                    <option v-for="currency in fieldOptions.currencies" :key="currency" :value="currency">
                      {{ currency }}
                    </option>
                  </select>
                </div>
                <div class="flex items-center">
                  <input type="checkbox" v-model="advancedData.currency.multicurrency" class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded">
                  <label class="ml-2 block text-sm text-gray-900">Enable Multicurrency</label>
                </div>
              </div>
            </div>

            <!-- Other Preferences -->
            <div class="bg-gray-50 p-4 rounded-lg">
              <h3 class="text-md font-medium mb-4">Other Preferences</h3>
              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700">Date Format</label>
                  <select v-model="advancedData.other_preferences.date_format"
                    class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                  >
                    <option value="">Select Date Format</option>
                    <option v-for="format in fieldOptions.date_formats" :key="format" :value="format">
                      {{ format }}
                    </option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700">Number Format</label>
                  <input type="text" v-model="advancedData.other_preferences.number_format" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700">Currency</label>
                  <input type="text" v-model="advancedData.other_preferences.currency" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
                </div>
                <div class="flex items-center">
                  <input type="checkbox" v-model="advancedData.other_preferences.vendor_bill_warning" class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded">
                  <label class="ml-2 block text-sm text-gray-900">Vendor Bill Warning</label>
                </div>
                <div class="flex items-center">
                  <input type="checkbox" v-model="advancedData.other_preferences.duplicate_journal_warning" class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded">
                  <label class="ml-2 block text-sm text-gray-900">Duplicate Journal Warning</label>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700">Sign Out After Inactivity</label>
                  <select v-model="advancedData.other_preferences.sign_out_after_inactivity"
                    class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                  >
                    <option value="">Select Sign Out Timer</option>
                    <option v-for="time in fieldOptions.sign_out_after_inactivity" :key="time" :value="time">
                      {{ time }}
                    </option>
                  </select>
                </div>
              </div>
            </div>

            <!-- Save Button -->
            <div class="flex justify-end">
              <button 
                @click="saveAdvancedSettings"
                class="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRuntimeConfig } from '#app'
import debounce from 'lodash/debounce'

const config = useRuntimeConfig()
const activeSection = ref('company')
const isLoading = ref(false)
const errorMessage = ref('')

const tabs = ref([
  { name: 'company', label: 'Company' },
  { name: 'advanced', label: 'Advanced' }
])

const fieldOptions = ref({
  // Company options
  identity_types: [],
  tax_forms: [],
  states: [],

  // Advanced options
  fiscal_year_start: [],
  income_tax_year_start: [],
  accounting_methods: [],
  currencies: [],
  date_formats: [],
  number_formats: [],
  sign_out_after_inactivity: [],
  tips_accounts: []
})

const companyData = ref({
  company_name_info: {
    company_name: '',
    legal_name: '',
    same_as_company_name: false,
    identity: '',
    tax_id: ''
  },
  company_type: {
    tax_form: '',
    industry: ''
  },
  contact_info: {
    company_email: '',
    customer_facing_email: '',
    same_as_company_email: false,
    company_phone: '',
    website: ''
  },
  Address: {
    company_address: {
      street: '',
      city: '',
      state: '',
      zip_code: '',
      country: ''
    },
    legal_address: {
      street: '',
      city: '',
      state: '',
      zip_code: '',
      country: ''
    },
    same_as_company_address: false
  }
})

const advancedData = ref({
  accounting: {
    fiscal_year_start: '',
    income_tax_year_start: '',
    accounting_method: '',
    close_the_books: false
  },
  company_type: {
    tax_form: ''
  },
  chart_of_accounts: {
    enable_account_numbers: false,
    tips_account: ''
  },
  automation: {
    pre_fill_forms: false,
    auto_apply_credits: false,
    auto_apply_payments: false
  },
  other_preferences: {
    date_format: '',
    number_format: '',
    currency: '',
    vendor_bill_warning: false,
    duplicate_journal_warning: false,
    sign_out_after_inactivity: ''
  }
})

const fetchFieldOptions = async () => {
  try {
    console.log('Fetching field options...')
    // Fetch company options
    const companyRes = await fetch(`${config.public.apiBase}/api/company/get_field_options`)
    if (companyRes.ok) {
      const companyData = await companyRes.json()
      console.log('Company options:', companyData)
      // Map company enums
      fieldOptions.value.identity_types = companyData.identity_types || []
      fieldOptions.value.tax_forms = companyData.tax_forms || []
      fieldOptions.value.states = companyData.states || []
    } else {
      console.error('Failed to fetch company options:', await companyRes.text())
    }

    // Fetch advanced options
    const advancedRes = await fetch(`${config.public.apiBase}/api/advanced/get_field_options`)
    if (advancedRes.ok) {
      const advancedData = await advancedRes.json()
      console.log('Advanced options:', advancedData)
      // Map advanced enums
      fieldOptions.value.fiscal_year_start = advancedData.fiscal_year_start || []
      fieldOptions.value.income_tax_year_start = advancedData.income_tax_year_start || []
      fieldOptions.value.accounting_methods = advancedData.accounting_methods || []
      fieldOptions.value.tips_accounts = advancedData.tips_accounts || []
      fieldOptions.value.currencies = advancedData.currencies || []
      fieldOptions.value.date_formats = advancedData.date_formats || []
      fieldOptions.value.number_formats = advancedData.number_formats || []
      fieldOptions.value.sign_out_after_inactivity = advancedData.sign_out_after_inactivity || []
    } else {
      console.error('Failed to fetch advanced options:', await advancedRes.text())
    }
  } catch (error) {
    console.error('Error fetching field options:', error)
  }
}

// Load all settings data when component mounts
onMounted(async () => {
  try {
    console.log('Component mounted')
    // First fetch field options
    await fetchFieldOptions()
    console.log('Field options loaded:', fieldOptions.value)

    // Then load company data
    const companyRes = await fetch(`${config.public.apiBase}/api/company/get_company`)
    if (companyRes.ok) {
      const data = await companyRes.json()
      console.log('Company data loaded:', data)
      companyData.value = data
    } else {
      console.error('Failed to load company data:', await companyRes.text())
    }

    // Finally load advanced settings
    const advancedRes = await fetch(`${config.public.apiBase}/api/advanced/get_advanced`)
    if (advancedRes.ok) {
      const data = await advancedRes.json()
      console.log('Advanced data loaded:', data)
      advancedData.value = data
    } else {
      console.error('Failed to load advanced data:', await advancedRes.text())
    }
  } catch (error) {
    console.error('Error in onMounted:', error)
  }
})

// Save functions
const saveCompanySettings = async () => {
  try {
    console.log('Saving company settings:', companyData.value)
    const response = await fetch(`${config.public.apiBase}/api/company/update_company`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(companyData.value)
    })

    if (response.ok) {
      console.log('Company settings saved successfully')
    } else {
      console.error('Failed to save company settings:', await response.text())
    }
  } catch (error) {
    console.error('Error saving company settings:', error)
  }
}

const saveAdvancedSettings = async () => {
  try {
    console.log('Saving advanced settings:', advancedData.value)
    const response = await fetch(`${config.public.apiBase}/api/advanced/update_advanced`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(advancedData.value)
    })

    if (response.ok) {
      console.log('Advanced settings saved successfully')
    } else {
      console.error('Failed to save advanced settings:', await response.text())
    }
  } catch (error) {
    console.error('Error saving advanced settings:', error)
  }
}

// Watch for changes in each section's data and auto-save
watch(companyData, (newVal) => {
}, { deep: true })

watch(advancedData, (newVal) => {
}, { deep: true })

// Watch for changes in same_as fields
watch(() => companyData.value.company_name_info.same_as_company_name, (newVal) => {
  if (newVal) {
    companyData.value.company_name_info.legal_name = companyData.value.company_name_info.company_name
  }
})

watch(() => companyData.value.contact_info.same_as_company_email, (newVal) => {
  if (newVal) {
    companyData.value.contact_info.customer_facing_email = companyData.value.contact_info.company_email
  }
})

watch(() => companyData.value.Address.same_as_company_address, (newVal) => {
  if (newVal) {
    companyData.value.Address.legal_address = { ...companyData.value.Address.company_address }
  }
})
</script>
