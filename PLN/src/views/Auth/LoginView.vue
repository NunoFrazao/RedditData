<template>
    <!-- Login form -->
    <div class="row w-100 m-0">
        <div class="content-wrapper full-page-wrapper d-flex align-items-center auth login-bg">
            <div class="card col-lg-4 mx-auto">
                <div class="card-body px-5 py-5">
                    <!-- Title -->
                    <div class="row justify-content-between px-3 pb-4 mb-3">
                        <TitleSection title="Login" />
                    </div>

                    <!-- Form -->
                    <form @submit.prevent="handleSubmit">
                        <div class="form-group">
                            <label>Email</label>
                            <input type="email" class="form-control p_input" v-model="user.email">
                            <small v-if="emailError" class="text-danger">Email inválido.</small>
                        </div>
                        <div class="form-group">
                            <label>Password</label>
                            <input type="password" class="form-control p_input" v-model="user.password">
                            <small v-if="passwordError" class="text-danger">Senha é obrigatória.</small>
                        </div>
                        <div class="text-center mt-4">
                            <button type="submit" class="btn btn-primary btn-block enter-btn">Login</button>
                        </div>
                        <p class="sign-up">Não tem uma conta?
                            <RouterLink to="/register" class="routerlink-anc"><a href="#"> Criar conta</a></RouterLink>
                        </p>
                    </form>
                </div>
            </div>
        </div>
    </div>

    <!-- Continue without login -->
    <div class="row w-100 m-0">
        <div class="content-wrapper full-page-wrapper d-flex align-items-center auth login-bg mt-0 py-0">
            <div class="card col-lg-4 mx-auto">
                <div class="card-body px-5 py-2">
                    <RouterLink to="/" id="anc-no-account">
                        <a class="d-block py-2 text-light text-center">
                            Continuar sem conta <i class="mdi mdi-chevron-right"></i>
                        </a>
                    </RouterLink>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>

//#region Imports
import { ref, computed, inject } from "vue"
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import { store } from '@/stores/login'

import axios from "axios"

import TitleSection from '@/components/TitleSection.vue'
//#endregion

//#region Variables
const router = useRouter()
const toast = useToast()
const socket = inject("socket")

const user = ref({
    email: '',
    password: ''
})

const emailError = computed(() => !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(user.value.email))
const passwordError = computed(() => user.value.password.trim() === '')
//#endregion

//#region Methods
const handleSubmit = async () => {
    if (emailError.value || passwordError.value) return

    try {
        const response = await axios.post('/users/email', {
            email: user.value.email,
            password: user.value.password
        })

        if (response.data.data.email === user.value.email) {
            store.login(response.data.data, socket)
            router.push('/')
            setTimeout(() => { location.reload() }, 250)

            // Reinitialize dropdowns after login
            if (typeof window.initProfileDropdown === 'function') window.initProfileDropdown()

            // Reinitialize sidebar after login
            if (typeof window.initSidebarToggle === 'function') window.initSidebarToggle()
        }
    } catch (error) {
        if (error.response && error.response.status === 401) {
            toast.error('Email ou senha incorretos.')
        } else {
            toast.error('Erro ao tentar fazer login. Por favor, tente novamente mais tarde.')
        }
    }
}
//#endregion

</script>