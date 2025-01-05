<template>
  <div class="min-h-screen bg-gradient-to-b from-gray-50 to-white">

    <!-- Hero section -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16 text-center">
      <div class="max-w-4xl mx-auto">
        <div class="mt-10 flex justify-center gap-4">
          <NuxtLink
            to="/signup"
            class="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
          >
            Get Started
          </NuxtLink>
          <NuxtLink
            to="/login"
            class="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-indigo-600 bg-white hover:bg-gray-50"
          >
            Sign In
          </NuxtLink>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
// No script needed for landing page
</script>