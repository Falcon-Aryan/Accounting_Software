<template>
  <BaseNewFormModal
    :is-open="modelValue"
    title="Create New Customer"
    width="md"
    @close="$emit('update:modelValue', false)"
  >
    <div v-if="errorMessage" class="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
      <p class="text-sm text-red-600">{{ errorMessage }}</p>
    </div>

    <form @submit.prevent="handleSubmit" class="space-y-4">
      <!-- Personal Information -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">First Name</label>
          <input
            type="text"
            v-model="form.first_name"
            required
            class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">Last Name</label>
          <input
            type="text"
            v-model="form.last_name"
            required
            class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
          />
        </div>
      </div>

      <!-- Contact Information -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">Email</label>
          <input
            type="email"
            v-model="form.email"
            required
            class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">Phone</label>
          <input
            type="tel"
            v-model="form.phone"
            required
            class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
          />
        </div>
      </div>

      <!-- Company Information -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">Company Name</label>
          <input
            type="text"
            v-model="form.company_name"
            class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">Website</label>
          <input
            type="url"
            v-model="form.website"
            class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
          />
        </div>
      </div>

      <!-- Billing Address -->
      <div>
        <h4 class="text-sm font-medium text-gray-700 mb-2">Billing Address</h4>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700">Street</label>
            <input
              type="text"
              v-model="form.billing_address.street"
              required
              class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">City</label>
            <input
              type="text"
              v-model="form.billing_address.city"
              required
              class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">State</label>
            <input
              type="text"
              v-model="form.billing_address.state"
              required
              class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Postal Code</label>
            <input
              type="text"
              v-model="form.billing_address.postal_code"
              required
              class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Country</label>
            <input
              type="text"
              v-model="form.billing_address.country"
              required
              class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
            />
          </div>
        </div>
      </div>

      <!-- Shipping Address -->
      <div>
        <div class="flex items-center mb-2">
          <input
            type="checkbox"
            v-model="form.use_billing_for_shipping"
            class="h-4 w-4 text-blue-600 rounded border-gray-300"
          />
          <label class="ml-2 text-sm text-gray-700">Use billing address for shipping</label>
        </div>
        
        <div v-if="!form.use_billing_for_shipping">
          <h4 class="text-sm font-medium text-gray-700 mb-2">Shipping Address</h4>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700">Street</label>
              <input
                type="text"
                v-model="form.shipping_address.street"
                required
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">City</label>
              <input
                type="text"
                v-model="form.shipping_address.city"
                required
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">State</label>
              <input
                type="text"
                v-model="form.shipping_address.state"
                required
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Postal Code</label>
              <input
                type="text"
                v-model="form.shipping_address.postal_code"
                required
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Country</label>
              <input
                type="text"
                v-model="form.shipping_address.country"
                required
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Form Actions -->
      <div class="flex justify-end space-x-3">
        <BaseButton 
          type="button" 
          variant="secondary"
          @click="$emit('update:modelValue', false)"
        >
          Cancel
        </BaseButton>
        <BaseButton 
          type="submit"
          variant="primary"
        >
          Add Customer
        </BaseButton>
      </div>
    </form>
  </BaseNewFormModal>
</template>

<script setup>
import { ref, watch } from 'vue'
import { getAuth } from 'firebase/auth'
import { useRuntimeConfig } from '#app'
import BaseNewFormModal from '~/components/BaseNewFormModal.vue'
import BaseButton from './BaseButton.vue'

const config = useRuntimeConfig()

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true
  }
})

const emit = defineEmits(['update:modelValue', 'submit'])

const form = ref({
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  website: '',
  use_billing_for_shipping: true,
  billing_address: {
    street: '',
    city: '',
    state: '',
    postal_code: '',
    country: 'United States'
  },
  shipping_address: {
    street: '',
    city: '',
    state: '',
    postal_code: '',
    country: 'United States'
  }
})

// Watch for use_billing_for_shipping changes
watch(() => form.value.use_billing_for_shipping, (newVal) => {
  if (newVal) {
    form.value.shipping_address = { ...form.value.billing_address }
  }
})

// Watch billing address changes when use_billing_for_shipping is true
watch(() => form.value.billing_address, (newVal) => {
  if (form.value.use_billing_for_shipping) {
    form.value.shipping_address = { ...newVal }
  }
}, { deep: true })

const errorMessage = ref('')

const handleSubmit = async () => {
  try {
    const auth = getAuth()
    const idToken = await auth.currentUser?.getIdToken()

    const response = await fetch(`${config.public.apiBase}/api/customers/create_customer`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${idToken}`
      },
      body: JSON.stringify(form.value)
    })

    if (response.ok) {
      const newCustomer = await response.json()
      emit('submit', newCustomer)
      resetForm()
    } else {
      const errorData = await response.text()
      setError(errorData || 'Failed to create customer')
    }
  } catch (error) {
    console.error('Error creating customer:', error)
    setError('An error occurred while creating the customer')
  }
}

const resetForm = () => {
  form.value = {
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    website: '',
    use_billing_for_shipping: true,
    billing_address: {
      street: '',
      city: '',
      state: '',
      postal_code: '',
      country: 'United States'
    },
    shipping_address: {
      street: '',
      city: '',
      state: '',
      postal_code: '',
      country: 'United States'
    }
  }
  errorMessage.value = ''
}

const setError = (message) => {
  errorMessage.value = message
}

defineExpose({ resetForm, setError })
</script>
