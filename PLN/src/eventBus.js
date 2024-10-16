import { ref } from 'vue'

export const eventBus = ref({
    emit(event, data) {
        this[event]?.(data)
    },
    on(event, callback) {
        this[event] = callback
    }
})
