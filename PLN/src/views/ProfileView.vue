<template>
    <!-- Information -->
    <div class="row">
        <div class="col-12 grid-margin">
            <div class="card">
                <div class="card-body">
                    <!-- Title -->
                    <div class="row justify-content-between px-3 pb-4 mb-3">
                        <TitleSection title="Perfil do utilizador" />
                        <div v-if="canDeleteAccount">
                            <button type="button" class="btn btn-outline-danger btn-fw"
                                @click="confirmDeleteAccount">Apagar Conta</button>
                        </div>
                    </div>

                    <!-- User Info Display -->
                    <div class="row pb-4">
                        <div class="col info-section">
                            <div>
                                <div class="user-image">
                                    <span class="user-image-in">{{ user_name[0] }}</span>
                                </div>
                            </div>

                            <!-- User data & form -->
                            <div id="div-user-data" class="w-100">
                                <!-- Display user data -->
                                <div v-if="!edit">
                                    <div class="mb-3"><span class="text-capitalize"><strong>Nome:</strong> {{ user_name
                                            }}</span></div>
                                    <div class="mb-3"><span><strong>Email:</strong> {{ user_email }}</span></div>
                                    <div class="mb-3"><span><strong>Tipo Utilizador:</strong> {{ user_type }}</span>
                                    </div>
                                    <div class="mb-3"><button class="btn btn-secondary" @click="isEdit">Editar
                                            dados</button></div>
                                </div>

                                <!-- Form -->
                                <div v-else>
                                    <form @submit.prevent="showConfirmationModal">
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
                                        <div class="mb-3">
                                            <button type="submit" id="confirm-changes" class="btn btn-warning"
                                                :disabled="!isChanged || nameError || emailError">Confirmar</button>
                                            <button class="btn btn-dark ml-3"
                                                @click.prevent="cancelEdit">Cancelar</button>
                                        </div>
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Dicionary header -->
                    <div class="row d-flex justify-content-between px-3 mt-5">
                        <h4 class="pb-3 mt-5"># Dicionários</h4>
                        <div class="d-flex align-items-center mb-3 justify-content-end">

                            <!-- "Adicionar palavras" button (visible when dictionary is empty or deleted) -->
                            <button v-if="!hasDictionary && !isAddingDictionary" id="addDictionaryButton"
                                class="btn btn-primary" @click="startDictionary">
                                Adicionar palavras
                            </button>

                            <!-- Spinner (replaces both "Atualizar" and "Apagar" buttons during operations) -->
                            <div v-if="(isUpdatingDictionary || isDeletingDictionary) && hasDictionary"
                                class="d-flex justify-content-center align-items-center mt-3">
                                <div class="spinner"></div>
                            </div>

                            <!-- "Atualizar dicionário" and "Apagar dicionário" buttons (visible when dictionary exists and no operation in progress) -->
                            <div v-else-if="hasDictionary && !isAddingDictionary" class="d-flex">
                                <button v-if="dictionaryQueries.length < 25" class="btn btn-primary mt-3 mr-2"
                                    @click="startDictionaryWithExistingQueries">
                                    +
                                </button>
                                <button class="btn btn-warning mt-3 mr-2" @click="updateDictionary">
                                    Atualizar dicionário
                                </button>
                                <button id="deleteDictionaryButton" class="btn btn-danger mt-3"
                                    @click="deleteDictionary">
                                    Apagar dicionário
                                </button>
                            </div>
                        </div>
                    </div>
                    <!-- Dicionary table -->
                    <div class="pb-5 border-bottom">
                        <div v-if="isAddingDictionary">
                            <form class="form w-100">
                                <div id="div-search-words" class="input-group mt-3">
                                    <input type="text" class="form-control" v-model="newQuery"
                                        placeholder="Digite uma consulta">
                                    <div class="input-group-append">
                                        <button type="submit" class="btn btn-sm btn-outline-dark"
                                            @click.prevent="addQuery"
                                            :disabled="dictionaryQueries.length >= 25">Adicionar</button>
                                    </div>
                                </div>
                            </form>

                            <div v-if="dictionaryQueries.length > 0" class="mt-3">
                                <span v-for="(query, index) in dictionaryQueries" :key="index"
                                    class="badge badge-primary mr-2 text-center">
                                    <span>{{ query.query }}</span>
                                    <button v-if="isNewQuery(query)" type="button" class="btn-close ml-2 d"
                                        aria-label="Close" @click="removeQuery(index)">
                                        <i class="mdi mdi-close pl-2"></i>
                                    </button>
                                </span>
                            </div>

                            <!-- Error message if more than 25 queries are added -->
                            <div v-if="dictionaryQueries.length >= 25" class="text-danger mt-2">
                                Apenas 25 consultas são permitidas.
                            </div>

                            <div class="mt-2">
                                <button class="btn btn-warning mt-2" @click="confirmDictionary"
                                    :disabled="dictionaryQueries.length === 0 || dictionaryQueries.length > 25 || !isChangedQueries()">
                                    Confirmar
                                </button>
                                <button class="btn btn-dark mt-2 ml-1" @click="cancelDictionary">Cancelar</button>
                            </div>
                        </div>

                        <div v-else>
                            <div class="row px-3">
                                <div class="ag-theme-quartz" style="width: 100%; height: 100%;">
                                    <ag-grid-vue :rowData="dictionaryQueries" :columnDefs="dictionaryColumnDefs"
                                        :pagination="true" :paginationPageSize="20" class="ag-theme-quartz"
                                        style="height: 300px"></ag-grid-vue>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- User likes/dislikes header-->
                    <div class="row d-flex justify-content-between px-3 mt-5">
                        <h4 class="pb-3 mt-5"># Histórico de likes/dislikes</h4>
                        <div class="d-flex align-items-center">
                            <button v-if="isLoggedIn" @click="showModal = true" :disabled="posts.length === 0"
                                class="btn btn-primary">
                                Exportar dados
                            </button>
                        </div>
                    </div>
                    <!-- User likes/dislikes table -->
                    <div class="row px-3">
                        <div class="ag-theme-quartz" style="width: 100%; height: 100%;">
                            <ag-grid-vue :rowData="posts" :columnDefs="columnDefs" :pagination="pagination"
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

    <!-- Color Palettes -->
    <div class="row">
        <div class="col-12 grid-margin">
            <div class="card mt-4">
                <div class="card-body">
                    <!-- Title -->
                    <div class="row justify-content-between px-3 pb-4 mb-3">
                        <TitleSection title="Temas de cores" />
                    </div>

                    <!-- Color Palettes -->
                    <div class="palette-container">
                        <div v-for="(palette, index) in colorPalettes" :key="index" class="mb-3 palette-item">
                            <input type="radio" :id="'palette' + index" name="colorPalette" :value="index"
                                v-model="selectedPalette" @change="changePalette" class="styled-radio">
                            <label :for="'palette' + index"></label>
                            <div class="color-squares mr-5">
                                <div v-for="color in palette.colors" :key="color" :style="{ backgroundColor: color }"
                                    class="color-square"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal Export -->
    <Modal v-if="showModal" :title="'Exportar dados'" :show="showModal" :confirmButtonClass="'btn-primary'"
        @confirm="exportToXLSX" @close="showModal = false">
        <p>Tem a certeza de que deseja exportar os dados da tabela?</p>
    </Modal>

    <!-- Confirmation Modal -->
    <Modal v-if="showConfirmation" :title="'Confirmar mudanças'" :show="showConfirmation"
        :confirmButtonClass="'btn-warning'" @confirm="handleSubmit" @close="showConfirmation = false">
        <p>Tem a certeza de que deseja salvar as alterações?</p>
    </Modal>

    <!-- Modal for confirming account deletion -->
    <Modal v-if="showDeleteModal" :title="'Confirmar Apagar Conta'" :show="showDeleteModal"
        :confirmButtonClass="'btn-danger'" @confirm="deleteAccount" @close="showDeleteModal = false">
        <p>Tem a certeza de que deseja apagar sua conta?</p>
    </Modal>
</template>

<script setup>

//#region Imports
import { ref, computed, onMounted } from 'vue'
import { AgGridVue } from "ag-grid-vue3"
import { useRouter } from 'vue-router'
import { useToast } from "vue-toastification"
import { eventBus } from '@/eventBus'
import { useElasticSearchIndexing } from '@/services/useElasticSearchIndexing'

import axios from 'axios'
import * as XLSX from 'xlsx'

import 'vuetify/styles'
import "ag-grid-community/styles/ag-grid.css"
import "ag-grid-community/styles/ag-theme-quartz.css"

import TitleSection from '@/components/TitleSection.vue'
import Modal from '@/components/Modal.vue'

import '@/assets/css/profile.css'
//#endregion

//#region Variables
const toast = useToast()
const router = useRouter()

const emit = defineEmits(['palette-changed'])

const user_name = computed(() => user.value.name)
const user_email = computed(() => user.value.email)
const user_type = computed(() => { return localStorage.getItem('tipo') == 1 ? 'Administrador' : 'Normal' })
const isLoggedIn = computed(() => localStorage.getItem('isLoggedIn') === 'true')
const isAdmin = computed(() => localStorage.getItem('tipo') == 1)

const userId = ref(localStorage.getItem('user_id'))
const selectedPalette = ref(localStorage.getItem('colorPalette') || 0)

const originalUser = ref({ name: '', email: '' })
const newQuery = ref('')

const edit = ref(false)
const loading = ref(false)
const showModal = ref(false)
const showConfirmation = ref(false)
const pagination = ref(true)
const hasDictionary = ref(false)
const isAddingDictionary = ref(false)
const isUpdatingDictionary = ref(false)
const isDeletingDictionary = ref(false)
const showDeleteModal = ref(false)
const canDeleteAccount = ref(true) // This will be updated based on the admin check
const paginationPageSize = ref(20)
const totalPosts = ref(0)
const paginationPageSizeSelector = ref[20, 50, 100]

const dictionaryQueries = ref([])
const posts = ref([])
const originalDictionaryQueries = ref([]) // Store the original queries for comparison

const user = ref({
    name: localStorage.getItem("name") || '',
    email: localStorage.getItem("email") || ''
})
const colorPalettes = ref([
    {
        name: "Default",
        colors: ["#1f262f", "#191c24", "#f8f8f8"]
    },
    {
        name: "Palette 1",
        colors: ["#2e3b4e", "#243447", "#f8f8f8"]
    },
    {
        name: "Palette 2",
        colors: ["#354458", "#2a2e38", "#f8f8f8"]
    },
    {
        name: "Palette 3",
        colors: ["#282c34", "#3a3f44", "#f8f8f8"]
    },
    {
        name: "Palette 4",
        colors: ["#E1E5F2", "#2C3D55", "#f8f8f8"]
    },
    {
        name: "Light Mode",
        colors: ["#f0f0f0", "#e0e0e0", "#2e2e2e"]  // Light theme
    }
])
const options = ref({
    page: 1,
    itemsPerPage: 5,
    sortBy: [],
    sortDesc: [],
    search: '',
})

const { indexingActive, message, startIndexing, stopIndexing, dicionario, deleteIndex } = useElasticSearchIndexing()

const nameError = computed(() => user.value.name.trim() === '')
const emailError = computed(() => !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(user.value.email))
//#endregion

//#region Methods
const isChanged = computed(() => {
    return user.value.name !== originalUser.value.name || user.value.email !== originalUser.value.email
})

const checkIfLastAdmin = async () => {
    if (isAdmin.value) {
        try {
            const response = await axios.get('/admin-count')
            const adminCount = response.data.adminCount

            // If there is only one admin and it's the current user, prevent deletion
            canDeleteAccount.value = adminCount > 1
        } catch (error) {
            console.error('Failed to check if the last admin:', error)
        }
    }
}

// Show confirmation modal for account deletion
const confirmDeleteAccount = () => {
    showDeleteModal.value = true
}

// Handle account deletion
const deleteAccount = async () => {
    try {
        await axios.delete(`/users/${userId.value}`)
        // After account deletion, log out or redirect the user as needed
        localStorage.clear()
        router.push({ name: 'Login' })
        toast.success('Conta eliminada com sucesso!')
    } catch (error) {
        // console.error("Failed to delete account:", error)
        toast.error(`Erro ao apagar conta. Tente novamente mais tarde.`)
    } finally {
        showDeleteModal.value = false
    }
}

const thumbnailRenderer = (params) => {
    return '<div class="no-image-profile"></div>'
}

const likeRenderer = (params) => {
    return params.value.like > 0 ? '<i class="mdi mdi-thumb-up"></i>' : '<i class="mdi mdi-thumb-down"></i>'
}

const buttonRenderer = (params) => {
    return `<a href="https://www.reddit.com/${params.data.permalink}" target="_blank"><i class="mdi mdi-open-in-new"></i></a>`
}

const columnDefs = ref([
    {
        headerName: '',
        field: 'thumbnail',
        sortable: false,
        width: 80,
        resizable: false,
        cellRenderer: thumbnailRenderer,
        cellClass: params => { return 'd-flex align-items-center justify-content-center' }
    },
    {
        headerName: 'Título',
        field: 'post.title',
        filter: true,
        flex: 1,
        valueFormatter: (params) => params.value || '-------------'
    },
    {
        headerName: 'Sentimento',
        field: 'sentiment',
        filter: true,
        sortable: false,
        flex: 1,
        cellDataType: 'object',
        width: 150,
        valueFormatter: (params) => params.data?.post?.scores ? getSentiment(params.data.post.scores) : '---------',
        cellClass: params => { return getBadgeClass(params.data?.post?.scores || {}) }
    },
    {
        headerName: '%',
        field: 'scores',
        filter: true,
        sortable: false,
        flex: 1,
        cellDataType: 'object',
        width: 100,
        valueFormatter: (params) => params.data?.post?.scores ? getSentimentPercentage(params.data.post.scores) : '0%',
        cellClass: params => { return 'text-small' }
    },
    {
        headerName: 'Like/Dislike',
        field: 'like',
        width: 150,
        sortable: false,
        resizable: false,
        valueFormatter: () => '',
        cellRenderer: likeRenderer,
        cellClass: params => { return getBadgeClass(params.data?.post?.scores || {}) }
    },
    {
        headerName: '',
        field: "button",
        sortable: false,
        width: 50,
        resizable: false,
        pinned: 'right',
        cellRenderer: buttonRenderer
    },
])

const isValidName = (thumbnail) => {
    return !(thumbnail.includes('external-preview') || thumbnail.includes('default') || thumbnail.includes('self') || thumbnail.includes('spoiler') || thumbnail.includes('image'))
}

// Computed property to determine the sentiment
const getSentiment = (scores) => {
    if (!scores || typeof scores !== 'object' || Object.keys(scores).length === 0) return 'Unknown'

    let maxScore = -1
    let sentiment = 'Unknown'
    for (const [label, score] of Object.entries(scores)) {
        if (score > maxScore) {
            maxScore = score
            sentiment = label
        }
    }
    return sentiment.charAt(0).toUpperCase() + sentiment.slice(1) // Capitalize the first letter
}

const getSentimentPercentage = (scores) => {
    const sentiment = getSentiment(scores)
    if (sentiment === 'Unknown' || !scores[sentiment]) {
        return '0%'
    }
    const percentage = (scores[sentiment] * 100).toFixed(2)
    return `${percentage}%`
}

const getBadgeClass = (scores) => {
    const sentiment = getSentiment(scores)
    if (sentiment === 'Positivo') return 'text-success'
    if (sentiment === 'Neutro') return 'text-warning'
    if (sentiment === 'Negativo') return 'text-danger'
    return 'text-secondary'
}

// Fetch likes and process data
const fetchLikes = async (page, itemsPerPage, sortBy, sortDesc, search) => {
    loading.value = true

    try {
        const response = await axios.get(`user-likes-posts/${userId.value}`, {
            params: { page, itemsPerPage, sortBy, sortDesc, search }
        })

        if (response.data.length > 0) {
            posts.value = response.data.map(post => {
                const postScores = post.post?.scores || {} // Ensure post.scores exists
                return {
                    ...post,
                    highestSentiment: getSentiment(postScores),
                    displayThumbnail: post.post?.thumbnail || '', // Fallback if thumbnail is missing
                    displayName: isValidName(post.post?.title || ''), // Fallback if title is missing
                    permalink: post.post?.permalink || '#' // Fallback to # if permalink is missing
                }
            })
            totalPosts.value = response.data.length
        } else {
            // toast.error('No data found.')
        }
    } catch (error) {
        // console.error('Error fetching likes:', error)
        // toast.error('Erro ao buscar dados. Tente novamente mais tarde.')
    } finally {
        loading.value = false
    }
}

const handleSubmit = async () => {
    try {
        await axios.patch(`users/${userId.value}`, user.value)
        localStorage.setItem('name', user.value.name)
        localStorage.setItem('email', user.value.email)
        originalUser.value = { ...user.value } // Update the original user data
        edit.value = false // Switch back to view mode
        toast.success('Dados atualizados!')
    } catch (error) {
        // console.error('Failed to submit user data:', error)
        toast.error('Erro. Não é possível realizar essa ação agora.')
    } finally {
        showConfirmation.value = false
    }
}

const isEdit = () => {
    if (!edit.value) {
        originalUser.value = { ...user.value }
    }
    edit.value = !edit.value
}

const cancelEdit = () => {
    user.value = { ...originalUser.value } // Reset user data to original values
    edit.value = false
}

const showConfirmationModal = () => {
    if (isChanged.value) showConfirmation.value = true
}

const changePalette = () => {
    localStorage.setItem('colorPalette', selectedPalette.value)
    eventBus.value.emit('palette-changed', selectedPalette.value)
}

const exportToXLSX = () => {
    if (posts.value.length === 0) return

    try {
        const data = posts.value.map((post, index) => {
            const postTitle = post.post?.title || 'No Title'; // Fallback to 'No Title' if title is missing
            const sentiment = post.post?.scores ? getSentiment(post.post.scores) : 'Unknown';
            const sentimentPercentage = post.post?.scores ? getSentimentPercentage(post.post.scores) : '0%';
            const likeDislike = post.like.like > 0 ? 'Like' : 'Dislike';

            return {
                ID: index + 1,
                Título: postTitle,
                Sentimento: `${sentiment} (${sentimentPercentage})`,
                'Like/Dislike': likeDislike,
            };
        });

        const worksheet = XLSX.utils.json_to_sheet(data);
        const workbook = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(workbook, worksheet, 'Likes_Dislikes');

        XLSX.writeFile(workbook, 'likes_dislikes.xlsx');

        showModal.value = false;  // Close the modal after export
        toast.success('Dados exportados!');
    } catch (error) {
        console.error('Error exporting data to XLSX:', error);
        toast.error('Erro ao exportar dados.');
    }
};


// Dictionary methods

const dictionaryColumnDefs = ref([
    {
        headerName: 'ID',
        field: 'id',
        width: 100,
        sortable: true,
        filter: true,
        resizable: false,
    },
    {
        headerName: 'Query',
        field: 'query',
        flex: 1,
        sortable: true,
        filter: true,
        resizable: false
    }
])

const isNewQuery = (query) => {
    return !originalDictionaryQueries.value.some(
        (originalQuery) => originalQuery.query.toLowerCase() === query.query.toLowerCase()
    )
}

const checkDictionary = async () => {
    try {
        const response = await axios.get(`dictionary/${userId.value}`)
        dictionaryQueries.value = response.data

        if (dictionaryQueries.value.length > 0) {
            hasDictionary.value = true
            originalDictionaryQueries.value = JSON.parse(JSON.stringify(dictionaryQueries.value)) // Save original queries
        } else {
            hasDictionary.value = false
            originalDictionaryQueries.value = []
        }
    } catch (error) {
        console.error('Error checking dictionary:', error)
    }
}

const startDictionary = () => {
    isAddingDictionary.value = true
    newQuery.value = '' // Reset the input field
    dictionaryQueries.value = [] // Clear any existing queries (if starting fresh)
}

const startDictionaryWithExistingQueries = async () => {
    isAddingDictionary.value = true
    newQuery.value = ''

    // Fetch the latest dictionary queries to ensure they are current
    await checkDictionary()

    // Ensure the dictionaryQueries are set to the existing queries
    dictionaryQueries.value = JSON.parse(JSON.stringify(originalDictionaryQueries.value))
}

const isChangedQueries = () => {
    // Compare the original queries with the current queries
    const originalSet = new Set(originalDictionaryQueries.value.map(q => q.query.toLowerCase()))
    const currentSet = new Set(dictionaryQueries.value.map(q => q.query.toLowerCase()))

    // If the sets are not the same, return true
    if (originalSet.size !== currentSet.size) return true

    for (let query of currentSet) {
        if (!originalSet.has(query)) return true
    }
    return false
}

const addQuery = () => {
    const trimmedQuery = newQuery.value.trim().toLowerCase() // Normalize for case-insensitive comparison
    const queryExists = dictionaryQueries.value.some(query => query.query.toLowerCase() === trimmedQuery)

    if (trimmedQuery && !queryExists && dictionaryQueries.value.length < 25) {
        dictionaryQueries.value.push({ query: trimmedQuery })
        newQuery.value = '' // Clear input after adding
    } else if (queryExists) {
        toast.error('Esta consulta já foi adicionada.')
    } else if (dictionaryQueries.value.length >= 25) {
        toast.error('Apenas 25 consultas são permitidas.')
    }
}

const removeQuery = (index) => {
    dictionaryQueries.value.splice(index, 1)
}

const confirmDictionary = async () => {
    const newQueries = dictionaryQueries.value.filter(isNewQuery);

    if (newQueries.length > 0) {
        try {
            await axios.post('dictionary', {
                user_id: userId.value,
                queries: newQueries.map((q) => q.query),
            })

            isAddingDictionary.value = false
            await checkDictionary() // Recheck dictionary status

            // Update the original queries to reflect the current state after addition
            originalDictionaryQueries.value = JSON.parse(JSON.stringify(dictionaryQueries.value))

            toast.success('Dicionário atualizado!')
        } catch (error) {
            // console.error('Error saving dictionary:', error)
            toast.error('Erro ao salvar o dicionário.')
        }
    } else {
        toast.error('Adicione novas consultas antes de confirmar.')
    }
}

const cancelDictionary = () => {
    isAddingDictionary.value = false
    newQuery.value = ''
    dictionaryQueries.value = JSON.parse(JSON.stringify(originalDictionaryQueries.value)) // Reset to original queries
}

const updateDictionary = async () => {
    isUpdatingDictionary.value = true
    isDeletingDictionary.value = false // Ensure that the delete button is also hidden

    dicionario.value = dictionaryQueries.value.map(row => row.query)
    await startIndexing() // Start the indexing process

    isUpdatingDictionary.value = false // Reset to the correct state after update
    toast.success('Dicionário atualizado!')
}

const deleteDictionary = async () => {
    isDeletingDictionary.value = true
    isUpdatingDictionary.value = false

    await deleteIndex() // Modulo 2 Leandro Vieira
    await axios.delete(`dictionary/${userId.value}`)

    dictionaryQueries.value = []
    originalDictionaryQueries.value = [] // Reset original queries after deletion
    hasDictionary.value = false

    isDeletingDictionary.value = false
    isAddingDictionary.value = false

    toast.success('Dicionário eliminado!')
}
//#endregion

//#region Lifecycle Hooks
onMounted(async () => {
    // Fetch likes when the component is mounted
    fetchLikes(
        options.value.page,
        options.value.itemsPerPage,
        options.value.sortBy,
        options.value.sortDesc,
        options.value.search
    )

    // Check if the dictionary exists and load it
    await checkDictionary()

    // Check if the user is the last admin
    checkIfLastAdmin()

    // Store the original state of the dictionary queries
    originalDictionaryQueries.value = JSON.parse(JSON.stringify(dictionaryQueries.value))

    // Ensure the "Confirmar" button is disabled if no changes were made
    isAddingDictionary.value = false
})
//#endregion

</script>