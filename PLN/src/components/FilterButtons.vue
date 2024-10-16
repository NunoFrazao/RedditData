<!-- src/components/FilterButtons.vue -->
<template>
    <div>
        <!-- Filter buttons for larger screens -->
        <div class="row mb-4 filter-buttons d-none d-md-flex">
            <!-- Sentiment filter buttons -->
            <div class="col d-flex justify-content-md-end">
                <button :class="['btn mx-2', selectedSentiment === '' ? 'btn-secondary' : 'btn-outline-secondary']"
                    @click="filterSentiment('')">
                    Todos <span class="small font-weight-bold">({{ searchData.length }})</span>
                </button>
                <button :class="['btn mx-2', selectedSentiment === 'Positivo' ? 'btn-success' : 'btn-outline-success']"
                    @click="filterSentiment('Positivo')">
                    Positivos <span class="small font-weight-bold">({{ countSentiments('Positivo') }})</span>
                </button>
                <button :class="['btn mx-2', selectedSentiment === 'Neutro' ? 'btn-warning' : 'btn-outline-warning']"
                    @click="filterSentiment('Neutro')">
                    Neutros <span class="small font-weight-bold">({{ countSentiments('Neutro') }})</span>
                </button>
                <button :class="['btn mx-2', selectedSentiment === 'Negativo' ? 'btn-danger' : 'btn-outline-danger']"
                    @click="filterSentiment('Negativo')">
                    Negativos <span class="small font-weight-bold">({{ countSentiments('Negativo') }})</span>
                </button>
            </div>
        </div>

        <!-- Filter dropdown for smaller screens -->
        <div class="row mb-4 filter-buttons d-flex d-md-none">
            <div class="col d-flex justify-content-md-start pb-4">
                <button class="btn btn-outline-secondary dropdown-toggle" type="button" id="dropdownFilterButton"
                    data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                    Filtrar por Sentimento
                </button>
                <div class="dropdown-menu" aria-labelledby="dropdownFilterButton">
                    <a class="dropdown-item" href="#" @click.prevent="filterSentiment('')">Todos <span
                            class="small font-weight-bold">({{ searchData.length }})</span></a>
                    <a class="dropdown-item" href="#" @click.prevent="filterSentiment('Positivo')">Positivos <span
                            class="small font-weight-bold">({{ countSentiments('Positivo') }})</span></a>
                    <a class="dropdown-item" href="#" @click.prevent="filterSentiment('Neutro')">Neutros <span
                            class="small font-weight-bold">({{ countSentiments('Neutro') }})</span></a>
                    <a class="dropdown-item" href="#" @click.prevent="filterSentiment('Negativo')">Negativos <span
                            class="small font-weight-bold">({{ countSentiments('Negativo') }})</span></a>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>

//#region Imports
import { useUserStore } from '@/stores/user'
//#endregion

const props = defineProps({
    searchData: Array,
    selectedSentiment: String,
})

//#region Variables
const emit = defineEmits(['update:selectedSentiment'])
//#endregion

//#region Methods
const filterSentiment = (sentiment) => {
    emit('update:selectedSentiment', sentiment)
}

const countSentiments = (sentiment) => {
    return props.searchData.filter(item => getSentiment(item.scores) === sentiment).length
}

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
//#endregion

</script>