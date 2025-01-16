<template>
  <div class="min-h-screen bg-gray-100 py-6 px-4 sm:px-6 lg:px-8">
    <div class="max-w-7xl mx-auto">
      <div class="bg-white shadow overflow-hidden sm:rounded-lg">
        <div class="px-4 py-5 sm:px-6 flex justify-between items-center">
          <div>
            <h3 class="text-lg leading-6 font-medium text-gray-900">Invoice Report</h3>
            <p class="mt-1 max-w-2xl text-sm text-gray-500">Detailed information about the invoice.</p>
          </div>
          <BaseButton @click="$router.push('/invoices')">
            Back to Invoices
          </BaseButton>
        </div>
        
        <div v-if="isLoading" class="px-4 py-5 sm:p-6">
          <div class="flex justify-center">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
          </div>
        </div>

        <div v-else-if="error" class="px-4 py-5 sm:p-6">
          <p class="text-red-600">{{ error }}</p>
        </div>

        <div v-else class="border-t border-gray-200">
          <dl>
            <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Invoice Number</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{{ invoice.invoice_no }}</dd>
            </div>
            <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Status</dt>
              <dd class="mt-1 text-sm sm:mt-0 sm:col-span-2">
                {{ invoice.status }}
                <span v-if="invoice.status === 'void'" class="ml-2 text-sm text-red-600">
                  {{ invoice.void_reason || 'No reason provided' }}
                </span>
              </dd>
            </div>
            <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Customer</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {{ invoice.customer_name }}
              </dd>
            </div>
            <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Invoice Date</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {{ formatDate(invoice.date) }}
              </dd>
            </div>
            <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Due Date</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {{ formatDate(invoice.due_date) }}
              </dd>
            </div>
            <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Products</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <div class="border rounded-md">
                  <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                      <tr>
                        <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                        <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                        <th scope="col" class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Quantity</th>
                        <th scope="col" class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Price</th>
                        <th scope="col" class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Total</th>
                      </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                      <tr v-for="item in invoice.line_items" :key="item.product_id">
                        <td class="px-4 py-3 text-sm text-gray-900">{{ item.product_id }}</td>
                        <td class="px-4 py-3 text-sm text-gray-900">{{ item.description }}</td>
                        <td class="px-4 py-3 text-sm text-gray-900 text-right">{{ item.quantity }}</td>
                        <td class="px-4 py-3 text-sm text-gray-900 text-right">{{ formatCurrency(item.unit_price) }}</td>
                        <td class="px-4 py-3 text-sm text-gray-900 text-right">{{ formatCurrency(item.total) }}</td>
                      </tr>
                      <tr class="bg-gray-50">
                        <td colspan="4" class="px-4 py-3 text-sm font-medium text-gray-900 text-left">Total:</td>
                        <td class="px-4 py-3 text-sm font-medium text-gray-900 text-right">{{ formatCurrency(invoice.total) }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </dd>
            </div>
            <div class="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Payments</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                <div v-if="payments.length > 0" class="border rounded-md">
                  <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                      <tr>
                        <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                        <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Method</th>
                        <th scope="col" class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Amount</th>
                      </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                      <tr v-for="payment in payments" :key="payment.id">
                        <td class="px-4 py-3 text-sm text-gray-900">{{ formatDate(payment.date) }}</td>
                        <td class="px-4 py-3 text-sm text-gray-900">{{ payment.method }}</td>
                        <td class="px-4 py-3 text-sm text-gray-900 text-right">{{ formatCurrency(payment.amount) }}</td>
                      </tr>
                      <tr class="bg-gray-50">
                        <td colspan="2" class="px-4 py-3 text-sm font-medium text-gray-900 text-right">Total Paid:</td>
                        <td class="px-4 py-3 text-sm font-medium text-gray-900 text-right">{{ formatCurrency(totalPaid) }}</td>
                      </tr>
                      <tr class="bg-gray-50">
                        <td colspan="2" class="px-4 py-3 text-sm font-medium text-gray-900 text-right">Balance Due:</td>
                        <td class="px-4 py-3 text-sm font-medium text-gray-900 text-right">{{ formatCurrency(balanceDue) }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <div v-else class="text-gray-500">No payments recorded</div>
              </dd>
            </div>
            <div class="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt class="text-sm font-medium text-gray-500">Notes</dt>
              <dd class="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2 whitespace-pre-wrap">{{ invoice.notes || 'No notes' }}</dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRuntimeConfig, useRoute } from '#app'
import { initializeApp } from 'firebase/app'
import { getAuth } from 'firebase/auth'
import { firebaseConfig } from '../../../config/firebase.config'

definePageMeta({
  middleware: ['auth']
})

const app = initializeApp(firebaseConfig)
const auth = getAuth(app)

async function getIdToken() {
  const user = auth.currentUser
  if (!user) {
    throw new Error('No authenticated user')
  }
  return user.getIdToken()
}


const config = useRuntimeConfig()
const route = useRoute()
const invoice = ref(null)
const payments = ref([])
const isLoading = ref(true)
const error = ref(null)

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString()
}

const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value || 0)
}

const fetchInvoice = async () => {
  try {
    isLoading.value = true
    error.value = null
    const token = await getIdToken()
    const response = await fetch(`${config.public.apiBase}/api/invoices/get_invoice/${route.params.id}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    if (!response.ok) {
      throw new Error('Failed to fetch invoice data')
    }
    const data = await response.json()
    invoice.value = data
    
    // Fetch payments for this invoice
    const paymentsResponse = await fetch(`${config.public.apiBase}/api/invoices/get_payments/${route.params.id}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    if (paymentsResponse.ok) {
      const paymentsData = await paymentsResponse.json()
      payments.value = paymentsData.payments || []
    }
  } catch (err) {
    handleError(err)
  } finally {
    isLoading.value = false
  }
}


function handleError(error) {
  if (error.message === 'No authenticated user') {
    error.value = 'Please log in to perform this action'
  } else {
    error.value = error.message
  }
  console.error('Error:', error)
}

onMounted(() => {
  fetchInvoice()
})
</script>
