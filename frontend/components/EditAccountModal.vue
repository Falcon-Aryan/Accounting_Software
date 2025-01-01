<!-- frontend/components/EditAccountModal.vue -->
<template>
  <BaseEditFormModal
    :is-open="isOpen"
    title="Edit Account"
    width="md"
    @close="close"
  >
    <form @submit.prevent="handleSubmit">
      <!-- Error Message -->
      <div v-if="errorMessage" class="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
        {{ errorMessage }}
      </div>

      <!-- Account Form -->
      <div class="space-y-4">
        <!-- Account Name -->
        <div>
          <label class="block text-sm font-medium text-gray-700">Account Name</label>
          <input
            type="text"
            v-model="form.name"
            required
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
          />
        </div>

        <!-- Account Type -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">Account Type</label>
            <select
              v-model="form.accountType"
              required
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            >
              <option value="">Select account type</option>
              <option v-for="type in accountTypes" :key="type" :value="type">
                {{ type }}
              </option>
            </select>
          </div>

          <!-- Detail Type -->
          <div>
            <label class="block text-sm font-medium text-gray-700">Detail Type</label>
            <select
              v-model="form.detailType"
              required
              :disabled="!form.accountType"
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            >
              <option value="">Select detail type</option>
              <option
                v-for="type in detailTypes[form.accountType] || []"
                :key="type"
                :value="type"
              >
                {{ type }}
              </option>
            </select>
          </div>
        </div>

        <!-- Description -->
        <div>
          <label class="block text-sm font-medium text-gray-700">Description</label>
          <textarea
            v-model="form.description"
            rows="3"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
          ></textarea>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="mt-6 flex justify-between">
        <!-- Delete Button -->
        <button
          type="button"
          @click="confirmDelete"
          class="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
          :disabled="isSubmitting"
        >
          Delete Account
        </button>
        
        <div class="flex space-x-3">
          <button
            type="button"
            @click="close"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
          >
            Cancel
          </button>
          <button
            type="submit"
            class="px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            :disabled="isSubmitting"
          >
            {{ isSubmitting ? 'Saving...' : 'Save Changes' }}
          </button>
        </div>
      </div>
    </form>
  </BaseEditFormModal>
</template>

<script setup>
import { ref, watch } from 'vue'
import BaseEditFormModal from '~/components/BaseEditFormModal.vue'

const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true
  },
  account: {
    type: Object,
    required: true
  },
  accountTypes: {
    type: Array,
    required: true
  },
  detailTypes: {
    type: Object,
    required: true
  },
  errorMessage: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['close', 'save', 'delete'])

const form = ref({
  name: '',
  accountType: '',
  detailType: '',
  description: ''
})

const isSubmitting = ref(false)

// Watch for account changes and update form
watch(() => props.account, (newAccount) => {
  if (newAccount) {
    form.value = {
      name: newAccount.name || '',
      accountType: newAccount.accountType || '',
      detailType: newAccount.detailType || '',
      description: newAccount.description || ''
    }
  }
}, { immediate: true })

function close() {
  emit('close')
}

async function handleSubmit() {
  try {
    isSubmitting.value = true
    await emit('save', { 
      id: props.account.id,
      ...form.value 
    })
    if (!props.errorMessage) {
      close()
    }
  } finally {
    isSubmitting.value = false
  }
}

function confirmDelete() {
  if (confirm('Are you sure you want to delete this account? This action cannot be undone.')) {
    emit('delete', props.account.id)
  }
}
</script>