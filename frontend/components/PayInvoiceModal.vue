<!-- PayInvoiceModal.vue -->
<template>
  <div v-if="show" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-[100]">
    <div class="relative top-20 mx-auto p-5 border w-[500px] shadow-lg rounded-md bg-white">
      <!-- Modal Header -->
      <div class="flex justify-between items-center p-4 border-b">
        <h2 class="text-xl font-semibold">Pay Invoice #{{ invoice?.id }}</h2>
        <button @click="close" class="text-gray-500 hover:text-gray-700">
          <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Modal Body -->
      <div class="p-6">
        <form @submit.prevent="handleSubmit">
          <!-- Error Message -->
          <div v-if="errorMessage" class="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {{ errorMessage }}
          </div>

          <!-- Payment Amount -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">Payment Amount</label>
            <div class="relative">
              <span class="absolute inset-y-0 left-0 pl-3 flex items-center text-gray-500">$</span>
              <input
                type="number"
                v-model="form.amount"
                class="pl-7 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                :placeholder="invoice?.balance_due.toString()"
                step="0.01"
                required
              />
            </div>
            <p class="mt-1 text-sm text-gray-500">Balance Due: ${{ invoice?.balance_due }}</p>
          </div>

          <!-- Payment Method -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">Payment Method</label>
            <select
              v-model="form.payment_method"
              class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              required
            >
              <option value="" disabled>Select a payment method</option>
              <option value="cash">Cash</option>
              <option value="check">Check</option>
              <option value="credit_card">Credit Card</option>
              <option value="bank_transfer">Bank Transfer</option>
              <option value="other">Other</option>
            </select>
          </div>

          <!-- Payment Date -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">Payment Date</label>
            <input
              type="date"
              v-model="form.payment_date"
              class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              required
            />
          </div>

          <!-- Reference Number -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">Reference Number (Optional)</label>
            <input
              type="text"
              v-model="form.reference_number"
              class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              placeholder="Check number, transaction ID, etc."
            />
          </div>

          <!-- Notes -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">Notes (Optional)</label>
            <textarea
              v-model="form.notes"
              rows="3"
              class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              placeholder="Add any additional notes..."
            ></textarea>
          </div>

          <!-- Footer -->
          <div class="mt-6 flex justify-end space-x-3">
            <BaseButton
              type="button"
              variant="secondary"
              @click="close"
            >
              Cancel
            </BaseButton>
            <BaseButton
              type="submit"
              variant="primary"
            >
              Record Payment
            </BaseButton>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRuntimeConfig } from '#app'
import { getAuth } from 'firebase/auth'
import BaseButton from '~/components/BaseButton.vue'

const config = useRuntimeConfig()

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  invoice: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'payment-recorded'])

const errorMessage = ref('')
const form = ref({
  amount: '',
  payment_method: '',
  payment_date: new Date().toISOString().split('T')[0],
  reference_number: '',
  notes: ''
})

function close() {
  form.value = {
    amount: '',
    payment_method: '',
    payment_date: new Date().toISOString().split('T')[0],
    reference_number: '',
    notes: ''
  }
  errorMessage.value = ''
  emit('close')
}

async function handleSubmit() {
  try {
    const auth = getAuth()
    const token = await auth.currentUser?.getIdToken()
    
    if (!token) {
      errorMessage.value = 'Authentication required'
      return
    }

    const response = await fetch(`${config.public.apiBase}/api/invoices/${props.invoice.id}/add_payment`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        amount: parseFloat(form.value.amount),
        date: form.value.payment_date,
        payment_method: form.value.payment_method,
        notes: form.value.notes
      })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || 'Failed to record payment')
    }

    const updatedInvoice = await response.json()
    emit('payment-recorded', updatedInvoice)
    close()
  } catch (error) {
    errorMessage.value = error.message
  }
}
</script>
