import { ref, inject } from 'vue'
import { searchReddit } from '@/services/useRedditSearch'
import axios from 'axios'


export function useElasticSearchIndexing() {
    const indexingActive = ref(false)
    const message = ref('')
    const dicionario = ref([])
    const elasticsearch = inject("elasticsearch")
    const elasticAxios = inject("elasticAxios")

    // Função para pausar a execução
    const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms))

    const user_id = localStorage.getItem('user_id')
    const indexName = `reddit_posts_${user_id}`

    const createIndex = async () => {
        try {
            // Tenta criar o índice
            const response = await elasticAxios.put(`${indexName}`, {
                settings: {
                    number_of_shards: 1,
                    number_of_replicas: 0,
                },
                mappings: {
                    properties: {
                        id: { type: 'keyword' },
                        title: { type: 'text' },
                        selftext: { type: 'text' },
                        thumbnail: { type: 'text' },
                        permalink: { type: 'text' },
                    },
                },
            }, {
                headers: {
                    'Content-Type': 'application/json'
                },
            })

            // console.log('Índice criado com sucesso:', response.data)
        } catch (error) {
            if (error.response && error.response.status === 400 && error.response.data.error.type === 'resource_already_exists_exception') {
                // console.log(`Índice ${indexName} já existe. Ignorando.`)
            } else {
                // console.error('Erro ao criar o índice:', error.response ? error.response.data : error.message)
            }
            console.clear()
        }
    }

    const deleteIndex = async () => {
        try {
            const response = await elasticAxios.delete(`${indexName}`, {
                headers: {
                    'Content-Type': 'application/json'
                },
            })
            // console.log('Índice deletado com sucesso:', response.data)
            message.value = 'Índice deletado com sucesso.'
        } catch (error) {
            // console.error('Erro ao deletar o índice:', error.response ? error.response.data : error.message)
            message.value = 'Erro ao deletar o índice.'
        }

        console.clear()
    }

    const indexPosts = async (posts) => {
        await createIndex()
    
        // Prepare bulkBody as an array of newline-delimited JSON strings
        let bulkBody = ''
    
        posts.forEach(post => {
            bulkBody += JSON.stringify({
                index: {
                    _index: indexName,
                    _id: post.id
                }
            }) + '\n'
            bulkBody += JSON.stringify(post) + '\n'
        })
    
        try {
            const response = await elasticAxios.post(`${indexName}/_doc/_bulk`, bulkBody, {
                headers: {
                    'Content-Type': 'application/x-ndjson' // Correct content type for bulk requests
                }
            })
    
            if (response.data.errors) {
                // console.error('Bulk indexing encountered errors:', response.data.items)
            } else {
                // console.log('Bulk indexing completed successfully.')
            }
        } catch (error) {
            console.error('Error during bulk indexing:', error.response ? error.response.data : error.message)
        }
    }

    // Função para executar a indexação para uma consulta
    const runIndexing = async (query) => {
        const data = await searchReddit(query) // Usa a função searchReddit
        await indexPosts(data.ids.map((id, index) => ({
            id,
            title: data.titles[index],
            selftext: data.selftexts[index],
            thumbnail: data.thumbnails[index],
            permalink: data.permalinks[index]
        })))
        return data.countRequests
    }

    const loopIndexing = async (i = 0, count = 0) => {
        while (i < dicionario.value.length && indexingActive.value) {
            count += await runIndexing(dicionario.value[i])
            i++
            if (count >= 100) {
                message.value = 'Pausa de 60 segundos...'
                await sleep(60000) // Pausa de 60 segundos
                // se houver mais de 100 requests à api do reddit fazer uma pausa de 60sec
            }
        }
    }

    const startIndexing = async () => {
        indexingActive.value = true
        message.value = 'Indexação iniciada.'
        await loopIndexing()
        message.value = 'Indexação concluída.'
        indexingActive.value = false
    }

    const stopIndexing = () => {
        indexingActive.value = false
        message.value = 'Indexação parada.'
    }

    return {
        indexingActive,
        message,
        startIndexing,
        stopIndexing,
        dicionario,
        deleteIndex
    }
}