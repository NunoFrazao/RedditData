<template>
    <div class="modal-overlay" v-if="show">
        <div class="modal-content">
            <!-- Title -->
            <h2 class="modal-title">{{ title }}</h2>

            <!-- Message -->
            <div class="modal-body text-muted mb-0">
                <slot></slot>
            </div>

            <!-- Buttons -->
            <div class="modal-footer">
                <button class="btn" :class="confirmButtonClass" @click="confirm">Confirmar</button>
                <button class="btn btn-secondary" @click="close">Cancelar</button>
            </div>
        </div>
    </div>
</template>

<script setup>

//#region Imports
import '@/assets/css/modal.css'
//#endregion

const props = defineProps({
    title: String,
    show: Boolean,
    confirmButtonClass: {
        type: String,
        default: 'btn-primary'
    }
})

//#region Variables
const emit = defineEmits(['confirm', 'close'])
//#endregion

//#region Methods
const confirm = () => { emit('confirm') }

const close = () => { emit('close') }
//#endregion

</script>