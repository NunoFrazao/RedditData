<template>
    <div>
        <h4 class="first-title pb-4 mb-0 display-5 text-uppercase">{{ title }}</h4>
    </div>
</template>

<script setup>

// Props
const props = defineProps({
    title: {
        type: String,
        required: true
    }
})

</script>
