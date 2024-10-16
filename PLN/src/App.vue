<template>
    <div class="container-scroller" @palette-changed="onPaletteChanged">
        <!-- Sidebar -->
        <Sidebar v-if="showControlls" />

        <div class="container-fluid" :class="containerClass">
            <!-- Navbar -->
            <Navbar />

            <!-- Main content -->
            <div class="main-panel">
                <div :class="showNavigation == true ? 'content-wrapper' : ''">
                    <RouterView />
                </div>
            </div>
        </div>
    </div>

    <!-- Footer -->
    <footer class="footer">
        <div class="d-sm-flex justify-content-center justify-content-center">
            <span class="text-muted d-block text-center text-sm-left d-sm-inline-block">
                © 2024 PLN - Made by
                <a href="https://www.linkedin.com/in/josé-parreira-8804931a0/" target="_blank">José Parreira</a> and
                <a href="https://www.linkedin.com/in/nuno-frazao/" target="_blank">Nuno Frazão</a>
            </span>
        </div>
    </footer>
</template>

<script setup>

//#region Imports
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute } from 'vue-router'
import { RouterView } from 'vue-router'
import { store } from '@/stores/login'
import { eventBus } from '@/eventBus'

import Sidebar from '@/components/navigation/Sidebar.vue'
import Navbar from '@/components/navigation/Navbar.vue'
//#endregion

//#region Variables
const route = useRoute()
const windowWidth = ref(window.innerWidth)
const selectedPalette = ref(localStorage.getItem("colorPalette") || 0)

const colorPalettes = ref([
    {
        name: "Default",
        colors: ["#1f262f", "#191c24", "#f8f8f8", "#1d232b"]
    },
    {
        name: "Palette 1",
        colors: ["#2e3b4e", "#243447", "#f8f8f8", "#2a3647"]
    },
    {
        name: "Palette 2",
        colors: ["#354458", "#2a2e38", "#f8f8f8", "#333f4f"]
    },
    {
        name: "Palette 3",
        colors: ["#282c34", "#3a3f44", "#f8f8f8", "#2c3039"]
    },
    {
        name: "Palette 4",
        colors: ["#E1E5F2", "#2C3D55", "#f8f8f8", "#cdd1db"]
    },
    {
        name: "Light Mode",
        colors: ["#f0f0f0", "#e0e0e0", "#2e2e2e", "#dbdbdb"]  // Light theme
    }
])
//#endregion

//#region Methods
const showNavigation = computed(() => route.meta.requiresAuth !== false)
const showControlls = computed(() => store.isLoggedIn)

const containerClass = computed(() => {
    if (windowWidth.value < 992) {
        return showNavigation.value && showControlls.value ? 'container-fluid' : 'full-page-wrapper'
    } else {
        return showNavigation.value && showControlls.value ? 'page-body-wrapper' : 'full-page-wrapper'
    }
})

const updateWindowWidth = () => {
    windowWidth.value = window.innerWidth
}

const handleResize = () => {
    updateWindowWidth()
}

const applyPalette = (paletteIndex) => {
    const palette = colorPalettes.value[paletteIndex]
    document.documentElement.style.setProperty('--bg-color-body', palette.colors[0])
    document.documentElement.style.setProperty('--bg-color-sidebar', palette.colors[1])
    document.documentElement.style.setProperty('--bg-color-navbar', palette.colors[1])
    document.documentElement.style.setProperty('--bg-color-card', palette.colors[1])
    document.documentElement.style.setProperty('--text-color', palette.colors[2])
    document.documentElement.style.setProperty('--text-after-color', palette.colors[3])
}

const onPaletteChanged = (paletteIndex) => {
    selectedPalette.value = paletteIndex
    applyPalette(paletteIndex)
}
//#endregion

//#region Lifecycle hooks
onMounted(() => {
    showNavigation
    showControlls
    applyPalette(selectedPalette.value)
    eventBus.value.on('palette-changed', applyPalette)
    window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
    window.removeEventListener('resize', handleResize)
    eventBus.value.emit('palette-changed', null) // Clean up the event listener
})

watch(windowWidth, (newWidth, oldWidth) => {
    if (newWidth < 991 && oldWidth >= 991) {
        document.querySelector('.container-fluid').classList.remove('page-body-wrapper-open')
    } else if (newWidth >= 991 && oldWidth < 991) {
        document.querySelector('.container-fluid').classList.add('page-body-wrapper-open')
    }
})
//#endregion

</script>