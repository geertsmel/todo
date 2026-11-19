<script setup>
import { computed, onMounted, ref } from 'vue'
import { api } from '../api.js'
import { buildSlices } from '../pie.js'

const stats = ref(null)
const error = ref('')

onMounted(async () => {
  try {
    stats.value = await api('/stats')
  } catch (e) {
    error.value = e.message
  }
})

const slices = computed(() => (stats.value ? buildSlices(stats.value) : []))
const summary = computed(() =>
  slices.value.map((s) => `${s.label} : ${s.value} (${s.percent} %)`).join(', '),
)
</script>

<template>
  <main class="card">
    <header>
      <h1>Statistiques</h1>
      <p v-if="stats" class="count">{{ stats.total }} tâche(s) au total</p>
    </header>

    <p v-if="error" class="error" role="alert">{{ error }}</p>
    <p v-else-if="!stats" class="empty">Chargement…</p>
    <p v-else-if="stats.total === 0" class="empty">Aucune tâche pour le moment : le camembert apparaîtra dès la première.</p>

    <div v-else class="stats">
      <svg class="pie" viewBox="0 0 200 200" role="img" :aria-label="`Répartition des tâches : ${summary}`">
        <template v-for="slice in slices" :key="slice.key">
          <circle v-if="slice.full" cx="100" cy="100" r="90" :fill="slice.color">
            <title>{{ slice.label }} : {{ slice.value }} ({{ slice.percent }} %)</title>
          </circle>
          <path v-else :d="slice.path" :fill="slice.color" stroke="#fff" stroke-width="2" stroke-linejoin="round">
            <title>{{ slice.label }} : {{ slice.value }} ({{ slice.percent }} %)</title>
          </path>
        </template>
      </svg>

      <ul class="legend">
        <li v-for="s in slices" :key="s.key">
          <span class="swatch" :style="{ background: s.color }" aria-hidden="true"></span>
          <span class="legend-label">{{ s.label }}</span>
          <span class="legend-value">{{ s.value }} · {{ s.percent }} %</span>
        </li>
      </ul>
    </div>
  </main>
</template>
