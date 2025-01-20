<template>
  <BaseEditFormModal
  :is-open="modelValue"
  title="Edit Customer"
  width="md"
  @close="$emit('update:modelValue', false)"
>
  <div v-if="errorMessage" class="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
    <p class="text-sm text-red-600">{{ errorMessage }}</p>
  </div>

  <form @submit.prevent="handleSubmit" class="space-y-4" novalidate>
      <!-- Personal Information -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">First Name</label>
          <input
            type="text"
            v-model="form.first_name"
            class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">Last Name</label>
          <input
            type="text"
            v-model="form.last_name"
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
            class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">Phone</label>
          <input
            type="tel"
            v-model="form.phone"
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
              class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">City</label>
            <input
              type="text"
              v-model="form.billing_address.city"
              class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">State</label>
            <input
              type="text"
              v-model="form.billing_address.state"
              class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Postal Code</label>
            <input
              type="text"
              v-model="form.billing_address.postal_code"
              class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Country</label>
            <input
              type="text"
              v-model="form.billing_address.country"
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
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">City</label>
              <input
                type="text"
                v-model="form.shipping_address.city"
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">State</label>
              <input
                type="text"
                v-model="form.shipping_address.state"
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Postal Code</label>
              <input
                type="text"
                v-model="form.shipping_address.postal_code"
                class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Country</label>
              <input
                type="text"
                v-model="form.shipping_address.country"
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
          :disabled="isSubmitting"
        >
        {{ isSubmitting ? 'Updating Customer...' : 'Update Customer' }}
      </BaseButton>
      </div>
    </form>
  </BaseEditFormModal>
</template>

<script setup>
import { ref, watch } from 'vue'
import { getAuth } from 'firebase/auth'
import { useRuntimeConfig } from '#app'
import BaseEditFormModal from '~/components/BaseEditFormModal.vue'
import BaseButton from './BaseButton.vue'

const config = useRuntimeConfig()

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true
  },
  customer: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update:modelValue', 'submit'])

const form = ref({
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  company_name: '',
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

const errorMessage = ref('')
const isSubmitting = ref(false)

const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

const validatePhone = (phone) => {
  // Allows formats like: +1-234-567-8901, (123) 456-7890, 123.456.7890, 1234567890
  const phoneRegex = /^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4}$/
  return phoneRegex.test(phone)
}

const validateWebsite = (website) => {
  if (!website) return true // Website is optional
  // Validates URLs starting with http:// or https://
  const urlRegex = /^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/
  return urlRegex.test(website)
}

// Watch for customer changes and update form
watch(() => props.customer, (newCustomer) => {
  if (newCustomer) {
    form.value = {
      ...newCustomer,
      use_billing_for_shipping: !newCustomer.shipping_address || 
        JSON.stringify(newCustomer.billing_address) === JSON.stringify(newCustomer.shipping_address)
    }
  }
}, { immediate: true })

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

const handleSubmit = async () => {
  try {
    isSubmitting.value = true
    errorMessage.value = ''
    
    if (!form.value.first_name || !form.value.last_name || !form.value.email || !form.value.phone) {
      throw new Error('Please fill in all required fields')
    }

  
    if (!validateEmail(form.value.email)) {
      throw new Error('Please enter a valid email address')
    }

    if (!validatePhone(form.value.phone)) {
      throw new Error('Please enter a valid phone number')
    }

    if (form.value.website && !validateWebsite(form.value.website)) {
      throw new Error('Please enter a valid website URL')
    }


    // Billing address validation
    if (!form.value.billing_address.street || !form.value.billing_address.city ||
        !form.value.billing_address.state || !form.value.billing_address.postal_code ||
        !form.value.billing_address.country) {
      throw new Error('Please complete the billing address')
    }

    // Shipping address validation only if not using billing address
    if (!form.value.use_billing_for_shipping) {
      if (!form.value.shipping_address.street || !form.value.shipping_address.city ||
          !form.value.shipping_address.state || !form.value.shipping_address.postal_code ||
          !form.value.shipping_address.country) {
        throw new Error('Please complete the shipping address')
      }
    }
    
    emit('submit', form.value)
  } catch (error) {
    handleError(error)
  } finally {
    isSubmitting.value = false
  }
}

function handleError(error) {
  if (error.message === 'No authenticated user') {
    errorMessage.value = 'Please log in to perform this action'
  } else {
    errorMessage.value = error.message
  }
  console.error('Error:', error)
}

const setError = (message) => {
  errorMessage.value = message
}

defineExpose({ setError })

</script>
