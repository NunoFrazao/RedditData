<template>
    <div class="row">
        <div class="col-12 grid-margin">
            <div class="card">
                <div class="card-body">
                    <!-- Title -->
                    <div class="row justify-content-between px-3">
                        <TitleSection title="Utilizadores" />
                        <div>
                            <button type="button" class="btn btn-outline-secondary btn-fw" @click="insertUser()">Criar
                                Utilizador</button>
                        </div>
                    </div>

                    <!-- Table -->
                    <div class="row mt-5 px-3">
                        <div class="ag-theme-quartz" style="width: 100%; height: 100%;">
                            <ag-grid-vue :rowData="users" :columnDefs="columnDefs" :pagination="pagination"
                                :paginationPageSize="paginationPageSize"
                                :paginationPageSizeSelector="paginationPageSizeSelector" style="height: 500px"
                                class="ag-theme-quartz">
                            </ag-grid-vue>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal -->
    <Modal v-if="showModal" :title="'Confirmar Apagar Utilizador'" :show="showModal" :confirmButtonClass="'btn-danger'"
        @confirm="deleteUser(selectedUserId)" @close="showModal = false">
        <p>Tem a certeza de que deseja apagar o utilizador <span class="text-danger">{{
            othersStore.getFirstAndLastName(selectedUserName) }}</span>?
        </p>
    </Modal>
</template>

<script setup>

//#region Imports
import { ref, watchEffect } from "vue"
import { useRouter } from 'vue-router'
import { useToast } from "vue-toastification"
import { AgGridVue } from "ag-grid-vue3"
import { useOthersStore } from '@/stores/others'

import "ag-grid-community/styles/ag-grid.css"
import "ag-grid-community/styles/ag-theme-quartz.css"

import axios from "axios"

import TitleSection from '@/components/TitleSection.vue'
import Modal from '@/components/Modal.vue'

import '@/assets/css/users.css'
//#endregion

//#region Variables
const router = useRouter()
const toast = useToast()
const othersStore = useOthersStore()

const users = ref([])

const showModal = ref(false)
const selectedUserId = ref(null)
const pagination = ref(true)
const paginationPageSize = ref(20)
const paginationPageSizeSelector = ref[20, 50, 100]

const selectedUserName = ref('')
//#endregion

//#region Methods
const thumbnailRenderer = (params) => {
    const nameLetter = params.data.name[0]
    return `<div class="user-image-table"><span class="user-image-in-table">${nameLetter}</span></div>`
}

const actions = (to, id) => {
    if (to === 'view') router.push({ name: 'Detalhe do Utilizador', params: { id, type: 'view' } })
    else if (to === 'edit') router.push({ name: 'Detalhe do Utilizador', params: { id, type: 'edit' } })
    else if (to === 'delete') confirmDeleteUser(id)
}

const confirmDeleteUser = (id) => {
    selectedUserId.value = id
    const user = users.value.find(user => user.id === id)
    selectedUserName.value = user ? user.name : ''
    showModal.value = true
}

const insertUser = () => {
    router.push({ name: 'Detalhe do Utilizador', params: { id: -1, type: 'create' } })
}

const deleteUser = async (id) => {
    let userSelected = users.value.find(user => user.id === id).name

    try {
        await axios.delete(`/users/${id}`)
        users.value = users.value.filter(user => user.id !== id)
        showModal.value = false
        toast.success(`Utilizador ${othersStore.getFirstAndLastName(userSelected)} eliminado!`)
    } catch (error) {
        // console.error("Failed to delete user:", error)
        toast.error(`Erro. Não é possível realizar essa ação agora.`)
    }
}

const columnDefs = ref([
    {
        headerName: '',
        field: 'thumbnail',
        sortable: false,
        width: 80,
        resizable: false,
        cellRenderer: thumbnailRenderer,
        cellClass: params => { return 'd-flex align-items-center justify-content-end' }
    },
    {
        headerName: 'Nome',
        field: 'name',  // Field for user name
        filter: true,
        flex: 1,
        cellDataType: 'text',
        valueFormatter: (params) => params.data.name || '',
    },
    {
        headerName: 'Email',
        field: 'email',  // Field for user email
        filter: true,
        cellDataType: 'text',
        valueFormatter: (params) => params.data.email || ''
    },
    {
        headerName: 'Tipo Utilizador',
        field: 'tipo_user',  // Field for user type
        filter: true,
        cellDataType: 'text',
        valueFormatter: (params) => params.data.tipo_user || '',
        cellStyle: params => { return params.value === 'Admin' ? { color: 'red', 'font-weight': 'bold' } : {} }
    },
    {
        headerName: 'Contacto',
        field: 'contacto',  // Field for user contact
        filter: true,
        resizable: false,
        cellDataType: 'text',
        valueFormatter: (params) => params.data.contacto || '-------'
    },
    {
        headerName: 'Ações',
        field: 'id',
        sortable: false,
        width: 250,
        pinned: 'right',
        resizable: false,
        cellRenderer: (params) => {
            const userId = params.data?.id
            const loggedInUserId = localStorage.getItem('user_id')

            if (!userId) return '' // If no userId, return empty

            const container = document.createElement('div') // Create a container for the icons

            // View icon
            const viewIcon = document.createElement('i')
            viewIcon.className = 'mdi mdi-eye text-primary mr-3 cursor-pointer'
            viewIcon.setAttribute('title', 'Ver')
            viewIcon.addEventListener('click', () => actions('view', userId))
            container.appendChild(viewIcon)

            // Edit icon
            const editIcon = document.createElement('i')
            editIcon.className = 'mdi mdi-pencil text-secondary mr-3 cursor-pointer'
            editIcon.setAttribute('title', 'Editar')
            editIcon.addEventListener('click', () => actions('edit', userId))
            container.appendChild(editIcon)

            // Delete icon
            const deleteIcon = document.createElement('i')
            deleteIcon.className = 'mdi mdi-trash-can text-danger cursor-pointer'
            deleteIcon.setAttribute('title', 'Apagar')
            deleteIcon.style.opacity = userId == loggedInUserId ? '0.5' : '1' // Dim if it's the logged-in user
            deleteIcon.style.cursor = userId == loggedInUserId ? 'not-allowed' : 'pointer'
            deleteIcon.addEventListener('click', () => {
                if (userId != loggedInUserId) actions('delete', userId)
            })
            container.appendChild(deleteIcon)

            return container
        },
        cellClass: params => 'd-flex justify-content-start align-items-center'
    }

])

const fetchUsers = async () => {
    try {
        const response = await axios.get('/users')
        users.value = response.data.data

        // for each user if type = 1 then is admin else if type = 2 then is user
        users.value.forEach(user => { user.tipo_user = user.tipo_user == 1 ? 'Admin' : 'Normal' })
    } catch (error) {
        // console.error("Failed to fetch users:", error)
        toast.error(`Erro. Não é possível realizar essa ação agora.`)
    }
}
//#endregion

//#region Lifecycle Hooks
watchEffect(() => {
    fetchUsers()
})
//#endregion

</script>