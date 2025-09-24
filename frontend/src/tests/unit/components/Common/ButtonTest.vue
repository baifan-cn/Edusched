<template>
  <div class="button-test">
    <el-button
      :type="type"
      :size="size"
      :disabled="disabled"
      :loading="loading"
      @click="handleClick"
    >
      <slot>{{ text }}</slot>
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue'

interface Props {
  type?: 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'text'
  size?: 'large' | 'default' | 'small'
  disabled?: boolean
  loading?: boolean
  text?: string
}

const props = withDefaults(defineProps<Props>(), {
  type: 'primary',
  size: 'default',
  disabled: false,
  loading: false,
  text: 'Button'
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const handleClick = (event: MouseEvent) => {
  emit('click', event)
}
</script>

<style scoped>
.button-test {
  display: inline-block;
}
</style>