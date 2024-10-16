<!-- CookieConsent.vue -->
<template>
    <div v-if="showCookieConsent" class="cookie-consent">
        <div class="cookie-consent-content">
            <p class="text-center pb-4 border-bottom">Este site utiliza cookies para melhorar a experiência do usuário.
                Ao continuar a navegar, você concorda com o uso de cookies.</p>
            <div class="btn-group" role="group" aria-label="Actions buttons">
                <button class="btn mx-1" @click="acceptCookies">Aceitar</button>
                <button class="btn mx-1 close-btn" @click="closeCookieConsent">Fechar</button>
            </div>
        </div>
    </div>
</template>

<script setup>

//#region Imports
import { ref } from 'vue'

import '@/assets/css/cookies.css'
//#endregion

//#region Variables
const showCookieConsent = ref(!localStorage.getItem('cookie-consent'))
//#endregion

//#region Methods
const acceptCookies = () => {
    localStorage.setItem('cookie-consent', 'accepted')
    showCookieConsent.value = false
}

const closeCookieConsent = () => {
    showCookieConsent.value = false
}
//#endregion

</script>