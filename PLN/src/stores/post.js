import { ref, inject, onMounted } from "vue"
import { defineStore } from "pinia"
import { useToast } from "vue-toastification"
import axios from 'axios'

export const usePostStore = defineStore("post", () => {
    const redditAxios = inject("redditAxios")
    const toast = useToast()
    const posts = ref([])

    const getAccessToken = async () => {
        const storedToken = sessionStorage.getItem('access_token')
        if (storedToken) {
            return { data: { access_token: storedToken } }
        }
        try {
            const response = await axios.get('/get_access_token')
            const token = response.data.access_token
            sessionStorage.setItem('access_token', token)
            return { data: { access_token: token } }
        } catch (error) {
            toast.error('Erro do servidor! Tente mais tarde.')
            throw error
        }
    }

    const getData = async (token, word, quantity, order, topic, isFiltersEnabled, isElasticEnabled, userId) => {
        try {
            let endpoint, params

            if (isFiltersEnabled) {
                endpoint = '/question'
                params = !isElasticEnabled ? { query: word } : { query: word, elastic_search: userId }
            } else {
                endpoint = topic ? '/search/tfidf/topic' : '/search'
                params = { query: word, sort: order, limit: quantity, topic: topic }
            }

            const response = await redditAxios.get(endpoint, {
                headers: { Authorization: `Bearer ${token}` },
                params
            })
            return response
        } catch (error) {
            toast.error('Erro ao ir buscar os dados! Tente mais tarde.')
            throw error
        }
    }

    const saveFetchedData = async (data) => {
        try {
            const response = await axios.post('/get_data', data, {
                headers: { 'Content-Type': 'application/json' }
            })
            return response
        } catch (error) {
            toast.error('Erro do servidor! Tente mais tarde.')
            throw error
        }
    }

    const fetchLikesDislikes = async (postIds) => {
        try {
            const response = await axios.post('/get_likes_dislikes', { post_ids: postIds })
            return response.data
        } catch (error) {
            // toast.error('Erro ao ir buscar os gostos! Tente mais tarde.')
            console.clear()
        }
    }
    
    const getAnalysis = async (data, endpoint) => {

        try {
            const response = await axios.post(endpoint, { data })
            return response
        } catch (error) {
            // toast.error('Erro do servidor! Tenta mais tarde.')
            console.clear()
        }
    }

    return {
        posts,
        getAccessToken,
        getData,
        saveFetchedData,
        fetchLikesDislikes,
        getAnalysis
    }
})
