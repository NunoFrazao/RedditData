<template>
    <!-- Register form -->
    <div class="row w-100 m-0">
        <div class="content-wrapper full-page-wrapper d-flex align-items-center auth login-bg">
            <div class="card col-lg-4 mx-auto">
                <div class="card-body px-5 py-5">
                    <!-- Title -->
                    <div class="row justify-content-between px-3 pb-4 mb-3">
                        <TitleSection title="Criar conta" />
                    </div>

                    <!-- Form -->
                    <form @submit.prevent="handleSubmit">
                        <div class="form-group">
                            <label>Nome *</label>
                            <input type="text" class="form-control p_input" v-model="user.name">
                            <small v-if="nameError" class="text-danger">Nome é obrigatório.</small>
                        </div>
                        <div class="form-group">
                            <label>Email *</label>
                            <input type="email" class="form-control p_input" v-model="user.email">
                            <small v-if="emailError" class="text-danger">Email inválido.</small>
                        </div>
                        <div class="form-group">
                            <label>Password *</label>
                            <input type="password" class="form-control p_input" v-model="user.password">
                            <small v-if="passwordError" class="text-danger">Senha é obrigatória.</small>
                        </div>
                        <div class="form-group">
                            <label>Contacto *</label>
                            <input type="text" class="form-control p_input" v-model="user.contacto">
                            <small v-if="contactoError" class="text-danger">Contacto é obrigatório.</small>
                        </div>
                        <div class="text-center">
                            <button type="submit" class="btn btn-primary btn-block enter-btn">Criar conta</button>
                            <button type="button" class="btn  btn-block" @click.prevent="cancel()">Cancel</button>
                        </div>
                        <p class="sign-up">Já tem uma conta?
                            <RouterLink to="/login" class="routerlink-anc"><a href="#"> Login</a></RouterLink>
                        </p>
                    </form>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>

//#region Imports
import { ref, computed } from "vue"
import { useOthersStore } from '@/stores/others'
import { useToast } from 'vue-toastification'

import router from '@/router/index.js'
import axios from "axios"

import TitleSection from '@/components/TitleSection.vue'
//#endregion

//#region Variables
const toast = useToast()
const othersStore = useOthersStore()

const user = ref({
    name: '',
    email: '',
    password: '',
    contacto: '',
    tipo_user: 2
})

const nameError = computed(() => user.value.name.trim() === '')
const emailError = computed(() => !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(user.value.email))
const passwordError = computed(() => user.value.password.trim() === '')
const contactoError = computed(() => !/^(9\d{8}|\+351\s9\d{8}|\+1\s\d{3}-\d{3}-\d{4}|\+44\s7\d{3}\s\d{6}|\+61\s4\d{2}\s\d{3}\s\d{3}|\+33\s6\d{2}\s\d{3}\s\d{3})$/.test(user.value.contacto.trim()))
//#endregion

//#region Methods
const handleSubmit = async () => {
    if (nameError.value || emailError.value || passwordError.value || contactoError.value) {
        toast.error("Por favor, preencha todos os campos obrigatórios.")
        return
    }

    try {
        const response = await axios.post('users', user.value)
        if (response && response.status === 201) { // Assuming a successful registration returns status 201
            toast.success(`Utilizador ${othersStore.getFirstAndLastName(user.value.name)} criado com sucesso`)
            setTimeout(() => router.push('/login'), 500)
        } else {
            throw new Error('Erro inesperado no registo')
        }
    } catch (error) {
        console.error("Failed to submit user data:", error)
        toast.error('Erro ao registar utilizador. Por favor, tente novamente mais tarde.')
    }
}

const cancel = () => {
    router.go(-1)
}
//#endregion

</script>
