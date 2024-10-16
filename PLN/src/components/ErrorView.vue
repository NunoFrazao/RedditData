<template>
    <div class="row align-self-stretch">
        <div class="col text-white">
            <div class="row">
                <div class="col grid-margin stretch-card">
                    <div class="card card-shadow">
                        <div class="card-body">
                            <div class="row flex-column text-center justify-content-center">
                                <h1 :class="['display-1 mb-4', colorClass]">{{ errorCode }}</h1>
                                <h3 class="font-weight-light">{{ errorMessage }}</h3>
                                <RouterLink to="/" class="mt-3">
                                    <a :class="[colorClass, 'font-weight-medium']" href="#">Voltar à página inicial</a>
                                </RouterLink>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>

// Props
const props = defineProps({
    errorCode: {
        type: String,
        required: true
    },
    errorMessage: {
        type: String,
        required: true
    },
    colorClass: {
        type: String,
        required: true
    }
})

</script>
