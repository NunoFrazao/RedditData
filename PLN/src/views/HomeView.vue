<template>
    <div class="d-flex justfify-content-around">
        <!-- Main part -->
        <div class="w-100">
            <!-- Cookie Consent Component -->
            <CookieConsent />

            <!-- Search bar -->
            <div class="row">
                <div class="col grid-margin stretch-card">
                    <div class="card card-shadow">
                        <div class="card-body">
                            <!-- Title -->
                            <div class="row justify-content-between px-3 pb-4">
                                <!-- Search title -->
                                <TitleSection title="Pesquisar Keywords" />

                                <!-- Filter button -->
                                <div v-if="store.isLoggedIn"
                                    class="d-flex align-items-center justify-content-md-end pt-3">
                                    <!-- GPT style + Elastic search -->
                                    <div v-if="isFiltersEnabled" id="div-toggle-switch"
                                        class="d-flex align-items-center justify-content-md-end mr-5">
                                        <span>Elastic</span>
                                        <label class="switch ml-3 mb-0">
                                            <input type="checkbox" v-model="isElasticEnabled"
                                                :disabled="isDictionaryEmpty">
                                            <span class="slider round"
                                                :class="{ 'disabled-slider': isDictionaryEmpty }"></span>
                                        </label>
                                    </div>

                                    <!-- GPT style search -->
                                    <div id="div-toggle-switch"
                                        class="d-flex align-items-center justify-content-md-end">
                                        <span v-if="!isFiltersEnabled">Pesquisa avançada</span>
                                        <span v-if="isFiltersEnabled">Pesquisa chat gpt</span>
                                        <label class="switch ml-3 mb-0">
                                            <input type="checkbox" v-model="isFiltersEnabled">
                                            <span class="slider round"></span>
                                        </label>
                                    </div>
                                </div>
                            </div>

                            <!-- Filters -->
                            <div class="row" v-if="!isFiltersEnabled">
                                <button type="button" class="btn text-light mb-3" data-bs-toggle="collapse"
                                    data-bs-target="#collapseFilters" aria-expanded="false"
                                    aria-controls="collapseFilters" v-if="!isFiltersEnabled">Filtros <i
                                        class="mdi mdi-chevron-down"></i></button>
                            </div>

                            <!-- Form -->
                            <div class="row">
                                <form class="form w-100">
                                    <!-- Filters -->
                                    <div class="col-12 collapse" id="collapseFilters" v-if="!isFiltersEnabled">
                                        <div id="div-filters" class="card card-body mb-2">
                                            <!-- Filters Section -->
                                            <div class="row">
                                                <!-- Quantity Filter -->
                                                <div class="col-6 col-sm-4">
                                                    <label for="quantity-select" class="form-label">Quantidade</label>
                                                    <select class="form-control" id="quantity-select"
                                                        name="selectedQuantity" v-model="selectedQuantity">
                                                        <option value="5">5</option>
                                                        <option value="10" selected>10</option>
                                                        <option value="25">25</option>
                                                        <option value="50">50</option>
                                                        <option value="100">100</option>
                                                    </select>
                                                </div>

                                                <!-- Order By Filter -->
                                                <div class="col-6 col-sm-4">
                                                    <label for="order-select" class="form-label">Ordenar Por</label>
                                                    <select class="form-control" id="order-select" name="selectedOrder"
                                                        v-model="selectedOrder">
                                                        <option value="relevance" selected>Relevância</option>
                                                        <option value="hot">Hot</option>
                                                        <option value="top">Top</option>
                                                        <option value="new">New</option>
                                                        <option value="comments">Comments</option>
                                                    </select>
                                                </div>

                                                <!-- Model Choice Filter -->
                                                <div id="div-filter-model" class="col-12 col-sm-4">
                                                    <label for="model-select" class="form-label">Modelo de
                                                        análise</label>
                                                    <select class="form-control" id="model-select" name="selectedModel"
                                                        v-model="selectedModel">
                                                        <option value="roberta" selected>Precisão (mais devagar)
                                                        </option>
                                                        <option value="vader">Desempenho (mais rápido)</option>
                                                    </select>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- Search input -->
                                    <ul class="list-unstyled w-100">
                                        <li class="nav-item w-100">
                                            <!-- Search input -->
                                            <ul class="list-unstyled w-100 px-3">
                                                <li class="nav-item w-100">
                                                    <div id="search-div" class="input-group search-input-group">
                                                        <input class="form-control py-4" type="text"
                                                            aria-label="Search for keyword"
                                                            :placeholder="!isFiltersEnabled ? 'Procurar por keywords' : 'Pesquise algo aqui...'"
                                                            name="word" v-model="word">
                                                        <input class="form-control py-4 ml-1" type="text"
                                                            aria-label="Search for topic (optional)"
                                                            placeholder="Tópico (opcional)" name="topic" v-model="topic"
                                                            v-if="!isFiltersEnabled && store.isLoggedIn">
                                                        <button type="submit" id="btn-search" class="btn btn-sm"
                                                            @click.prevent="fetchData"
                                                            :disabled="isSearchDisabled || !canSearch">Pesquisar</button>
                                                    </div>
                                                </li>
                                            </ul>
                                        </li>
                                    </ul>
                                </form>

                                <!-- Timer display -->
                                <div v-if="!canSearch" class="col-12 text-center mt-3">
                                    <p class="text-warning">Pode pesquisar novamente em {{ remainingTime }} segundos.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Loading spinner -->
            <div v-if="isLoading && remainingTime === 0" class="row loading-spinner search-results">
                <div class="col grid-margin stretch-card">
                    <div class="card card-shadow">
                        <div class="card-body">
                            <div class="row justify-content-center">
                                <div class="spinner"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Search results -->
            <div v-if="searchData.length > 0" id="div-search-data" class="row mt-5 search-results d-flex">
                <div id="results-shown" class="col-12 grid-margin">
                    <!-- Output title & types of grid -->
                    <div class="row justify-content-between px-3">
                        <div class="d-flex align-items-center">
                            <h4 class="card-title text-uppercase">Resultados encontrados para <strong
                                    class="text-primary">{{
                                        words_together }}</strong></h4>
                        </div>

                        <div class="d-flex justify-content-end align-items-center">
                            <!-- Toggle view buttons -->
                            <div class="view-toggle-buttons text-center mb-3">
                                <button class="btn" @click="viewType(false)"><i class="mdi mdi-view-grid"></i></button>
                                <button class="btn" @click="viewType(true)"><i
                                        class="mdi mdi-format-list-bulleted"></i></button>
                            </div>
                        </div>
                    </div>

                    <!-- Filter buttons -->
                    <div class="row mb-4 filter-buttons">
                        <!-- Sort dropdown -->
                        <div class="col d-flex justify-content-between pb-4">
                            <button class="btn btn-outline-secondary dropdown-toggle" type="button"
                                id="dropdownSortButton" data-bs-toggle="dropdown" aria-expanded="false">
                                Ordenar por
                            </button>

                            <ul class="dropdown-menu" aria-labelledby="dropdownSortButton">
                                <li><a class="dropdown-item" href="#" @click.prevent="sortOption = 'sentimentAsc'">Peso
                                        ascendente</a></li>
                                <li><a class="dropdown-item" href="#" @click.prevent="sortOption = 'sentimentDesc'">Peso
                                        descendente</a></li>
                                <li><a class="dropdown-item" href="#" @click.prevent="sortOption = 'likes'">Likes</a>
                                </li>
                                <li><a class="dropdown-item" href="#"
                                        @click.prevent="sortOption = 'dislikes'">Dislikes</a></li>
                            </ul>

                            <!-- Sentiment filter buttons -->
                            <FilterButtons :searchData="searchData" :selectedSentiment="selectedSentiment"
                                @update:selectedSentiment="selectedSentiment = $event" />
                        </div>
                    </div>

                    <!-- No results message -->
                    <div v-if="filteredData.length === 0" class="row">
                        <div class="col grid-margin stretch-card">
                            <div class="card card-shadow">
                                <div class="card-body">
                                    <div class="row justify-content-center">
                                        <div class="col text-center">
                                            <p class="m-0">0 resultados <strong>{{ noResultsMessage }}</strong></p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Search results in card view -->
                    <div v-if="!isListView && filteredData.length > 0" class="row">
                        <div class="col-sm-6 col-md-4 col-xl-3 mb-3" v-for="(item, index) in filteredData" :key="index">
                            <div class="card h-100 search-input-group">
                                <div class="image-container position-relative" @click="() => openModal(item)">
                                    <a class="see-more">
                                        <img v-if="isValidName(item.thumbnail)" :src="isValidThumbnail(item.thumbnail)"
                                            :alt="isValidName(item.thumbnail)" class="card-img-top">
                                        <div v-else class="no-image"></div>
                                    </a>
                                </div>

                                <div class="card-body d-flex flex-column p-0">
                                    <div class="p-3">
                                        <h5 class="card-title my-3 font-weight-bold">{{ item.title }}</h5>
                                        <p class="card-text flex-grow-1">{{ item.selftext || '-----------------------'
                                            }}
                                        </p>
                                        <p class="card-text">
                                            <strong class="text-warning">Sentimento:</strong> {{
                                                getSentiment(item.scores)
                                            }}
                                            <span class="small">({{ getSentimentPercentage(item.scores) }})</span>
                                        </p>
                                        <div class="likes-dislikes">
                                            <span>Likes: {{ item.likes }}</span>
                                            <span class="pl-2">Dislikes: {{ item.dislikes }}</span>
                                        </div>
                                    </div>
                                </div>

                                <!-- Like & Dislike buttons -->
                                <div class="card-footer p-0" v-if="showControlls">
                                    <button class="btn w-50"
                                        @click.prevent="sendLikeDislike(item.id, item.user_like === 1 ? 0 : 1)">
                                        <i
                                            :class="item.user_like === 1 ? 'mdi mdi-thumb-up' : 'mdi mdi-thumb-up-outline'"></i>
                                    </button>
                                    <button class="btn w-50 border-left"
                                        @click.prevent="sendLikeDislike(item.id, item.user_like === -1 ? 0 : -1)">
                                        <i
                                            :class="item.user_like === -1 ? 'mdi mdi-thumb-down' : 'mdi mdi-thumb-down-outline'"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Search results in list view -->
                    <div v-if="isListView && filteredData.length > 0" class="list-view">
                        <div class="horizontal-card" v-for="(item, index) in filteredData" :key="index">
                            <div class="col-3 pl-0">
                                <div class="image-container position-relative" @click="() => openModal(item)">
                                    <a class="see-more">
                                        <img v-if="isValidName(item.thumbnail)" :src="isValidThumbnail(item.thumbnail)"
                                            :alt="isValidName(item.thumbnail)" class="card-img-top">
                                        <div v-else class="no-image"></div>
                                    </a>
                                </div>
                            </div>
                            <div class="card-body d-flex justify-content-between">
                                <div class="div-info">
                                    <h5 class="card-title my-3 font-weight-bold">{{ item.title }}</h5>
                                    <p class="card-text flex-grow-1">{{ item.selftext || '-----------------------' }}
                                    </p>
                                    <p class="card-text">
                                        <strong class="text-warning">Sentimento:</strong> {{ getSentiment(item.scores)
                                        }}
                                        <span class="small">({{ getSentimentPercentage(item.scores) }})</span>
                                    </p>
                                    <div class="likes-dislikes">
                                        <span>Likes: {{ item.likes }}</span>
                                        <span class="pl-2">Dislikes: {{ item.dislikes }}</span>
                                    </div>
                                </div>

                                <!-- Like & Dislike buttons -->
                                <div class="border-left">
                                    <div
                                        class="d-flex flex-column justify-content-around align-items-center ml-3 h-100">
                                        <button class="btn mb-1"
                                            @click.prevent="sendLikeDislike(item.id, item.user_like === 1 ? 0 : 1)">
                                            <i
                                                :class="item.user_like === 1 ? 'mdi mdi-thumb-up' : 'mdi mdi-thumb-up-outline'"></i>
                                        </button>
                                        <button class="btn mt-1"
                                            @click.prevent="sendLikeDislike(item.id, item.user_like === -1 ? 0 : -1)">
                                            <i
                                                :class="item.user_like === -1 ? 'mdi mdi-thumb-down' : 'mdi mdi-thumb-down-outline'"></i>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Sliding div for post details -->
                <div class="col-12 post-details-container">
                    <div class="card">
                        <div id="post-card-body" class="card-body">
                            <div class="row justify-content-center mx-2">
                                <div class="post-details" :class="{ 'show': showPostDetails }">
                                    <!-- Button go back -->
                                    <button id="button-go-back" class="d-flex ml-0" @click="closePostDetails">
                                        <i class="mdi mdi-arrow-left mr-3"></i>
                                        Voltar para os resultados
                                    </button>
                                    <hr class="mt-4 mb-3" />

                                    <!-- Post details -->
                                    <div v-if="currentPost" class="mt-5">
                                        <!-- Title -->
                                        <h4 class="text-warning">{{ currentPost.title }}</h4>
                                        <span class="small">Ver o post completo <a
                                                :href="'https://www.reddit.com' + currentPost.permalink"
                                                target="_blank">aqui</a></span>

                                        <!-- Image -->
                                        <div class="image-container position-relative mt-5">
                                            <a class="see-more-details">
                                                <img v-if="isValidName(currentPost.thumbnail)"
                                                    :src="isValidThumbnail(currentPost.thumbnail)"
                                                    :alt="isValidName(currentPost.thumbnail)" class="card-img-top">
                                                <div v-else class="no-image"></div>
                                            </a>
                                        </div>

                                        <!-- Description, sentiments and likes -->
                                        <div class="mt-5">
                                            <!-- Description -->
                                            <span class="font-weight-bold">Descrição</span>
                                            <p class="post-description pt-3">
                                                {{ currentPost.selftext || 'Sem descrição' }}
                                            </p>

                                            <hr class="mt-4 mb-3" />

                                            <div class="d-flex my-5">
                                                <!-- Sentiment -->
                                                <p class="mr-5 my-0 pr-5"><strong
                                                        class="text-warning">Sentimento:</strong> {{
                                                            getSentiment(currentPost.scores) }}
                                                    <span class="small">({{ getSentimentPercentage(currentPost.scores)
                                                        }})</span>
                                                </p>

                                                <!-- Like & Dislike buttons -->
                                                <div class="likes-dislikes ml-5 d-flex">
                                                    <span class="d-flex align-items-center">
                                                        <i class="mdi mdi-thumb-up mr-1"></i>
                                                        {{ currentPost.likes }}
                                                    </span>
                                                    <span class="d-flex align-items-center ml-5">
                                                        <i class="mdi mdi-thumb-down mr-1"></i>
                                                        {{ currentPost.dislikes }}
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                        <hr class="mt-4 mb-3" v-if="showControlls == true" />

                                        <!-- Comments -->
                                        <div v-if="showControlls == true" class="mt-5">
                                            <h4 class="first-title pr-3 pb-4 display-5 text-uppercase">
                                                Comentários
                                            </h4>

                                            <div v-if="isCommentsLoading" class="row loading-spinner">
                                                <div class="spinner mx-auto"></div>
                                            </div>

                                            <div v-else id="accordion">
                                                <div v-for="(comment, index) in comments" :key="index"
                                                    class="card mb-1 comments-cards">
                                                    <div class="card-header p-0" :id="'heading' + index">
                                                        <button class="btn w-100 text-left py-2"
                                                            data-bs-toggle="collapse"
                                                            :data-bs-target="'#collapse' + index" aria-expanded="true"
                                                            :aria-controls="'collapse' + index">
                                                            <span class="badge badge-dark badge-comments mr-3"
                                                                :class="getBadgeClass(comment.scores)">
                                                                {{ getSentiment(comment.scores) }}
                                                                <span class="small">({{
                                                                    getSentimentPercentage(comment.scores) }})</span>
                                                            </span>
                                                            Comentário <span class="text-warning">#{{ index + 1
                                                                }}</span>
                                                            <i class="mdi mdi-chevron-down"></i>
                                                        </button>
                                                    </div>

                                                    <div :id="'collapse' + index" class="collapse"
                                                        :aria-labelledby="'heading' + index"
                                                        data-bs-parent="#accordion">
                                                        <div class="card-body">
                                                            {{ comment.body }}
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Aside -->
        <aside id="aside-div" class="pl-5 d-none d-xl-flex flex-column">
            <div class="aside-section">
                <div class="aside-content">
                    <h4>{{ adTitle }}</h4>
                    <p>{{ adText }}</p>
                    <RouterLink to="/register">
                        <button v-if="!store.isLoggedIn" class="btn btn-primary">{{ adButton }}</button>
                    </RouterLink>
                </div>
            </div>

            <div class="mt-5">
                <!-- Additional content or placeholders can be added here -->
            </div>
        </aside>
    </div>
</template>

<script setup>

//#region Imports
import { ref, computed, onMounted } from 'vue'
import { store } from '@/stores/login'
import { useToast } from "vue-toastification"
import { useUserStore } from '@/stores/user'
import { usePostStore } from '@/stores/post'

import axios from 'axios'
import FilterButtons from '@/components/FilterButtons.vue'
import TitleSection from '@/components/TitleSection.vue'
import CookieConsent from '@/components/CookieConsent.vue'

import '@/assets/css/index.css'
import '@/assets/js/filters.js'
//#endregion

//#region Variables
const toast = useToast()
const userStore = useUserStore()
const postStore = usePostStore()

const user_id = ref(localStorage.getItem('user_id'))

const word = ref('')
const word_aux = ref('')
const topic = ref('')
const topic_aux = ref('')
const words_together = ref('')
const accessToken = ref('')

const isListView = ref(false)
const isLoading = ref(false)
const isCommentsLoading = ref(false)
const canSearch = ref(true)
const isFiltersEnabled = ref(false)
const showPostDetails = ref(false)
const isElasticEnabled = ref(false)
const isDictionaryEmpty = ref(true)
const selectedQuantity = ref(10)
const remainingTime = ref(0)

const sortOption = ref('sentimentDesc')
const selectedOrder = ref('relevance')
const selectedModel = ref('roberta')
const selectedSentiment = ref('')

const currentPost = ref({})
const searchData = ref([])
const comments = ref([])
//#endregion

//#region Methods
const adTitle = computed(() => store.isLoggedIn ? 'Bem-vindo de volta!' : 'Oferta Exclusiva!')
const adText = computed(() => store.isLoggedIn ? 'Explore recursos premium personalizados para você.' : 'Cadastre-se agora para ter acesso a recursos premium.')
const adButton = computed(() => store.isLoggedIn ? '' : 'Cadastre-se')

const isSearchDisabled = computed(() => { return word.value.trim() === '' })

const showControlls = computed(() => store.isLoggedIn)

const viewType = (isList) => { isListView.value = isList }

const startTimer = (duration) => {
    remainingTime.value = duration
    const timer = setInterval(() => {
        remainingTime.value -= 1
        if (remainingTime.value <= 0) {
            clearInterval(timer)
            canSearch.value = true
        }
    }, 1000)
}

const openModal = (post) => {
    currentPost.value = post
    showPostDetails.value = true
    document.querySelector('.search-results').classList.add('slide-left')
    document.querySelector('.post-details-container').classList.add('show')
    document.querySelector('#results-shown').classList.add('shown')
    fetchComments(post.id)

    // Scroll to the top of the page
    window.scrollTo({ top: 0, behavior: 'smooth' })
}

const checkDictionaryEmpty = async () => {
    try {
        const response = await axios.get(`/dictionary/${user_id.value}`)
        isDictionaryEmpty.value = response.data.length === 0
    } catch (error) {
        // console.error('Error checking dictionary:', error)
        toast.error('Ocorreu um erro ao verificar o dicionário.')
    }
}

const closePostDetails = () => {
    showPostDetails.value = false
    document.querySelector('.search-results').classList.remove('slide-left')
    document.querySelector('.post-details-container').classList.remove('show')
    document.querySelector('#results-shown').classList.remove('shown')
}

const isValidThumbnail = (thumbnail) => {
    return typeof thumbnail === 'string' && (thumbnail.includes('external-preview') || thumbnail.includes('default') || thumbnail.includes('self') || thumbnail.includes('spoiler') || thumbnail.includes('image')) ? '../assets/img/reddit-post-background.jpg' : thumbnail
}

const isValidName = (thumbnail) => {
    return typeof thumbnail === 'string' && (thumbnail.includes('external-preview') || thumbnail.includes('default') || thumbnail.includes('self') || thumbnail.includes('spoiler') || thumbnail.includes('image')) ? false : true
}

const fetchData = () => {
    isLoading.value = true
    searchData.value = []
    word_aux.value = word.value
    topic_aux.value = topic.value
    words_together.value = word.value + ' ' + topic.value

    if (!userStore.verifyRequests()) {
        canSearch.value = false
        isLoading.value = false
        const time = 60
        startTimer(time)
        return
    }

    postStore.getAccessToken().then(response => {
        accessToken.value = response.data.access_token
        return postStore.getData(accessToken.value, word.value, selectedQuantity.value, selectedOrder.value, topic.value, isFiltersEnabled.value, isElasticEnabled.value, user_id.value)
    }).then(redditDataResponse => {
        const data = redditDataResponse.data.data // Extract the actual data
        if (!Array.isArray(data)) {
            throw new Error('Erro! Formato errado.') // Throw an error if data is not an array
        }

        const count = data.length
        userStore.countUp(count)

        // Save the fetched data to data.txt via the backend
        return postStore.saveFetchedData(data).then(() => {
            const postIds = data.map(post => post.id)
            return postStore.fetchLikesDislikes(postIds)
        }).then(likesDislikesData => {
            const analyzeEndpoint = (selectedModel.value === 'roberta' || isFiltersEnabled.value) ? '/analyze' : '/analyze/vader'

            return postStore.getAnalysis(data, analyzeEndpoint).then(dataResponse => {
                searchData.value = dataResponse.data

                // Merge likes/dislikes data with search data
                searchData.value.forEach(post => {
                    const postId = post.id
                    if (likesDislikesData[postId]) {
                        post.likes = likesDislikesData[postId].likes
                        post.dislikes = likesDislikesData[postId].dislikes
                        post.user_like = likesDislikesData[postId].user_like
                    } else {
                        post.likes = 0
                        post.dislikes = 0
                        post.user_like = 0
                    }
                })

                // Store the search in history
                storeSearchInHistory()

                isLoading.value = false
                word.value = ''
                topic.value = ''
            })
        })
    }).catch(error => {
        if (error.response && error.response.status === 429) {
            userStore.timeLastRequest.value = Date.now()
            canSearch.value = false
            isLoading.value = false
            const time = 60
            startTimer(time)
            // Optionally, call countUp with 1 request
            userStore.countUp(1)
        }

        // console.error('There was an error!', error)
        if (isElasticEnabled.value) toast.error('Palavra-chave não encontrada no dicionário.')
        else toast.error('Erro ao buscar os dados. Tente novamente.')
        isLoading.value = false
    })
}

const storeSearchInHistory = () => {
    const payload = {
        user_id: user_id.value,
        query: words_together.value, // The search query (keyword + topic)
        tipo_pesquisa: isElasticEnabled.value
            ? 'elastic'
            : isFiltersEnabled.value
                ? 'gpt'
                : topic.value.trim() !== ''
                    ? 'topic'
                    : 'normal' // Determine the search type
    }

    // if user is logged in then save the search history
    if (store.isLoggedIn) {
        axios.post('users/history', payload).then(response => {
            // console.log('Search history saved successfully:', response.data.message)
        }).catch(error => {
            console.error('Error saving search history:', error)
        })
    }
}

const getCommentsData = (token, postId) => {
    return axios.get(`/comments/${postId}`, {
        headers: {
            Authorization: `Bearer ${token}`
        }
    })
}

const fetchComments = (postId) => {
    isCommentsLoading.value = true

    getCommentsData(accessToken.value, postId).then(response => {
        comments.value = response.data
        return axios.get('/analyze_comments')
    }).then(analyzedResponse => {
        comments.value = analyzedResponse.data

        // Merge analyzed sentiment scores with comments
        comments.value.forEach(comment => {
            const analyzedComment = analyzedResponse.data.find(ac => ac.id === comment.id)
            if (analyzedComment) comment.scores = analyzedComment.scores
        })
        isCommentsLoading.value = false
    }).catch(error => {
        console.error('There was an error fetching comments!', error)
    })
}

const fetchLikeDislikeCounts = async (postId) => {
    try {
        const response = await axios.get(`/likes/${postId}`, {
            params: { user_id: user_id.value }
        })
        return {
            likes: response.data.likes,
            dislikes: response.data.dislikes,
            user_like: response.data.user_like
        }
    } catch (error) {
        console.error('There was an error fetching like/dislike counts!', error)
        return { likes: 0, dislikes: 0, user_like: 0 } // Default values in case of error
    }
}

const sendLikeDislike = async (postId, likeValue) => {
    if (!user_id.value) return

    const payload = {
        post_id: postId,
        user_id: user_id.value,
    }

    const endpoint = likeValue === 1 ? '/like' : (likeValue === -1 ? '/dislike' : '/neutral')

    try {
        await axios.post(endpoint, payload)

        // Update the specific post in the searchData array
        const post = searchData.value.find(post => post.id === postId)
        if (post) {
            const counts = await fetchLikeDislikeCounts(postId)
            post.likes = counts.likes
            post.dislikes = counts.dislikes
            post.user_like = counts.user_like
        }
    } catch (error) {
        console.error('There was an error!', error)
    }
}

// Computed property to determine the sentiment
const getSentiment = (scores) => {
    if (!scores || typeof scores !== 'object' || Object.keys(scores).length === 0) return 'Unknown'

    let maxScore = -1
    let sentiment = 'Unknown' // Default sentiment if no scores are found
    for (const [label, score] of Object.entries(scores)) {
        if (score > maxScore) {
            maxScore = score
            sentiment = label
        }
    }
    return sentiment
}

const getSentimentPercentage = (scores) => {
    const sentiment = getSentiment(scores)
    if (sentiment === 'Unknown' || !scores[sentiment]) {
        return '0%'
    }
    const percentage = (scores[sentiment] * 100).toFixed(2)
    return `${percentage}%`
}

// Filtered search data based on sentiment
const filteredData = computed(() => {
    let filtered = searchData.value
    if (selectedSentiment.value !== '') {
        filtered = searchData.value.filter(item => getSentiment(item.scores) === selectedSentiment.value)
    }
    return applySorting(filtered)
})

const applySorting = (data) => {
    if (sortOption.value === 'sentimentAsc') {
        return data.sort((a, b) => {
            const aScore = getSentiment(a.scores) ? a.scores[getSentiment(a.scores)] : 0
            const bScore = getSentiment(b.scores) ? b.scores[getSentiment(b.scores)] : 0
            return aScore - bScore
        })
    }
    if (sortOption.value === 'sentimentDesc') {
        return data.sort((a, b) => {
            const aScore = getSentiment(a.scores) ? a.scores[getSentiment(a.scores)] : 0
            const bScore = getSentiment(b.scores) ? b.scores[getSentiment(b.scores)] : 0
            return bScore - aScore
        })
    }
    if (sortOption.value === 'likes') {
        return data.sort((a, b) => b.likes - a.likes)
    }
    if (sortOption.value === 'dislikes') {
        return data.sort((a, b) => b.dislikes - a.dislikes)
    }
    return data
}

const noResultsMessage = computed(() => {
    switch (selectedSentiment.value) {
        case 'Positivo':
            return 'positivos'
        case 'Neutro':
            return 'neutros'
        case 'Negativo':
            return 'negativos'
        default:
            return 'para a pesquisa'
    }
})

const getBadgeClass = (scores) => {
    const sentiment = getSentiment(scores)
    if (sentiment === 'Positivo') return 'text-success'
    if (sentiment === 'Neutro') return 'text-warning'
    if (sentiment === 'Negativo') return 'text-danger'
    return 'text-secondary' // Default class if sentiment is unknown or not in the expected set
}
//#endregion

//#region Lifecycle hooks
onMounted(() => {
    checkDictionaryEmpty()
})
//#endregion

</script>