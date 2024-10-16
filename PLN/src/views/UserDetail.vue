<template>
    <div class="row">
        <div class="col-12 grid-margin">
            <div class="table-responsive">
                <div class="col-12 grid-margin stretch-card">
                    <div class="card">
                        <div class="card-body">
                            <!-- Title -->
                            <TitleSection :title="title_type" />

                            <!-- Form -->
                            <form class="forms-sample mt-3" @submit.prevent="showConfirmationModal">
                                <div class="form-group">
                                    <label for="exampleInputName1">Nome</label>
                                    <input type="text" class="form-control" id="exampleInputName1" placeholder="Nome"
                                        v-model="user.name" :disabled="mode == 'view'">
                                    <span v-if="!isNameValid" class="text-danger">Nome deve ter pelo menos 3
                                        caracteres.</span>
                                </div>
                                <div class="form-group">
                                    <label for="exampleInputEmail3">Email</label>
                                    <input type="email" class="form-control" id="exampleInputEmail3" placeholder="Email"
                                        v-model="user.email" :disabled="mode == 'view'">
                                    <span v-if="!isEmailValid" class="text-danger">Email inválido.</span>
                                </div>
                                <div class="form-group">
                                    <label for="exampleInputContacto">Contacto</label>
                                    <input type="text" class="form-control" id="exampleInputContacto"
                                        placeholder="Contacto" v-model="user.contacto" :disabled="mode == 'view'">
                                    <span v-if="!isContactoValid" class="text-danger">Contacto inválido.</span>
                                </div>
                                <div class="form-group mt-5">
                                    <input type="checkbox" id="exampleInputAdmin" v-model="user.tipo_user"
                                        :disabled="mode == 'view'" class="styled-checkbox">
                                    <label for="exampleInputAdmin" class="styled-checkbox-label">Administrador</label>
                                </div>

                                <button class="btn btn-primary mr-2" :disabled="!isFormValid"
                                    v-if="mode !== 'view'">Submeter</button>
                                <button type="button" class="btn btn-dark" @click.prevent="cancel">Cancelar</button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal Submit -->
    <Modal v-if="showConfirmation" :title="mode == 'edit' ? 'Confirmar mudanças' : 'Criar utilizador'"
        :show="showConfirmation" :confirmButtonClass="'btn-primary'" @confirm="handleSubmit"
        @close="showConfirmation = false">
        <p>{{ mode == 'edit'
            ? 'Tem certeza de que deseja salvar as alterações?'
            : 'Tem certeza de que quer criar o utilizador?' }}
        </p>
    </Modal>
</template>

<script setup>

//#region Imports
import { ref, computed, watchEffect, inject } from 'vue'
import { useToast } from "vue-toastification"
import { useOthersStore } from '@/stores/others'

import axios from 'axios'
import router from '@/router/index.js'

import TitleSection from '@/components/TitleSection.vue'
import Modal from '@/components/Modal.vue'

import '@/assets/css/users.css'
//#endregion

const props = defineProps({
    id: [String, Number],
    type: String
})

//#region Variables
const toast = useToast()
const socket = inject("socket")
const othersStore = useOthersStore()

const userId = ref(props.id)
const mode = ref(props.type)
const user = ref({ name: '', email: '', password: '123456', contacto: '900000000', tipo_user: 2 }) // Default data
const originalUser = ref({ name: '', email: '', password: '', contacto: '', tipo_user: 2 })

const showConfirmation = ref(false)
//#endregion

//#region Methods
const isNameValid = computed(() => user.value.name.length >= 3)
const isEmailValid = computed(() => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(user.value.email))
const isContactoValid = computed(() => /^\+?\d{1,4}?[\d\s-]{7,14}$/.test(user.value.contacto))

const isFormValid = computed(() => {
    if (mode.value === 'create') {
        return isNameValid.value && isEmailValid.value && isContactoValid.value
    }
    return isNameValid.value && isEmailValid.value && isContactoValid.value && isChanged.value
})

const isChanged = computed(() => {
    if (mode.value === 'create') {
        return user.value.name !== '' || user.value.email !== '' || user.value.contacto !== '' || user.value.tipo_user !== 2
    }
    return user.value.name !== originalUser.value.name ||
        user.value.email !== originalUser.value.email ||
        user.value.contacto !== originalUser.value.contacto ||
        user.value.tipo_user !== originalUser.value.tipo_user
})

const title_type = computed(() => {
    if (mode.value === 'create') return 'Criar Utilizador'
    if (mode.value === 'edit') return 'Editar Utilizador'
    if (mode.value === 'view') return 'Informação'
    return ''
})

const fetchUser = async () => {
    if (mode.value == 'create') return

    try {
        const response = await axios.get(`/users/${userId.value}`)
        user.value = response.data.data
        user.value.tipo_user = response.data.data.tipo_user == 1 // Convert to boolean for checkbox
        originalUser.value = { ...response.data.data, tipo_user: response.data.data.tipo_user == 1 }
    } catch (error) {
        // console.error("Failed to fetch user details:", error)
        toast.error('Erro. Não é possível realizar essa ação agora.')
    }
}

const handleSubmit = async () => {
    try {
        user.value.tipo_user = user.value.tipo_user ? 1 : 2 // Convert boolean back to integer

        if (mode.value === 'create') {
            const response = await axios.post('users', user.value)
            console.log(user.value)
            
            socket.emit('newUser', response.data.data)
            toast.success(`Utilizador ${othersStore.getFirstAndLastName(user.value.name)} criado!`)
        } else if (mode.value === 'edit') {
            const response = await axios.patch(`users/${userId.value}`, user.value)
            socket.emit('userChange', response.data.data)
            toast.success(`Utilizador ${othersStore.getFirstAndLastName(user.value.name)} atualizado!`)
        }
    } catch (error) {
        toast.error('Erro. Não é possível realizar essa ação agora.')
    } finally {
        showConfirmation.value = false
        router.go(-1)
    }
}

const showConfirmationModal = () => {
    if (isChanged.value || mode.value === 'create') showConfirmation.value = true
}

const cancel = () => { router.go(-1) }
//#endregion

//#region Lifecycle Hooks
watchEffect(() => {
    fetchUser()
})
//#endregion

</script>
