import axios from 'axios'

/**
 * Função para buscar dados do Reddit
 * @param {string} query - Termo de busca
 * @param {number} pages - Número de páginas a buscar
 * @param {string} sort - Ordenação dos resultados
 * @param {number} limit - Limite de resultados por página
 * @returns {Promise<Object>} - Objeto com títulos, textos, IDs, thumbnails e permalinks
 */
export async function searchReddit(query, pages = 10, sort = 'relevance', limit = 100) {
    if (!query) {
        throw new Error("The 'query' is empty")
    }
    if (pages < 1) {
        throw new Error(`Invalid value '${pages}' for 'pages'`)
    }

    let listOfResponses = []
    let titles = []
    let selftexts = []
    let ids = []
    let thumbnails = []
    let permalinks = []
    let after = null
    let countRequests = 0

    for (let i = 0; i < pages; i++) {
        const { statusCode, responseJson, newAfter } = await globalSearch(query, after, sort, limit)
        countRequests++
        if (statusCode !== 200) {
            throw new Error("Reddit request exception")
        }
        listOfResponses.push(responseJson)
        after = newAfter
        if (!after) {
            break
        }
    }

    if (listOfResponses.length === 0) {
        throw new Error("Reddit response is empty")
    }

    listOfResponses.forEach(response => {
        response.data.children.forEach(reddit => {
            titles.push(reddit.data.title)
            selftexts.push(reddit.data.selftext)
            ids.push(reddit.data.id)
            thumbnails.push(reddit.data.thumbnail)
            permalinks.push(reddit.data.permalink)
        })
    })

    // console.log("Number of ids:", ids.length)

    return {
        titles,
        selftexts,
        ids,
        thumbnails,
        permalinks,
        countRequests
    }
}

/**
 * Função para realizar a busca global no Reddit
 * @param {string} baseUrl - URL base do Reddit
 * @param {string} query - Termo de busca
 * @param {string|null} after - Cursor de paginação
 * @param {string} sort - Ordenação dos resultados
 * @param {number} limit - Limite de resultados por página
 * @param {Object} headers - Cabeçalhos HTTP
 * @returns {Promise<Object>} - StatusCode, resposta JSON e novo cursor 'after'
 */
async function globalSearch(query, after, sort, limit) {
    const baseUrl = 'https://www.reddit.com'
    const headers = {
        //'User-Agent': 'Your bot 0.1'
    };
    const url = `${baseUrl}/search.json`;
    const params = {
        q: query,
        sort,
        limit,
        after
    };

    try {
        const response = await axios.get(url, { params, headers });
        const responseJson = response.data;
        const newAfter = responseJson.data.after;
        return {
            statusCode: response.status,
            responseJson,
            newAfter
        };
    } catch (error) {
        console.error("Error in global search:", error.message);
        return {
            statusCode: error.response ? error.response.status : 500,
            responseJson: null,
            newAfter: null
        };
    }
}